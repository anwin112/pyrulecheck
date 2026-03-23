import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Search, CheckCircle, XCircle, Github, Lock, Globe, Shield } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';

const RepoSelector = ({ onScanStart }) => {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRepoUrl, setSelectedRepoUrl] = useState('');
  const [isManualMode, setIsManualMode] = useState(false);
  const [manualUrl, setManualUrl] = useState('');

  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [validatedRepo, setValidatedRepo] = useState(null);

  useEffect(() => {
    fetchRepos();
  }, []);

  const fetchRepos = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/github/repos/list`, {
        withCredentials: true
      });
      setRepos(res.data.repositories);
    } catch (err) {
      setError('Failed to fetch your repositories. Please try refreshing.');
    } finally {
      setLoading(false);
    }
  };

  const handleValidation = async () => {
    setValidationError('');
    setValidatedRepo(null);
    setIsValidating(true);
    
    const urlToValidate = isManualMode ? manualUrl : selectedRepoUrl;
    
    if (!urlToValidate) {
      setValidationError('Please select or enter a repository URL.');
      setIsValidating(false);
      return;
    }

    try {
      const res = await axios.post(`${API_URL}/github/repos/validate`, 
        { repo_url: urlToValidate },
        { withCredentials: true }
      );
      
      setValidatedRepo(res.data.repository);
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Failed to validate repository access.';
      setValidationError(errMsg);
    } finally {
      setIsValidating(false);
    }
  };

  const filteredRepos = repos.filter(repo => 
    repo.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-surface rounded-2xl border border-surface-light p-6 shadow-xl w-full max-w-2xl mx-auto mb-8">
      <h2 className="text-xl font-bold flex items-center gap-2 mb-6">
        <Github className="w-6 h-6 text-primary" />
        Select Repository
      </h2>

      {/* Input Selection Mode */}
      <div className="flex gap-4 mb-6 border-b border-surface-light pb-4">
        <button 
          onClick={() => setIsManualMode(false)}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${!isManualMode ? 'bg-primary text-white' : 'bg-background hover:bg-surface-light text-slate-300'}`}
        >
          My Repositories
        </button>
        <button 
          onClick={() => setIsManualMode(true)}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${isManualMode ? 'bg-primary text-white' : 'bg-background hover:bg-surface-light text-slate-300'}`}
        >
          Manual URL
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm mb-4">
          {error}
        </div>
      ) : (
        <>
          {/* Dropdown / Search Mode */}
          {!isManualMode && (
            <div className="mb-6">
              <div className="relative mb-4">
                <Search className="absolute left-3 top-3.5 w-5 h-5 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Search your repositories..."
                  className="w-full bg-background border border-surface-light rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="max-h-64 overflow-y-auto rounded-xl border border-surface-light bg-background scrollbar-thin scrollbar-thumb-surface-light">
                {filteredRepos.length > 0 ? (
                  <div className="flex flex-col divide-y divide-surface-light">
                    {filteredRepos.map(repo => (
                      <button
                        key={repo.id}
                        onClick={() => setSelectedRepoUrl(repo.clone_url)}
                        className={`text-left px-4 py-3 hover:bg-surface flex items-center justify-between transition-colors ${selectedRepoUrl === repo.clone_url ? 'bg-primary/10 border-l-2 border-primary' : ''}`}
                      >
                        <div className="flex items-center gap-3">
                          {repo.private ? <Lock className="w-4 h-4 text-slate-400" /> : <Globe className="w-4 h-4 text-slate-400" />}
                          <span className="font-medium text-slate-200">{repo.full_name}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 text-center text-sm text-slate-400">
                    No repositories found matching your search.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Manual URL Mode */}
          {isManualMode && (
            <div className="mb-6">
              <input 
                type="text" 
                placeholder="https://github.com/username/repository.git"
                className="w-full bg-background border border-surface-light rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                value={manualUrl}
                onChange={(e) => setManualUrl(e.target.value)}
              />
              <p className="text-xs text-slate-500 mt-2 ml-1">Must be a repository you have read access to.</p>
            </div>
          )}

          {/* Validation Errors */}
          {validationError && (
             <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 p-3 rounded-lg mb-4">
               <XCircle className="w-5 h-5 shrink-0 mt-0.5" />
               <p>{validationError}</p>
             </div>
          )}

          {/* Validated Repository Card */}
          {validatedRepo && !validationError && (
            <div className="bg-background border border-green-500/30 rounded-xl p-4 mb-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Access Verified</span>
                </div>
                <div className="flex gap-2">
                  <span className="text-xs font-semibold uppercase px-2 py-1 rounded bg-surface text-slate-300 border border-surface-light">
                    {validatedRepo.private ? 'Private' : 'Public'}
                  </span>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-surface text-slate-300 border border-surface-light flex items-center gap-1">
                    <Shield className="w-3 h-3" />
                    {validatedRepo.permissions?.admin ? 'Admin' : validatedRepo.permissions?.push ? 'Write' : 'Read-Only'}
                  </span>
                </div>
              </div>
              <h3 className="font-bold text-lg">{validatedRepo.full_name}</h3>
              <p className="text-sm text-slate-400 mt-1">Default Branch: {validatedRepo.default_branch}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col gap-3 mt-2">
            {!validatedRepo ? (
               <button 
                 onClick={handleValidation}
                 disabled={isValidating || (!isManualMode && !selectedRepoUrl) || (isManualMode && !manualUrl)}
                 className="w-full py-3 rounded-xl font-medium bg-surface-light hover:bg-surface-light text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
               >
                 {isValidating ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                 Validate Access
               </button>
            ) : (
               <button 
                 onClick={() => onScanStart(validatedRepo.clone_url)}
                 className="w-full py-3 rounded-xl font-bold bg-primary hover:bg-primary-hover text-white shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 transform hover:-translate-y-0.5"
               >
                 Start Security Scan
               </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default RepoSelector;
