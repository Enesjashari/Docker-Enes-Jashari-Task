import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [n, setN] = useState(200000);
  const [chunks, setChunks] = useState(16);
  const [jobId, setJobId] = useState(null);
  const [jobState, setJobState] = useState(null);
  const [progress, setProgress] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const pollingInterval = useRef(null);

  useEffect(() => {
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  const pollJobStatus = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/jobs/${id}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      setJobState(data.state);
      setProgress(data.progress);
      
      if (data.state === 'SUCCESS') {
        setResult(data.result);
        setLoading(false);
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
          pollingInterval.current = null;
        }
      } else if (data.state === 'FAILURE') {
        setError(data.error || 'Job failed');
        setLoading(false);
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
          pollingInterval.current = null;
        }
      }
    } catch (err) {
      console.error('Error polling job status:', err);
      setError(`Failed to get job status: ${err.message}`);
      setLoading(false);
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
        pollingInterval.current = null;
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setJobId(null);
    setJobState(null);
    setProgress(null);
    setResult(null);
    setError(null);
    setLoading(true);
    
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/count-primes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ n: parseInt(n), chunks: parseInt(chunks) }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setJobId(data.job_id);
      
      pollingInterval.current = setInterval(() => {
        pollJobStatus(data.job_id);
      }, 1000);
      
      pollJobStatus(data.job_id);
      
    } catch (err) {
      console.error('Error submitting job:', err);
      setError(`Failed to submit job: ${err.message}`);
      setLoading(false);
    }
  };

  const progressPercentage = progress 
    ? Math.round((progress.completed / progress.total) * 100)
    : 0;

  return (
    <div className="App">
      <div className="container">
        <h1> Distributed Prime Counter</h1>
        <p className="subtitle">Count prime numbers using parallel processing</p>
        
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="n">
              Maximum Number (N)
              <span className="hint">Must be ≥ 10,000</span>
            </label>
            <input
              type="number"
              id="n"
              value={n}
              onChange={(e) => setN(e.target.value)}
              min="10000"
              required
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="chunks">
              Number of Chunks
              <span className="hint">1-128 parallel tasks</span>
            </label>
            <input
              type="number"
              id="chunks"
              value={chunks}
              onChange={(e) => setChunks(e.target.value)}
              min="1"
              max="128"
              required
              disabled={loading}
            />
          </div>
          
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Processing...' : 'Count Primes'}
          </button>
        </form>
        
        {jobId && (
          <div className="job-info">
            <div className="job-id">
              <strong>Job ID:</strong>
              <code>{jobId}</code>
            </div>
          </div>
        )}
        
        {jobState && (
          <div className="status-section">
            <div className="status-badge" data-state={jobState}>
              {jobState}
            </div>
            
            {progress && (
              <div className="progress-section">
                <div className="progress-info">
                  <span>Progress: {progress.completed} / {progress.total} chunks</span>
                  <span>{progressPercentage}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )}
        
        {result && (
          <div className="result-section">
            <h2>Results</h2>
            <div className="result-grid">
              <div className="result-item">
                <span className="result-label">Prime Count</span>
                <span className="result-value">{result.prime_count.toLocaleString()}</span>
              </div>
              <div className="result-item">
                <span className="result-label">Max Number (N)</span>
                <span className="result-value">{result.n.toLocaleString()}</span>
              </div>
              <div className="result-item">
                <span className="result-label">Duration</span>
                <span className="result-value">{result.duration_sec}s</span>
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="error-section">
            <strong>❌ Error:</strong> {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

