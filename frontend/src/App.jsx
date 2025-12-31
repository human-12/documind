import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import { 
  Upload, Search, FileText, Clock, TrendingUp, 
  Trash2, Loader, Send, MessageSquare, Database,
  Zap, CheckCircle, XCircle, Sparkles
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const onDrop = async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      const formData = new FormData();
      formData.append('file', file);

      setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

      try {
        await axios.post(`${API_BASE}/api/documents/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          }
        });

        setUploadProgress(prev => {
          const newProgress = { ...prev };
          delete newProgress[file.name];
          return newProgress;
        });

        fetchDocuments();
        fetchStats();
      } catch (error) {
        console.error('Error uploading file:', error);
        setUploadProgress(prev => {
          const newProgress = { ...prev };
          delete newProgress[file.name];
          return newProgress;
        });
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt']
    }
  });

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage = { type: 'user', content: query };
    setChatHistory(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/query`, {
        query: query,
        session_id: 'web-session',
        top_k: 5
      });

      const assistantMessage = {
        type: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        responseTime: response.data.response_time,
        cached: response.data.cached
      };

      setChatHistory(prev => [...prev, assistantMessage]);
      fetchStats();
    } catch (error) {
      console.error('Error querying:', error);
      const errorMessage = {
        type: 'error',
        content: 'Sorry, there was an error processing your query. Please try again.'
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      await axios.delete(`${API_BASE}/api/documents/${docId}`);
      fetchDocuments();
      fetchStats();
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <Sparkles size={32} />
            </div>
            <div>
              <h1 className="logo-title">DocuMind</h1>
              <p className="logo-subtitle">Enterprise Knowledge Intelligence</p>
            </div>
          </div>
          
          {stats && (
            <div className="stats-bar">
              <div className="stat-item">
                <Database size={18} />
                <div>
                  <span className="stat-value">{stats.total_documents}</span>
                  <span className="stat-label">Documents</span>
                </div>
              </div>
              <div className="stat-item">
                <MessageSquare size={18} />
                <div>
                  <span className="stat-value">{stats.total_queries}</span>
                  <span className="stat-label">Queries</span>
                </div>
              </div>
              <div className="stat-item">
                <Zap size={18} />
                <div>
                  <span className="stat-value">{stats.avg_response_time.toFixed(2)}s</span>
                  <span className="stat-label">Avg Response</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare size={20} />
          Chat
        </button>
        <button
          className={`nav-tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          <FileText size={20} />
          Documents
        </button>
        <button
          className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          <Upload size={20} />
          Upload
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'chat' && (
          <div className="chat-container">
            <div className="chat-messages">
              {chatHistory.length === 0 ? (
                <div className="empty-state">
                  <Sparkles size={64} className="empty-icon" />
                  <h2>Welcome to DocuMind</h2>
                  <p>Ask me anything about your documents and I'll help you find the answers.</p>
                  <div className="example-queries">
                    <p>Try asking:</p>
                    <button onClick={() => setQuery("What are our company policies?")} className="example-btn">
                      "What are our company policies?"
                    </button>
                    <button onClick={() => setQuery("Summarize our Q3 report")} className="example-btn">
                      "Summarize our Q3 report"
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {chatHistory.map((message, index) => (
                    <div key={index} className={`message message-${message.type}`}>
                      {message.type === 'user' && (
                        <div className="message-content">
                          <div className="message-avatar user-avatar">You</div>
                          <div className="message-text">{message.content}</div>
                        </div>
                      )}
                      {message.type === 'assistant' && (
                        <div className="message-content">
                          <div className="message-avatar assistant-avatar">
                            <Sparkles size={20} />
                          </div>
                          <div className="message-details">
                            <div className="message-text">
                              <ReactMarkdown>{message.content}</ReactMarkdown>
                            </div>
                            {message.sources && message.sources.length > 0 && (
                              <div className="sources">
                                <p className="sources-title">Sources:</p>
                                {message.sources.map((source, idx) => (
                                  <div key={idx} className="source-item">
                                    <FileText size={14} />
                                    <span>Document {source.document_id}, Section {source.chunk_index}</span>
                                    <span className="similarity">
                                      {(source.similarity_score * 100).toFixed(1)}% match
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                            <div className="message-meta">
                              <Clock size={12} />
                              <span>{message.responseTime.toFixed(2)}s</span>
                              {message.cached && <span className="cached-badge">Cached</span>}
                            </div>
                          </div>
                        </div>
                      )}
                      {message.type === 'error' && (
                        <div className="message-content error">
                          <XCircle size={20} />
                          <p>{message.content}</p>
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="message message-assistant">
                      <div className="message-content">
                        <div className="message-avatar assistant-avatar">
                          <Sparkles size={20} />
                        </div>
                        <div className="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </>
              )}
            </div>

            <form className="chat-input-form" onSubmit={handleQuery}>
              <div className="chat-input-container">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask anything about your documents..."
                  className="chat-input"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  className="send-button"
                  disabled={isLoading || !query.trim()}
                >
                  {isLoading ? <Loader className="spin" size={20} /> : <Send size={20} />}
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="documents-container">
            <div className="documents-header">
              <h2>Document Library</h2>
              <p>{documents.length} documents indexed</p>
            </div>

            {documents.length === 0 ? (
              <div className="empty-state">
                <FileText size={64} className="empty-icon" />
                <h3>No documents yet</h3>
                <p>Upload your first document to get started</p>
                <button onClick={() => setActiveTab('upload')} className="primary-btn">
                  <Upload size={20} />
                  Upload Document
                </button>
              </div>
            ) : (
              <div className="documents-grid">
                {documents.map(doc => (
                  <div key={doc.id} className="document-card">
                    <div className="document-icon">
                      <FileText size={32} />
                    </div>
                    <div className="document-info">
                      <h3>{doc.filename}</h3>
                      <div className="document-meta">
                        <span className="file-type">{doc.file_type.toUpperCase()}</span>
                        <span>•</span>
                        <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                        {doc.page_count && (
                          <>
                            <span>•</span>
                            <span>{doc.page_count} pages</span>
                          </>
                        )}
                      </div>
                      <div className="document-status">
                        {doc.processed ? (
                          <span className="status-badge success">
                            <CheckCircle size={14} />
                            Processed
                          </span>
                        ) : (
                          <span className="status-badge pending">
                            <Loader className="spin" size={14} />
                            Processing...
                          </span>
                        )}
                        <span className="upload-time">
                          {formatDistanceToNow(new Date(doc.upload_date), { addSuffix: true })}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteDocument(doc.id)}
                      className="delete-btn"
                      title="Delete document"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'upload' && (
          <div className="upload-container">
            <div className="upload-section">
              <h2>Upload Documents</h2>
              <p>Add PDFs, Word documents, spreadsheets, or text files to your knowledge base</p>

              <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
                <input {...getInputProps()} />
                <Upload size={48} className="dropzone-icon" />
                <p className="dropzone-text">
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here, or click to browse'}
                </p>
                <p className="dropzone-hint">
                  Supported: PDF, DOCX, XLSX, TXT
                </p>
              </div>

              {Object.keys(uploadProgress).length > 0 && (
                <div className="upload-progress">
                  <h3>Uploading...</h3>
                  {Object.entries(uploadProgress).map(([filename, progress]) => (
                    <div key={filename} className="progress-item">
                      <span className="progress-filename">{filename}</span>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                      </div>
                      <span className="progress-percent">{progress}%</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="upload-info">
                <h3>How it works</h3>
                <div className="info-steps">
                  <div className="info-step">
                    <div className="step-number">1</div>
                    <div>
                      <h4>Upload</h4>
                      <p>Add your documents to the platform</p>
                    </div>
                  </div>
                  <div className="info-step">
                    <div className="step-number">2</div>
                    <div>
                      <h4>Process</h4>
                      <p>AI extracts and indexes the content</p>
                    </div>
                  </div>
                  <div className="info-step">
                    <div className="step-number">3</div>
                    <div>
                      <h4>Query</h4>
                      <p>Ask questions and get instant answers</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
