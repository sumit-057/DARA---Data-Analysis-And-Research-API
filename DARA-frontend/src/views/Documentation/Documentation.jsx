import React, { useState, useEffect } from 'react';
import './Documentation.css';

export default function Documentation() {
  const [docs, setDocs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeDataset, setActiveDataset] = useState('olympics');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedEndpoint, setExpandedEndpoint] = useState(null);

  useEffect(() => {
    fetchDocumentation();
  }, []);

  const fetchDocumentation = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/docs/detailed');
      if (!response.ok) throw new Error('Failed to fetch documentation');
      const data = await response.json();
      setDocs(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="docs-container">
        <div className="loading-spinner"></div>
        <p>Loading API Documentation...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="docs-container">
        <div className="error-message">
          <p>⚠️ Error loading documentation: {error}</p>
          <button onClick={fetchDocumentation} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  if (!docs) return null;

  const currentDataset = docs.datasets[activeDataset];
  const filteredEndpoints = currentDataset.endpoints.filter(ep =>
    ep.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ep.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleEndpoint = (index) => {
    setExpandedEndpoint(expandedEndpoint === index ? null : index);
  };

  return (
    <div className="docs-container">
      <header className="docs-header">
        <h1>🚀 API Documentation</h1>
        <p className="docs-subtitle">{docs.title} - v{docs.api_version}</p>
        <p className="docs-description">{docs.description}</p>
      </header>

      <div className="docs-content">
        {/* Dataset Tabs */}
        <div className="dataset-tabs">
          {Object.entries(docs.datasets).map(([key, dataset]) => (
            <button
              key={key}
              className={`tab-button ${activeDataset === key ? 'active' : ''}`}
              onClick={() => {
                setActiveDataset(key);
                setSearchTerm('');
                setExpandedEndpoint(null);
              }}
            >
              {dataset.name}
            </button>
          ))}
        </div>

        {/* Dataset Info & Search */}
        <div className="dataset-info">
          <div className="info-section">
            <h2>{currentDataset.name}</h2>
            <p>{currentDataset.description}</p>
          </div>

          <div className="search-section">
            <input
              type="text"
              placeholder="🔍 Search endpoints by name or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            {searchTerm && (
              <button className="clear-search" onClick={() => setSearchTerm('')}>✕</button>
            )}
          </div>
        </div>

        {/* Endpoints List */}
        <div className="endpoints-section">
          <h3>Endpoints ({filteredEndpoints.length})</h3>
          
          {filteredEndpoints.length === 0 ? (
            <div className="no-results">
              <p>No endpoints match your search. Try a different keyword.</p>
            </div>
          ) : (
            <div className="endpoints-list">
              {filteredEndpoints.map((endpoint, index) => (
                <div key={index} className="endpoint-card">
                  <div
                    className="endpoint-header"
                    onClick={() => toggleEndpoint(index)}
                  >
                    <div className="endpoint-title">
                      <span className={`method-badge ${endpoint.method.toLowerCase()}`}>
                        {endpoint.method}
                      </span>
                      <code className="endpoint-path">{endpoint.path}</code>
                    </div>
                    <span className={`toggle-icon ${expandedEndpoint === index ? 'expanded' : ''}`}>
                      ▼
                    </span>
                  </div>

                  <p className="endpoint-description">{endpoint.description}</p>

                  {expandedEndpoint === index && (
                    <div className="endpoint-details">
                      {endpoint.parameters && endpoint.parameters.length > 0 && (
                        <div className="details-section">
                          <h4>Parameters</h4>
                          <div className="parameters-table">
                            <div className="param-header">
                              <span>Name</span>
                              <span>Type</span>
                              <span>Required</span>
                              <span>Description</span>
                            </div>
                            {endpoint.parameters.map((param, pIdx) => (
                              <div key={pIdx} className="param-row">
                                <span className="param-name">{param.name}</span>
                                <span className="param-type">{param.type}</span>
                                <span className="param-required">
                                  {param.required ? '✓' : '✗'}
                                  {param.default && ` (default: ${param.default})`}
                                </span>
                                <span className="param-description">{param.description}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="details-section">
                        <h4>Example URL</h4>
                        <div className="example-url">
                          <code>http://localhost:5000{endpoint.example_url}</code>
                          <button
                            className="copy-btn"
                            onClick={() => {
                              navigator.clipboard.writeText(`http://localhost:5000${endpoint.example_url}`);
                              alert('URL copied to clipboard!');
                            }}
                          >
                            📋 Copy
                          </button>
                        </div>
                      </div>

                      {endpoint.sample_response && (
                        <div className="details-section">
                          <h4>Sample Response</h4>
                          <div className="sample-response">
                            <pre>{JSON.stringify(endpoint.sample_response, null, 2)}</pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="docs-footer">
        <p>💡 Base URL: <code>http://localhost:5000</code></p>
        <p>📝 All endpoints return JSON responses</p>
        <p>⚙️ For issues or questions, contact the API support team</p>
      </div>
    </div>
  );
}
