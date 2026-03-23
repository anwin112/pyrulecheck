import React, { useState } from 'react';
import axios from 'axios';
import { Sparkles, FileCode2, ChevronDown, CheckCircle2, Loader2, XCircle, Github } from 'lucide-react';

export default function AIFixList({ aiStatus, suggestions, onFixApplied, repoFullName }) {
    if (aiStatus === "not_configured" || aiStatus === "skipped_no_key") {
        return (
            <div className="text-center py-12 border border-dashed border-slate-700 rounded-xl bg-slate-800/20">
                <Sparkles className="w-12 h-12 text-slate-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">AI Fix Suggestions Not Configured</h3>
                <p className="text-slate-400 text-sm max-w-md mx-auto">
                    Add a <code className="bg-slate-800 px-1 rounded">GEMINI_API_KEY</code> to your backend environment variables to enable automated AI fix suggestions.
                </p>
            </div>
        );
    }

    if (aiStatus === "failed") {
        return (
            <div className="text-center py-12 border border-dashed border-slate-700 rounded-xl bg-red-500/5">
                <Sparkles className="w-12 h-12 text-red-400/50 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">AI Generation Failed</h3>
                <p className="text-slate-400 text-sm">
                    The Gemini API encountered an error or timed out while generating suggestions.
                </p>
            </div>
        );
    }

    if (aiStatus === "rate_limited") {
        return (
            <div className="text-center py-12 border border-dashed border-yellow-700/50 rounded-xl bg-yellow-500/5">
                <Sparkles className="w-12 h-12 text-yellow-400/50 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">API Rate Limit Reached</h3>
                <p className="text-slate-400 text-sm max-w-md mx-auto">
                    The Gemini AI free-tier rate limit has been exhausted. Please wait a minute and try analyzing the repository again.
                </p>
            </div>
        );
    }

    if (!suggestions || suggestions.length === 0) {
        return (
            <div className="text-center py-12">
                <div className="w-16 h-16 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-500/20">
                    <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-medium text-white mb-1">No Fixes Needed</h3>
                <p className="text-slate-400 text-sm">The deterministic scan found no critical/major issues to fix.</p>
            </div>
        );
    }

    const [applyingAll, setApplyingAll] = useState(false);
    const [applyAllMessage, setApplyAllMessage] = useState('');
    const [globalApplySuccess, setGlobalApplySuccess] = useState(false);

    const [pushing, setPushing] = useState(false);
    const [pushMessage, setPushMessage] = useState('');
    const [pushResult, setPushResult] = useState(null);

    const handleApplyAll = async () => {
        setApplyingAll(true);
        setApplyAllMessage('');
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';
            const res = await axios.post(`${API_URL}/apply-all-fixes`);
            setApplyAllMessage(`Successfully applied ${res.data.applied_fixes} fixes!`);
            setGlobalApplySuccess(true);
            if (onFixApplied) onFixApplied();
        } catch (e) {
            setApplyAllMessage("Failed to apply fixes: " + (e.response?.data?.detail || e.message));
        }
        setApplyingAll(false);
    };

    const handlePushFixes = async () => {
        setPushing(true);
        setPushMessage('Initializing GitHub push...');
        setPushResult(null);

        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';
        
        // Start polling for status updates
        const pollInterval = setInterval(async () => {
            try {
                const statusRes = await axios.get(`${API_URL}/github/push-status`, { withCredentials: true });
                if (statusRes.data && statusRes.data.status === 'in_progress') {
                    setPushMessage(`Pushing: ${statusRes.data.step}...`);
                }
            } catch (err) {}
        }, 1500);

        try {
            const res = await axios.post(`${API_URL}/github/push-fixes`, {
                repo_full_name: repoFullName
            }, { withCredentials: true });
            
            clearInterval(pollInterval);
            setPushResult(res.data);
            setPushMessage('Push successful!');
        } catch (err) {
            clearInterval(pollInterval);
            setPushMessage("Failed to push fixes: " + (err.response?.data?.detail || err.message));
        }
        setPushing(false);
    };

    return (
        <div className="space-y-6 flex flex-col h-full">
            <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl flex items-start gap-4">
                <Sparkles className="w-6 h-6 text-blue-400 shrink-0 mt-0.5" />
                <div>
                    <h4 className="text-blue-200 font-medium mb-1">AI-Powered Fixes (Gemini)</h4>
                    <p className="text-xs text-blue-300/80 leading-relaxed">
                        These suggestions are generated dynamically based on the results of the static scanning engine. The AI does not detect issues itself, it only curates solutions. Always review generated code before applying to production.
                    </p>
                </div>
            </div>

            <div className="space-y-4 flex-1">
                {suggestions.map((suggestion, idx) => (
                    <AIFixItem key={idx} suggestion={suggestion} isAppliedAll={globalApplySuccess} onFixApplied={onFixApplied} />
                ))}
            </div>

            <div className="pt-6 border-t border-slate-700/50 mt-auto flex flex-col items-center justify-center gap-3">
                <button
                    onClick={handleApplyAll}
                    disabled={applyingAll}
                    className="flex items-center gap-2 bg-primary hover:bg-blue-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-8 py-3 rounded-full font-medium transition-colors w-full max-w-sm justify-center shadow-lg"
                >
                    {applyingAll ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle2 className="w-5 h-5" />}
                    {applyingAll ? 'Applying...' : 'Apply All Fixes'}
                </button>
                {applyAllMessage && (
                    <span className={`text-sm font-medium ${applyAllMessage.includes('Failed') ? 'text-danger' : 'text-green-400'}`}>
                        {applyAllMessage}
                    </span>
                )}
                
                {globalApplySuccess && !pushResult && (
                    <div className="w-full max-w-sm mt-4">
                        <button
                            onClick={handlePushFixes}
                            disabled={pushing}
                            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-3 rounded-full font-medium transition-colors w-full justify-center shadow-lg text-sm"
                        >
                            {pushing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Github className="w-4 h-4" />}
                            {pushing ? pushMessage : 'Push Approved Fixes to GitHub'}
                        </button>
                        {pushMessage && !pushing && pushMessage.includes('Failed') && (
                            <p className="text-danger text-sm font-medium mt-2 text-center">{pushMessage}</p>
                        )}
                    </div>
                )}
                
                {pushResult && pushResult.status === 'success' && (
                    <div className="w-full max-w-md mt-4 bg-green-900/20 border border-green-500/30 rounded-xl p-5">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="bg-green-500/20 p-2 rounded-full text-green-400">
                                <CheckCircle2 className="w-5 h-5" />
                            </div>
                            <h4 className="font-medium text-white">Successfully Pushed to GitHub</h4>
                        </div>
                        <div className="space-y-2 text-sm">
                            <p className="flex justify-between">
                                <span className="text-slate-400">Branch:</span>
                                <span className="text-slate-200 font-mono">{pushResult.branch}</span>
                            </p>
                            <div className="pt-3 flex gap-3 mt-1">
                                <a href={pushResult.commit_url} target="_blank" rel="noopener noreferrer" className="flex-1 flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 py-2 rounded-lg text-xs font-medium transition-colors">
                                    <FileCode2 className="w-3.5 h-3.5" /> View Commit
                                </a>
                                <a href={pushResult.pr_url} target="_blank" rel="noopener noreferrer" className="flex-1 flex items-center justify-center gap-2 bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/50 text-blue-300 py-2 rounded-lg text-xs font-medium transition-colors">
                                    <Github className="w-3.5 h-3.5" /> Review PR #{pushResult.pr_number}
                                </a>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function AIFixItem({ suggestion, isAppliedAll, onFixApplied }) {
    const [expanded, setExpanded] = useState(false);
    const [status, setStatus] = useState('pending'); // pending, applying, applied, rejecting, rejected

    const effectiveStatus = (isAppliedAll && status === 'pending') ? 'applied' : status;

    const handleApply = async (e) => {
        e.stopPropagation();
        setStatus('applying');
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';
            await axios.post(`${API_URL}/apply-fix`, {
                fix_id: suggestion.fix_id,
                file: suggestion.file,
                line: suggestion.line,
                secure_code_example: suggestion.secure_code_example
            });
            setStatus('applied');
            setExpanded(false);
            if (onFixApplied) onFixApplied();
        } catch (err) {
            setStatus('pending');
            alert('Failed to apply fix: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleReject = async (e) => {
        e.stopPropagation();
        setStatus('rejecting');
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
            await axios.post(`${API_URL}/reject-fix`, { fix_id: suggestion.fix_id });
            setStatus('rejected');
            setExpanded(false);
        } catch (err) {
            setStatus('pending');
        }
    };

    let borderClass = "border-slate-700/50 bg-slate-800/30";
    if (effectiveStatus === 'applied') borderClass = "border-green-500/50 bg-green-500/10";
    if (effectiveStatus === 'rejected') borderClass = "border-slate-800 bg-slate-900/50 opacity-60 grayscale";

    return (
        <div className={`border rounded-xl overflow-hidden transition-all duration-300 ${borderClass}`}>
            <div
                onClick={() => setExpanded(!expanded)}
                className="w-full text-left p-4 flex items-center justify-between hover:bg-slate-700/20 cursor-pointer"
            >
                <div className="flex items-start gap-4 flex-1">
                    <div className={`p-2 rounded-lg border flex-shrink-0 ${effectiveStatus === 'applied' ? 'border-green-500/30 bg-green-500/10 text-green-400' : 'border-purple-500/30 bg-purple-500/10 text-purple-400'}`}>
                        {effectiveStatus === 'applied' ? <CheckCircle2 className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
                    </div>

                    <div className="flex-1 min-w-0 pr-4">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-white">Suggested Fix: {suggestion.issue_type}</span>
                            <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${expanded ? 'rotate-180' : ''}`} />
                        </div>
                        <div className="flex items-center gap-2 text-sm text-slate-400">
                            <FileCode2 className="w-4 h-4" />
                            <span className="truncate">{suggestion.file}</span>
                            <span className="text-slate-500">Line {suggestion.line}</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0 ml-4">
                        {effectiveStatus === 'applied' && <span className="text-green-400 text-sm font-medium px-2 py-1 bg-green-400/10 rounded-lg">Applied</span>}
                        {effectiveStatus === 'rejected' && <span className="text-slate-400 text-sm font-medium px-2 py-1 bg-slate-400/10 rounded-lg">Rejected</span>}
                        {effectiveStatus === 'pending' && (
                            <>
                                <button onClick={handleReject} className="flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg transition-colors border border-slate-700">
                                    <XCircle className="w-3.5 h-3.5" /> Reject
                                </button>
                                <button onClick={handleApply} className="flex items-center gap-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-500 px-3 py-1.5 rounded-lg transition-colors shadow-lg shadow-green-900/20">
                                    <CheckCircle2 className="w-3.5 h-3.5" /> Apply Fix
                                </button>
                            </>
                        )}
                        {(effectiveStatus === 'applying' || effectiveStatus === 'rejecting') && (
                            <Loader2 className="w-5 h-5 text-slate-400 animate-spin mr-4" />
                        )}
                    </div>
                </div>
            </div>

            {expanded && (
                <div className="p-5 border-t border-slate-700/50 space-y-5 bg-surface/50">
                    <div>
                        <h5 className="text-xs font-semibold text-red-300 uppercase tracking-wider mb-2">Risk Explanation</h5>
                        <p className="text-sm text-slate-300 leading-relaxed">{suggestion.risk_explanation}</p>
                    </div>

                    <div>
                        <h5 className="text-xs font-semibold text-green-300 uppercase tracking-wider mb-2">Recommended Fix</h5>
                        <p className="text-sm text-slate-300 leading-relaxed">{suggestion.recommended_fix_explanation}</p>
                    </div>

                    <div>
                        <h5 className="text-xs font-semibold text-blue-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                            <CodeIcon /> Secure Code Example
                        </h5>
                        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800 overflow-x-auto relative group">
                            <button
                                className="absolute top-2 right-2 text-xs bg-slate-800 hover:bg-slate-700 text-slate-400 px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={(e) => {
                                    navigator.clipboard.writeText(suggestion.secure_code_example);
                                    e.target.innerText = 'Copied!';
                                    setTimeout(() => e.target.innerText = 'Copy', 2000);
                                }}
                            >
                                Copy
                            </button>
                            <pre className="text-sm text-slate-300 font-mono">
                                {suggestion.secure_code_example}
                            </pre>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function CodeIcon() {
    return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
    );
}
