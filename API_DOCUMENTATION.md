# DocuMind API Documentation

## Base URL

```
http://localhost:8000
```

For production, replace with your domain.

## Authentication

Currently, the API doesn't require authentication. For production deployment, implement authentication using JWT tokens or API keys.

## Endpoints

### Health Check

#### GET /

Check if the API is running.

**Response:**
```json
{
  "message": "DocuMind API is running",
  "version": "1.0.0",
  "status": "healthy"
}
```

---

### Documents

#### POST /api/documents/upload

Upload a new document for processing.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field

**Supported File Types:**
- PDF (.pdf)
- Word Documents (.docx)
- Excel Spreadsheets (.xlsx)
- Text Files (.txt)

**Response:**
```json
{
  "id": 1,
  "filename": "company_policy.pdf",
  "file_type": "pdf",
  "upload_date": "2024-12-30T10:30:00",
  "file_size": 1048576,
  "page_count": 25,
  "processed": false
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file type or bad request
- 500: Server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

---

#### GET /api/documents

List all uploaded documents.

**Query Parameters:**
- `skip` (optional): Number of documents to skip (default: 0)
- `limit` (optional): Maximum number of documents to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "filename": "company_policy.pdf",
    "file_type": "pdf",
    "upload_date": "2024-12-30T10:30:00",
    "file_size": 1048576,
    "page_count": 25,
    "processed": true
  },
  {
    "id": 2,
    "filename": "technical_specs.docx",
    "file_type": "docx",
    "upload_date": "2024-12-30T11:00:00",
    "file_size": 524288,
    "page_count": 15,
    "processed": true
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/documents?limit=10"
```

---

#### GET /api/documents/{document_id}

Get details of a specific document.

**Path Parameters:**
- `document_id`: ID of the document

**Response:**
```json
{
  "id": 1,
  "filename": "company_policy.pdf",
  "file_type": "pdf",
  "upload_date": "2024-12-30T10:30:00",
  "file_size": 1048576,
  "page_count": 25,
  "processed": true
}
```

**Status Codes:**
- 200: Success
- 404: Document not found

**Example:**
```bash
curl "http://localhost:8000/api/documents/1"
```

---

#### DELETE /api/documents/{document_id}

Delete a document and all its associated chunks.

**Path Parameters:**
- `document_id`: ID of the document

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

**Status Codes:**
- 200: Success
- 404: Document not found

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/documents/1"
```

---

### Queries

#### POST /api/query

Query the knowledge base using natural language.

**Request Body:**
```json
{
  "query": "What are the company's vacation policies?",
  "session_id": "user-session-123",
  "top_k": 5
}
```

**Parameters:**
- `query` (required): The question or search query
- `session_id` (optional): Session identifier for tracking chat history (default: "default")
- `top_k` (optional): Number of relevant chunks to retrieve (default: 5)

**Response:**
```json
{
  "answer": "According to the company policy, employees are entitled to 15 days of vacation per year. Vacation days must be requested at least two weeks in advance...",
  "sources": [
    {
      "document_id": 1,
      "chunk_index": 3,
      "similarity_score": 0.89,
      "content_preview": "Vacation Policy: All full-time employees are entitled to 15 days of paid vacation annually..."
    },
    {
      "document_id": 1,
      "chunk_index": 4,
      "similarity_score": 0.85,
      "content_preview": "Requesting Time Off: Vacation requests must be submitted through the HR portal at least two weeks..."
    }
  ],
  "response_time": 1.25,
  "cached": false
}
```

**Status Codes:**
- 200: Success
- 500: Server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the company vacation policies?",
    "session_id": "my-session"
  }'
```

---

### Chat History

#### GET /api/history/{session_id}

Retrieve chat history for a specific session.

**Path Parameters:**
- `session_id`: Session identifier

**Query Parameters:**
- `limit` (optional): Maximum number of messages to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "query": "What are the company vacation policies?",
    "response": "According to the company policy...",
    "timestamp": "2024-12-30T10:35:00",
    "response_time": 1.25
  },
  {
    "id": 2,
    "query": "How do I request time off?",
    "response": "To request time off, you need to...",
    "timestamp": "2024-12-30T10:36:00",
    "response_time": 0.95
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/history/user-session-123?limit=20"
```

---

### Statistics

#### GET /api/stats

Get platform usage statistics.

**Response:**
```json
{
  "total_documents": 42,
  "total_chunks": 1250,
  "total_queries": 387,
  "avg_response_time": 1.35
}
```

**Example:**
```bash
curl "http://localhost:8000/api/stats"
```

---

### Cache Management

#### POST /api/cache/clear

Clear the query cache.

**Response:**
```json
{
  "message": "Cache cleared successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/cache/clear"
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

---

## Rate Limiting

Currently, there are no rate limits. For production, implement rate limiting based on your requirements.

---

## Interactive Documentation

FastAPI provides interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test endpoints directly from your browser.

---

## Best Practices

1. **Document Processing**: Wait for `processed: true` before querying documents
2. **Session Management**: Use consistent session IDs to maintain chat context
3. **Query Optimization**: Use specific questions for better results
4. **Batch Operations**: Upload multiple documents in parallel for efficiency
5. **Cache Management**: Clear cache when making significant document changes
6. **Error Handling**: Implement proper error handling in client applications

---

## SDK Examples

### Python

```python
import requests

API_BASE = "http://localhost:8000"

# Upload document
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_BASE}/api/documents/upload", files=files)
    document = response.json()

# Query
query_data = {
    "query": "What is the main topic of the document?",
    "session_id": "my-session"
}
response = requests.post(f"{API_BASE}/api/query", json=query_data)
result = response.json()
print(result["answer"])
```

### JavaScript

```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/documents/upload', {
  method: 'POST',
  body: formData
});
const document = await uploadResponse.json();

// Query
const queryResponse = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is the main topic?',
    session_id: 'my-session'
  })
});
const result = await queryResponse.json();
console.log(result.answer);
```

### cURL

```bash
# Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"

# Query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?", "session_id": "test"}'
```

---

## WebSocket Support (Future)

Real-time streaming responses will be available in a future version.

---

## Support

For API support, please:
- Check the documentation
- Review the troubleshooting guide
- Open an issue on GitHub
- Contact support@documind.example.com
