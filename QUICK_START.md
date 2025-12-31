# DocuMind - 5-Minute Quick Start

Get DocuMind running in 5 minutes!

## Step 1: Prerequisites Check ✓

```bash
# Check Docker
docker --version
# Should show: Docker version 20.x or higher

# Check Docker Compose
docker-compose --version
# Should show: Docker Compose version 2.x or higher
```

Don't have Docker? Install from: https://docs.docker.com/get-docker/

## Step 2: Get Your OpenAI API Key 🔑

1. Go to: https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it (starts with `sk-...`)

## Step 3: Configure Environment ⚙️

```bash
# Navigate to the project
cd documind

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your favorite editor

# Add your OpenAI API key:
OPENAI_API_KEY=sk-your-actual-key-here
# Save and exit
```

## Step 4: Start DocuMind 🚀

```bash
# Make startup script executable (Linux/Mac)
chmod +x start.sh

# Run the startup script
./start.sh

# OR manually with Docker Compose:
docker-compose up -d
```

Wait ~30 seconds for everything to start...

## Step 5: Access the Application 🎉

Open your browser:
- **Main App**: http://localhost
- **API Docs**: http://localhost:8000/docs

## First Steps After Installation

### 1. Upload a Document
- Click the **Upload** tab
- Drag and drop a PDF, Word doc, or text file
- Wait for processing (shows green checkmark when done)

### 2. Ask a Question
- Go to the **Chat** tab
- Type: "What is this document about?"
- Press Enter or click Send
- Get your answer with sources!

### 3. View Documents
- Click the **Documents** tab
- See all uploaded files
- Check processing status
- Delete documents if needed

## Troubleshooting

### Problem: "Cannot connect to Docker daemon"
**Solution**: Start Docker Desktop

### Problem: "Port 80 already in use"
**Solution**: Stop other web servers or edit docker-compose.yml to use a different port

### Problem: "OpenAI API error"
**Solution**: Check your API key in .env file

### Problem: "Services not starting"
**Solution**: 
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Full reset
docker-compose down
docker-compose up -d
```

## Useful Commands

```bash
# View all running containers
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose stop

# Start again
docker-compose start

# Complete shutdown (keeps data)
docker-compose down

# Complete reset (deletes ALL data)
docker-compose down -v
```

## Test the API

```bash
# Run automated tests
python test_api.py

# Check health
curl http://localhost:8000/

# Get stats
curl http://localhost:8000/api/stats
```

## What's Running?

After starting, you have:
- ✅ PostgreSQL database (with pgvector)
- ✅ Redis cache
- ✅ FastAPI backend
- ✅ React frontend
- ✅ Complete RAG pipeline

## Production Deployment

For production, also:
1. Change `POSTGRES_PASSWORD` in .env
2. Set up HTTPS/SSL
3. Add authentication
4. Use managed database (AWS RDS, etc.)
5. Set up monitoring
6. Configure backups

See README.md for full production guide.

## Getting Help

- 📖 Full docs: See README.md
- 🔧 API reference: See API_DOCUMENTATION.md
- 💻 Architecture: See PROJECT_STRUCTURE.md
- 🐛 Issues: Open on GitHub
- 📧 Email: support@documind.example.com

## Next Steps

1. **Upload your documents** - Add your knowledge base
2. **Test queries** - Ask various questions
3. **Check sources** - Verify answer accuracy
4. **Customize** - Adapt to your needs
5. **Deploy** - Move to production

---

**That's it! You're now running DocuMind! 🎉**

Start uploading documents and asking questions!
