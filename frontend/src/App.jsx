import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Github, LogOut, Loader2 } from 'lucide-react';
import Dashboard from './components/Dashboard';

// Ensure cookies are sent with every request
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await axios.get(`${API_URL}/auth/github/me`);
        setUser(res.data);
      } catch (err) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const handleLogin = () => {
    window.location.href = `${API_URL}/auth/github/login`;
  };

  const handleLogout = async () => {
    await axios.post(`${API_URL}/auth/github/logout`);
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-background text-textMain selection:bg-primary/30">
      <nav className="border-b border-surface bg-background/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="font-bold text-xl tracking-tight text-white flex gap-2 items-center">
            <span className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center border border-primary/30">
              Py
            </span>
            RuleCheck
          </div>

          {user && user.authenticated && (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <img src={user.avatar_url} alt="Avatar" className="w-8 h-8 rounded-full border border-slate-700" />
                <span className="text-sm font-medium text-slate-200">{user.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-slate-400 hover:text-red-400 transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </nav>
      <main>
        {loading ? (
          <div className="flex items-center justify-center h-[60vh]">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : user && user.authenticated ? (
          <Dashboard />
        ) : (
          <div className="max-w-lg mx-auto mt-24 text-center px-4">
            <div className="w-20 h-20 bg-slate-800/50 rounded-2xl border border-slate-700 mx-auto flex items-center justify-center mb-6">
              <Github className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-4">Code Security Scanning</h1>
            <p className="text-slate-400 mb-8 leading-relaxed">
              Authenticate with your GitHub account to start analyzing Python repositories for vulnerabilities, performance bottlenecks, and structural flaws.
            </p>
            <button
              onClick={handleLogin}
              className="flex items-center justify-center gap-3 bg-[#24292e] hover:bg-[#2f363d] text-white px-8 py-4 rounded-xl font-medium w-full transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
            >
              <Github className="w-5 h-5" />
              Continue with GitHub
            </button>
          </div>
        )}
      </main>
      <footer className="border-t border-surface py-8 mt-12 text-center text-textMuted text-sm">
        <p>Built with Deterministic Rule Engine Technology.</p>
        <p className="mt-2 text-slate-600">Disclaimer: Analyzes up to 5 Python files (max 1000 lines each).</p>
      </footer>
    </div>
  );
}

export default App;
