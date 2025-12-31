#!/usr/bin/env python3
"""
DocuMind API Test Script
Tests the main functionality of the DocuMind API
"""

import requests
import time
import sys
from pathlib import Path

API_BASE = "http://localhost:8000"

def print_status(message, status="info"):
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")

def test_health_check():
    """Test if the API is responding"""
    print_status("Testing health check...", "info")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print_status("API is healthy", "success")
            return True
        else:
            print_status(f"API returned status {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Cannot connect to API: {e}", "error")
        return False

def test_stats():
    """Test stats endpoint"""
    print_status("Testing stats endpoint...", "info")
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print_status(f"Stats retrieved successfully", "success")
            print(f"   Documents: {stats['total_documents']}")
            print(f"   Chunks: {stats['total_chunks']}")
            print(f"   Queries: {stats['total_queries']}")
            return True
        else:
            print_status(f"Stats endpoint failed: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Stats test failed: {e}", "error")
        return False

def test_document_upload():
    """Test document upload"""
    print_status("Testing document upload...", "info")
    
    # Create a test file
    test_content = """
# Test Document for DocuMind

This is a test document to verify the upload functionality.

## Section 1: Introduction
DocuMind is an enterprise RAG platform that helps organizations
manage and query their internal documentation.

## Section 2: Features
- Document processing
- Vector search
- AI-powered answers
- Source attribution

## Section 3: Technology
Built with FastAPI, LangChain, and OpenAI.
"""
    
    test_file_path = Path("/tmp/test_document.txt")
    test_file_path.write_text(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(f"{API_BASE}/api/documents/upload", files=files)
        
        if response.status_code == 200:
            doc = response.json()
            print_status(f"Document uploaded successfully (ID: {doc['id']})", "success")
            
            # Wait for processing
            print_status("Waiting for document processing...", "info")
            time.sleep(5)
            
            # Check if processed
            response = requests.get(f"{API_BASE}/api/documents/{doc['id']}")
            if response.status_code == 200:
                doc_status = response.json()
                if doc_status['processed']:
                    print_status("Document processed successfully", "success")
                    return doc['id']
                else:
                    print_status("Document still processing...", "warning")
                    return doc['id']
        else:
            print_status(f"Upload failed: {response.status_code}", "error")
            return None
    except Exception as e:
        print_status(f"Upload test failed: {e}", "error")
        return None
    finally:
        test_file_path.unlink(missing_ok=True)

def test_query(doc_id):
    """Test query endpoint"""
    print_status("Testing query endpoint...", "info")
    
    test_query = "What is DocuMind?"
    
    try:
        response = requests.post(
            f"{API_BASE}/api/query",
            json={"query": test_query, "session_id": "test-session"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_status("Query executed successfully", "success")
            print(f"   Query: {test_query}")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Sources: {len(result['sources'])} documents")
            print(f"   Response time: {result['response_time']:.2f}s")
            return True
        else:
            print_status(f"Query failed: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Query test failed: {e}", "error")
        return False

def test_document_list():
    """Test document listing"""
    print_status("Testing document list...", "info")
    try:
        response = requests.get(f"{API_BASE}/api/documents")
        if response.status_code == 200:
            docs = response.json()
            print_status(f"Retrieved {len(docs)} documents", "success")
            return True
        else:
            print_status(f"List failed: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"List test failed: {e}", "error")
        return False

def cleanup_test_data(doc_id):
    """Clean up test document"""
    if doc_id:
        print_status("Cleaning up test data...", "info")
        try:
            response = requests.delete(f"{API_BASE}/api/documents/{doc_id}")
            if response.status_code == 200:
                print_status("Test data cleaned up", "success")
            else:
                print_status("Cleanup failed (non-critical)", "warning")
        except Exception as e:
            print_status(f"Cleanup failed: {e}", "warning")

def main():
    print("\n" + "="*50)
    print("   DocuMind API Test Suite")
    print("="*50 + "\n")
    
    results = []
    doc_id = None
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    
    if not results[-1][1]:
        print_status("\nAPI is not responding. Please ensure DocuMind is running.", "error")
        sys.exit(1)
    
    results.append(("Stats Endpoint", test_stats()))
    results.append(("Document List", test_document_list()))
    
    # Upload and query test
    doc_id = test_document_upload()
    if doc_id:
        results.append(("Document Upload", True))
        
        # Wait a bit more for processing
        time.sleep(3)
        
        results.append(("Query Execution", test_query(doc_id)))
    else:
        results.append(("Document Upload", False))
        results.append(("Query Execution", False))
    
    # Print summary
    print("\n" + "="*50)
    print("   Test Summary")
    print("="*50 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "success" if result else "error"
        print_status(f"{test_name}: {'PASSED' if result else 'FAILED'}", status)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    # Cleanup
    if doc_id:
        cleanup_test_data(doc_id)
    
    print("\n" + "="*50 + "\n")
    
    if passed == total:
        print_status("All tests passed! DocuMind is working correctly. 🎉", "success")
        sys.exit(0)
    else:
        print_status(f"{total - passed} test(s) failed. Please check the logs.", "error")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
