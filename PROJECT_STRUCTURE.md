# DocuMind Project Structure

```
documind/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Main FastAPI application
│   ├── database.py                   # Database models and setup
│   ├── document_processor.py         # Document text extraction
│   ├── rag_pipeline.py               # RAG implementation
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Backend container config
│
├── frontend/                         # React Frontend
│   ├── public/
│   │   └── index.html               # HTML template
│   ├── src/
│   │   ├── App.jsx                  # Main React component
│   │   ├── App.css                  # Styling
│   │   └── index.js                 # Entry point
│   ├── package.json                 # Node dependencies
│   ├── Dockerfile                   # Frontend container config
│   └── nginx.conf                   # Nginx configuration
│
├── database/                         # Database Scripts
│   └── init.sql                     # Database initialization
│
├── docker-compose.yml               # Container orchestration
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
│
├── start.sh                         # Startup script
├── test_api.py                      # API testing script
│
├── README.md                        # Main documentation
├── API_DOCUMENTATION.md             # API reference
├── CONTRIBUTING.md                  # Contribution guide
├── CHANGELOG.md                     # Version history
├── LICENSE                          # MIT License
└── PROJECT_STRUCTURE.md             # This file
```

## Component Overview

### Backend Components

#### main.py
- FastAPI application setup
- API endpoints definition
- CORS configuration
- Background task handling
- Request/response models

#### database.py
- SQLAlchemy models
- Database connection setup
- Session management
- pgvector integration
- Database initialization

#### document_processor.py
- File type detection
- Text extraction from various formats
- Document chunking strategy
- Metadata extraction
- File validation

#### rag_pipeline.py
- OpenAI embeddings integration
- Vector similarity search
- Context retrieval
- Answer generation
- Cache management
- LangChain integration

### Frontend Components

#### App.jsx
- Main application component
- Tab navigation (Chat, Documents, Upload)
- Document upload handling
- Query submission
- Chat message display
- Document management UI
- Statistics dashboard

#### App.css
- Custom design system
- Responsive layouts
- Animations and transitions
- Dark theme
- Component styling
- Mobile optimization

### Database Schema

#### documents
- id (Primary Key)
- filename
- file_type
- content
- upload_date
- file_size
- page_count
- processed

#### document_chunks
- id (Primary Key)
- document_id (Foreign Key)
- chunk_index
- content
- embedding (vector)
- metadata

#### chat_history
- id (Primary Key)
- session_id
- query
- response
- sources
- timestamp
- response_time

### Docker Services

#### postgres
- PostgreSQL 16 with pgvector
- Persistent volume for data
- Health checks

#### redis
- Redis 7 for caching
- Append-only persistence
- Health checks

#### backend
- Python FastAPI server
- Port 8000
- Depends on postgres and redis

#### frontend
- Nginx serving React build
- Port 80
- Proxies API requests to backend

## Data Flow

### Document Upload Flow
```
User → Frontend → Backend → 
  ├── Save File
  ├── Create DB Record
  └── Background Task →
      ├── Extract Text
      ├── Chunk Text
      ├── Generate Embeddings
      ├── Store in Database
      └── Update Status
```

### Query Flow
```
User → Frontend → Backend →
  ├── Check Cache (Redis)
  ├── Generate Query Embedding
  ├── Vector Search (pgvector)
  ├── Retrieve Context
  ├── Generate Answer (OpenAI)
  ├── Save to History
  ├── Update Cache
  └── Return Response
```

## Key Technologies

### Backend
- **FastAPI**: Web framework
- **LangChain**: RAG orchestration
- **OpenAI**: Embeddings & generation
- **PostgreSQL**: Document storage
- **pgvector**: Vector search
- **Redis**: Query caching
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation

### Frontend
- **React**: UI framework
- **Axios**: HTTP client
- **React Dropzone**: File uploads
- **React Markdown**: Response formatting
- **Lucide React**: Icons
- **date-fns**: Date formatting

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Orchestration
- **Nginx**: Web server & reverse proxy
- **PostgreSQL**: Database
- **Redis**: Cache

## Configuration

### Environment Variables

#### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key

#### Frontend
- `REACT_APP_API_URL`: Backend API URL

### Docker Volumes
- `postgres_data`: Database persistence
- `redis_data`: Cache persistence
- `upload_data`: Temporary file storage

### Ports
- 80: Frontend (Nginx)
- 8000: Backend API
- 5432: PostgreSQL
- 6379: Redis

## Development vs Production

### Development
- Hot reload enabled
- Debug logging
- Local file storage
- No authentication
- CORS permissive

### Production Recommendations
- Use environment-specific configs
- Enable authentication
- Use cloud storage (S3, GCS)
- Implement rate limiting
- Add monitoring and logging
- Use managed databases
- Enable HTTPS
- Restrict CORS
- Add CDN for frontend

## Scalability Considerations

### Horizontal Scaling
- Stateless backend (multiple instances)
- Shared database and cache
- Load balancer in front
- Container orchestration (Kubernetes)

### Vertical Scaling
- Increase container resources
- Database connection pooling
- Optimize vector indexes
- Cache warming strategies

### Performance Optimization
- Database query optimization
- Vector index tuning
- Redis cache strategies
- CDN for static assets
- Lazy loading
- Pagination
- Background job queues

## Security Layers

1. **Input Validation**: Pydantic models
2. **File Validation**: Type and size checks
3. **SQL Injection**: Parameterized queries
4. **CORS**: Configured origins
5. **Secrets**: Environment variables
6. **Rate Limiting**: (To be implemented)
7. **Authentication**: (To be implemented)

## Monitoring Points

- API response times
- Database query performance
- Cache hit rates
- Vector search latency
- Document processing time
- Error rates
- System resources
- Queue depths

## Backup Strategy

### Database
- Regular PostgreSQL backups
- Point-in-time recovery
- Backup rotation

### Documents
- Original file retention
- Version control
- Disaster recovery plan

## Future Enhancements

1. **Authentication System**
2. **Multi-tenancy**
3. **Advanced Analytics**
4. **Webhook Support**
5. **Integration APIs**
6. **Mobile Apps**
7. **Voice Interface**
8. **Custom Models**
9. **A/B Testing**
10. **Audit Logs**

---

This structure provides a solid foundation for an enterprise-grade RAG platform with room for growth and customization.
