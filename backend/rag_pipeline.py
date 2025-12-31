from typing import List, Dict, Tuple
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy.orm import Session
from database import DocumentChunk, ChatHistory
import json
import time
import redis
import hashlib

class RAGPipeline:
    """RAG pipeline for document retrieval and generation"""
    
    def __init__(self, openai_api_key: str, redis_url: str = "redis://localhost:6379"):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-3-small"
        )
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.cache_enabled = True
        except:
            print("Warning: Redis not available, caching disabled")
            self.cache_enabled = False
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are DocuMind, an intelligent assistant that helps users find information from their organization's documentation.

Use the following pieces of context from internal documents to answer the question. If you don't know the answer based on the context, say so - don't make up information.

Context:
{context}

Question: {question}

Provide a clear, comprehensive answer based on the context above. Include relevant details and cite which documents the information came from when applicable.

Answer:"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        return self.embeddings.embed_query(text)
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        return self.embeddings.embed_documents(texts)
    
    def vector_search(
        self, 
        db: Session, 
        query_embedding: List[float], 
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Perform vector similarity search using pgvector
        Returns list of (chunk, similarity_score) tuples
        """
        # Convert embedding to string format for pgvector
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Use pgvector's cosine distance operator (<=>)
        query = f"""
            SELECT 
                id, document_id, chunk_index, content, metadata,
                1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM document_chunks
            WHERE 1 - (embedding <=> '{embedding_str}'::vector) > {similarity_threshold}
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT {top_k}
        """
        
        results = db.execute(query).fetchall()
        
        chunks_with_scores = []
        for row in results:
            chunk = DocumentChunk(
                id=row[0],
                document_id=row[1],
                chunk_index=row[2],
                content=row[3],
                metadata=row[4]
            )
            chunks_with_scores.append((chunk, row[5]))
        
        return chunks_with_scores
    
    def retrieve_context(
        self, 
        db: Session, 
        query: str, 
        top_k: int = 5
    ) -> Tuple[str, List[Dict]]:
        """
        Retrieve relevant context for a query
        Returns (context_string, source_documents)
        """
        # Create query embedding
        query_embedding = self.create_embedding(query)
        
        # Perform vector search
        results = self.vector_search(db, query_embedding, top_k)
        
        # Build context string and source list
        context_parts = []
        sources = []
        
        for i, (chunk, score) in enumerate(results, 1):
            context_parts.append(
                f"[Document {chunk.document_id}, Section {chunk.chunk_index}]\n{chunk.content}\n"
            )
            sources.append({
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "similarity_score": float(score),
                "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            })
        
        context = "\n\n".join(context_parts)
        return context, sources
    
    def generate_answer(
        self, 
        db: Session, 
        query: str, 
        session_id: str = "default",
        use_cache: bool = True
    ) -> Dict:
        """
        Generate an answer to a query using RAG
        Returns dict with answer, sources, and metadata
        """
        start_time = time.time()
        
        # Check cache
        if use_cache and self.cache_enabled:
            cache_key = self._get_cache_key(query)
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                result = json.loads(cached_result)
                result["cached"] = True
                result["response_time"] = time.time() - start_time
                return result
        
        # Retrieve relevant context
        context, sources = self.retrieve_context(db, query)
        
        if not context:
            return {
                "answer": "I couldn't find any relevant information in the knowledge base to answer your question. Please try rephrasing or check if the relevant documents have been uploaded.",
                "sources": [],
                "response_time": time.time() - start_time,
                "cached": False
            }
        
        # Generate answer
        answer = self.chain.run(context=context, question=query)
        
        response_time = time.time() - start_time
        
        result = {
            "answer": answer.strip(),
            "sources": sources,
            "response_time": response_time,
            "cached": False
        }
        
        # Save to chat history
        chat_entry = ChatHistory(
            session_id=session_id,
            query=query,
            response=answer.strip(),
            sources=json.dumps(sources),
            response_time=response_time
        )
        db.add(chat_entry)
        db.commit()
        
        # Cache result
        if self.cache_enabled:
            cache_key = self._get_cache_key(query)
            self.redis_client.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(result)
            )
        
        return result
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        return f"rag:query:{query_hash}"
    
    def clear_cache(self):
        """Clear all cached queries"""
        if self.cache_enabled:
            keys = self.redis_client.keys("rag:query:*")
            if keys:
                self.redis_client.delete(*keys)
