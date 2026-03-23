import React, { useState } from 'react';
import axios from 'axios';
import { Github, Loader2, ShieldAlert, Activity, FileWarning, Zap, Download, Sparkles, Archive } from 'lucide-react';
import ScoreCard from './ScoreCard';
import IssueList from './IssueList';
import MetricsPanel from './MetricsPanel';
import AIFixList from './AIFixList';
import RepoSelector from './RepoSelector';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';

export default function Dashboard() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [downloadingRepo, setDownloadingRepo] = useState(false);
    const [error, setError] = useState('');
    const [report, setReport] = useState(null);
    const [activeTab, setActiveTab] = useState('security');
    const [hasAppliedFixes, setHasAppliedFixes] = useState(false);

    const analyzeRepo = async (repoUrl) => {
        if (!repoUrl || !repoUrl.trim() || !repoUrl.startsWith('https://github.com/')) {
            setError('Please enter a valid GitHub repository URL.');
            return;
        }

        setUrl(repoUrl);
        setLoading(true);
        setError('');
        setReport(null);
        setHasAppliedFixes(false);

        try {
            const response = await axios.post(`${API_URL}/analyze`, { github_url: repoUrl }, {
                withCredentials: true
            });
            setReport(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'An unexpected error occurred during analysis.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (!report) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "pyrulecheck_report.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const handleDownloadRepo = async () => {
        if (!report) return;
        setDownloadingRepo(true);
        try {
            const response = await axios.get(`${API_URL}/download-repo`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'patched_repository.zip');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert("Failed to download repository. It may have expired or been cleaned up.");
        } finally {
            setDownloadingRepo(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <header className="flex flex-col items-center justify-center mb-12">
                <div className="flex items-center gap-3 mb-4">
                    <ShieldAlert className="w-10 h-10 text-primary animate-pulse" />
                    <h1 className="text-4xl font-bold tracking-tight">PyRuleCheck</h1>
                </div>
                <p className="text-textMuted text-lg mb-4 max-w-2xl text-center">
                    Static code analysis engine for Python repositories. Secure, fast, and deterministic. No AI, just strict rules.
                </p>
                <p className="text-slate-400 text-sm mb-8 max-w-2xl text-center font-medium bg-slate-800/50 py-2 px-4 rounded-lg border border-slate-700/50">
                    Maximum 5 Python files will be analyzed. <br />
                    Each file must contain fewer than 1000 lines of code.
                </p>

                {loading ? (
                    <div className="w-full max-w-2xl bg-surface rounded-2xl border border-surface-light p-12 shadow-xl flex flex-col items-center justify-center">
                        <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
                        <h3 className="text-xl font-bold mb-2">Analyzing Repository...</h3>
                        <p className="text-slate-400 text-center text-sm">Parsing Python AST, searching for vulnerabilities, and computing code quality metrics.</p>
                    </div>
                ) : !report && (
                    <div className="w-full">
                        <RepoSelector onScanStart={analyzeRepo} />
                        {error && <p className="text-danger mt-3 text-sm text-center font-medium animate-bounce">{error}</p>}
                    </div>
                )}
            </header>

            {report && (
                <div className="animate-fade-in opacity-100 transition-opacity duration-500">
                    <div className="flex justify-between items-center mb-8">
                        <h2 className="text-2xl font-bold text-white">Analysis Report</h2>
                        <div className="flex gap-3">
                            {hasAppliedFixes && (
                                <button
                                    onClick={handleDownloadRepo}
                                    disabled={downloadingRepo}
                                    className="flex items-center gap-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/50 px-4 py-2 rounded-lg text-sm transition-colors text-blue-300 disabled:opacity-50"
                                >
                                    {downloadingRepo ? <Loader2 className="w-4 h-4 animate-spin" /> : <Archive className="w-4 h-4" />} Download Patched Code
                                </button>
                            )}
                            <button
                                onClick={handleDownload}
                                className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 px-4 py-2 rounded-lg text-sm transition-colors text-white"
                            >
                                <Download className="w-4 h-4" /> Download JSON
                            </button>
                        </div>
                    </div>

                    <ScoreCard summary={report.summary} />

                    <div className="mt-12 bg-surface rounded-xl border border-slate-700/50 overflow-hidden">
                        <div className="flex overflow-x-auto border-b border-slate-700/50 scrollbar-hide">
                            <Tab
                                active={activeTab === 'security'}
                                onClick={() => setActiveTab('security')}
                                icon={<ShieldAlert className="w-4 h-4" />}
                                label={`Security (${report.issues.critical.length + report.issues.major.length})`}
                            />
                            <Tab
                                active={activeTab === 'quality'}
                                onClick={() => setActiveTab('quality')}
                                icon={<Activity className="w-4 h-4" />}
                                label="Code Quality"
                            />
                            <Tab
                                active={activeTab === 'performance'}
                                onClick={() => setActiveTab('performance')}
                                icon={<Zap className="w-4 h-4" />}
                                label="Performance"
                            />
                            <Tab
                                active={activeTab === 'metrics'}
                                onClick={() => setActiveTab('metrics')}
                                icon={<FileWarning className="w-4 h-4" />}
                                label="Metrics & Cross-File"
                            />
                            <Tab
                                active={activeTab === 'ai_fixes'}
                                onClick={() => setActiveTab('ai_fixes')}
                                icon={<Sparkles className="w-4 h-4 text-purple-400" />}
                                label={`AI Fixes (${report.ai_fix_suggestions ? report.ai_fix_suggestions.length : 0})`}
                            />
                        </div>

                        <div className="p-6">
                            {activeTab === 'security' && (
                                <IssueList title="Security Issues" issues={[...report.issues.critical, ...report.issues.major]} type="security" />
                            )}
                            {activeTab === 'quality' && (
                                <IssueList title="Code Quality Issues" issues={report.issues.minor} type="quality" />
                            )}
                            {activeTab === 'performance' && (
                                <IssueList title="Performance Issues" issues={report.issues.minor} type="performance" filterPrefix="PERF" />
                            )}
                            {activeTab === 'metrics' && (
                                <MetricsPanel metrics={report.metrics} crossFile={report.cross_file_analysis} />
                            )}
                            {activeTab === 'ai_fixes' && (
                                <AIFixList
                                    repoFullName={url.replace('https://github.com/', '').replace('.git', '')}
                                    aiStatus={report.ai_status}
                                    suggestions={report.ai_fix_suggestions}
                                    onFixApplied={() => setHasAppliedFixes(true)}
                                />
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function Tab({ active, onClick, icon, label }) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-2 px-6 py-4 text-sm font-medium whitespace-nowrap transition-colors ${active
                ? 'text-primary border-b-2 border-primary bg-primary/5'
                : 'text-textMuted hover:text-white hover:bg-white/5'
                }`}
        >
            {icon}
            {label}
        </button>
    );
}
