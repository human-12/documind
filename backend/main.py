from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
import uvicorn

from database import get_db, init_db, Document, DocumentChunk, ChatHistory
from document_processor import DocumentProcessor
from rag_pipeline import RAGPipeline

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind API",
    description="Enterprise RAG platform for intelligent document search",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
UPLOAD_DIR = Path("/tmp/documind_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

document_processor = DocumentProcessor()
rag_pipeline = RAGPipeline(OPENAI_API_KEY, REDIS_URL)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    response_time: float
    cached: bool

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    upload_date: str
    file_size: int
    page_count: Optional[int]
    processed: bool

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    avg_response_time: float

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized successfully")

# Health check
@app.get("/")
async def root():
    return {
        "message": "DocuMind API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

# Upload document endpoint
@app.post("/api/documents/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        # Validate file type
        file_type = document_processor.get_file_type(file.filename)
        if file_type == "unknown":
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Create document record
        doc = Document(
            filename=file.filename,
            file_type=file_type,
            content="",  # Will be populated during processing
            file_size=file_size,
            processed=False
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Process document in background
        background_tasks.add_task(
            process_document_background,
            doc.id,
            str(file_path),
            file_type
        )
        
        return DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            upload_date=doc.upload_date.isoformat(),
            file_size=doc.file_size,
            page_count=doc.page_count,
            processed=doc.processed
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_document_background(doc_id: int, file_path: str, file_type: str):
    """Background task to process document"""
    db = next(get_db())
    try:
        # Extract text
        text, metadata = document_processor.extract_text(file_path, file_type)
        
        # Chunk text
        chunks = document_processor.chunk_text(text, metadata)
        
        # Create embeddings
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = rag_pipeline.create_embeddings_batch(chunk_texts)
        
        # Save chunks with embeddings
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_record = DocumentChunk(
                document_id=doc_id,
                chunk_index=i,
                content=chunk["content"],
                embedding=embedding,
                metadata=str(chunk["metadata"])
            )
            db.add(chunk_record)
        
        # Update document
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.content = text[:1000]  # Store preview
        doc.page_count = metadata.get("page_count") or metadata.get("paragraph_count")
        doc.processed = True
        
        db.commit()
        
        # Clean up file
        os.remove(file_path)
        
    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.processed = False
            db.commit()
    finally:
        db.close()

# Query endpoint
@app.post("/api/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query documents using RAG"""
    try:
        result = rag_pipeline.generate_answer(
            db=db,
            query=request.query,
            session_id=request.session_id
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List documents endpoint
@app.get("/api/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all documents"""
    documents = db.query(Document).offset(skip).limit(limit).all()
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            upload_date=doc.upload_date.isoformat(),
            file_size=doc.file_size,
            page_count=doc.page_count,
            processed=doc.processed
        )
        for doc in documents
    ]

# Get document by ID
@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        upload_date=doc.upload_date.isoformat(),
        file_size=doc.file_size,
        page_count=doc.page_count,
        processed=doc.processed
    )

# Delete document endpoint
@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its chunks"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete chunks
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    
    # Delete document
    db.delete(doc)
    db.commit()
    
    # Clear cache
    rag_pipeline.clear_cache()
    
    return {"message": "Document deleted successfully"}

# Chat history endpoint
@app.get("/api/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    history = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": entry.id,
            "query": entry.query,
            "response": entry.response,
            "timestamp": entry.timestamp.isoformat(),
            "response_time": entry.response_time
        }
        for entry in history
    ]

# Stats endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    total_documents = db.query(Document).count()
    total_chunks = db.query(DocumentChunk).count()
    total_queries = db.query(ChatHistory).count()
    
    avg_response_time = db.query(ChatHistory).with_entities(
        db.func.avg(ChatHistory.response_time)
    ).scalar() or 0.0
    
    return StatsResponse(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_queries=total_queries,
        avg_response_time=float(avg_response_time)
    )

# Clear cache endpoint
@app.post("/api/cache/clear")
async def clear_cache():
    """Clear the query cache"""
    rag_pipeline.clear_cache()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
