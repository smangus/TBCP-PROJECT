import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Icons - replace with your own if needed
import { FaSearch, FaSpinner, FaHistory, FaChevronDown, FaChevronUp, FaInfoCircle } from 'react-icons/fa';
import { GiMolecule, GiChart, GiMoneyStack, GiDiploma, GiTechnoHeart } from 'react-icons/gi';

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [memoryStats, setMemoryStats] = useState(null);
  const messagesEndRef = useRef(null);

  // Function to scroll to bottom of results
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (result) {
      scrollToBottom();
    }
  }, [result]);

  // Fetch memory stats on load
  useEffect(() => {
    fetchMemoryStats();
  }, []);

  const fetchMemoryStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/memory/stats');
      setMemoryStats(response.data);
    } catch (err) {
      console.error('Error fetching memory stats:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://localhost:8000/api/query', {
        query: query
      });
      
      setResult(response.data);
      
      // Refresh memory stats after a query
      fetchMemoryStats();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) return;
    
    try {
      const response = await axios.post('http://localhost:8000/api/search', {
        query: searchQuery,
        limit: 5
      });
      
      setSearchResults(response.data.results);
    } catch (err) {
      console.error('Error searching:', err);
    }
  };

  const toggleAgentResponse = (agentName) => {
    if (expandedAgent === agentName) {
      setExpandedAgent(null);
    } else {
      setExpandedAgent(agentName);
    }
  };

  // Get agent icon based on agent name
  const getAgentIcon = (agentName) => {
    switch (agentName) {
      case 'molecular_agent':
        return <GiMolecule />;
      case 'market_agent':
        return <GiChart />;
      case 'investor_agent':
        return <GiMoneyStack />;
      case 'ip_agent':
        return <GiDiploma />;
      case 'tech_stack_agent':
        return <GiTechnoHeart />;
      default:
        return <FaInfoCircle />;
    }
  };

  // Format agent name for display
  const formatAgentName = (agentName) => {
    if (!agentName) return '';
    const name = agentName.replace('_agent', '');
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>TechBio C-Suite CoPilot</h1>
        <p>AI-powered decision support for biotech executives</p>
      </header>

      <div className="content-container">
        <div className="sidebar">
          <div className="sidebar-section">
            <h3 onClick={() => setShowHistory(!showHistory)} className="sidebar-header">
              {showHistory ? <FaChevronUp /> : <FaChevronDown />} Recent Queries
            </h3>
            {showHistory && (
              <div className="search-container">
                <form onSubmit={handleSearchSubmit}>
                  <div className="search-input-container">
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search past conversations..."
                      className="search-input"
                    />
                    <button type="submit" className="search-button">
                      <FaSearch />
                    </button>
                  </div>
                </form>
                
                {searchResults.length > 0 && (
                  <div className="search-results">
                    {searchResults.map((result) => (
                      <div 
                        key={result.id} 
                        className="search-result-item"
                        onClick={() => {
                          setQuery(result.user_query);
                          setShowHistory(false);
                        }}
                      >
                        <div className="search-result-query">{result.user_query}</div>
                        <div className="search-result-date">
                          {new Date(result.timestamp).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
          
          {memoryStats && (
            <div className="sidebar-section">
              <h3 className="sidebar-header">Memory Stats</h3>
              <div className="memory-stats">
                <div>
                  <strong>Agents:</strong> {Object.keys(memoryStats.agent_memory).length}
                </div>
                <div>
                  <strong>Conversations:</strong> {memoryStats.conversations.total}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="main-content">
          <form onSubmit={handleSubmit} className="query-form">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about molecular structures, biotech market trends, investment strategies, IP considerations, or tech infrastructure..."
              rows={4}
              className="query-input"
            />
            <button 
              type="submit" 
              className="submit-button"
              disabled={isLoading}
            >
              {isLoading ? <FaSpinner className="spinner" /> : 'Submit'}
            </button>
          </form>

          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
            </div>
          )}

          {result && (
            <div className="result-container">
              <div className="result-header">
                <h2>Response</h2>
                <div className="result-meta">
                  {result.processing_time && (
                    <span className="processing-time">
                      Processed in {result.processing_time}s
                    </span>
                  )}
                  <div className="contributing-agents">
                    {result.contributing_agents.map((agent, index) => (
                      <span key={index} className="agent-badge">
                        {getAgentIcon(agent)} {formatAgentName(agent)}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="synthesized-response">
                {result.response.split('\n').map((paragraph, index) => (
                  paragraph ? <p key={index}>{paragraph}</p> : <br key={index} />
                ))}
              </div>

              {result.agent_responses && Object.keys(result.agent_responses).length > 0 && (
                <div className="agent-responses-container">
                  <h3>Contributing Agent Details</h3>
                  <div className="agent-responses">
                    {Object.entries(result.agent_responses).map(([agentName, response]) => (
                      <div key={agentName} className="agent-response-card">
                        <div 
                          className="agent-header"
                          onClick={() => toggleAgentResponse(agentName)}
                        >
                          <h4>
                            {getAgentIcon(agentName)} {formatAgentName(agentName)} Analysis
                          </h4>
                          <span>{expandedAgent === agentName ? <FaChevronUp /> : <FaChevronDown />}</span>
                        </div>
                        
                        {expandedAgent === agentName && (
                          <div className="agent-content">
                            {typeof response === 'string' ? (
                              response.split('\n').map((paragraph, index) => (
                                paragraph ? <p key={index}>{paragraph}</p> : <br key={index} />
                              ))
                            ) : (
                              <p>Complex response format (see synthesized answer)</p>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>
      
      <footer className="app-footer">
        <p>TechBio C-Suite CoPilot powered by TxGemma &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;