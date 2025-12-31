#!/bin/bash

# DocuMind Startup Script
# This script helps you get DocuMind up and running quickly

set -e

echo "======================================"
echo "   DocuMind - Enterprise RAG Platform"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key!"
    echo "   Then run this script again."
    echo ""
    read -p "Do you want to edit .env now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    else
        echo "Please edit .env manually and add your OPENAI_API_KEY"
        exit 1
    fi
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if OPENAI_API_KEY is set in .env
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "❌ OPENAI_API_KEY not properly set in .env file"
    echo "   Please edit .env and add your OpenAI API key"
    exit 1
fi

echo "🔍 Checking Docker daemon..."
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if containers are already running
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  DocuMind containers are already running"
    read -p "Do you want to restart them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Restarting containers..."
        docker-compose restart
    else
        echo "ℹ️  Containers left running"
    fi
else
    echo "🚀 Starting DocuMind..."
    echo ""
    
    # Pull latest images
    echo "📥 Pulling Docker images..."
    docker-compose pull
    
    # Start services
    echo "🏗️  Building and starting services..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check if services are healthy
    echo "🔍 Checking service health..."
    
    if docker-compose ps | grep -q "postgres.*Up"; then
        echo "✅ PostgreSQL is running"
    else
        echo "❌ PostgreSQL failed to start"
        docker-compose logs postgres
        exit 1
    fi
    
    if docker-compose ps | grep -q "redis.*Up"; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis failed to start"
        docker-compose logs redis
        exit 1
    fi
    
    if docker-compose ps | grep -q "backend.*Up"; then
        echo "✅ Backend is running"
    else
        echo "❌ Backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    
    if docker-compose ps | grep -q "frontend.*Up"; then
        echo "✅ Frontend is running"
    else
        echo "❌ Frontend failed to start"
        docker-compose logs frontend
        exit 1
    fi
fi

echo ""
echo "======================================"
echo "   🎉 DocuMind is ready!"
echo "======================================"
echo ""
echo "📱 Frontend:  http://localhost"
echo "🔧 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f        # View logs"
echo "  docker-compose ps             # Check status"
echo "  docker-compose stop           # Stop services"
echo "  docker-compose down           # Stop and remove"
echo "  docker-compose down -v        # Stop and remove all data"
echo ""
echo "Happy querying! 🚀"
