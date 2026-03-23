import React, { useState } from 'react';
import { AlertTriangle, ChevronRight, FileCode2 } from 'lucide-react';

export default function IssueList({ title, issues, type, filterPrefix }) {
    // If we only want specific issues like PERF or QUAL from minor/major list
    const filteredIssues = filterPrefix
        ? issues.filter(i => i.rule_id.startsWith(filterPrefix))
        : (type === 'quality' ? issues.filter(i => i.rule_id.startsWith('QUAL')) : issues);

    if (!filteredIssues || filteredIssues.length === 0) {
        return (
            <div className="text-center py-12">
                <div className="w-16 h-16 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-500/20">
                    <AlertTriangle className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-medium text-white mb-1">No Issues Found</h3>
                <p className="text-slate-400 text-sm">Great job! Your code passes all {title.toLowerCase()}.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {filteredIssues.map((issue, idx) => (
                <IssueItem key={idx} issue={issue} />
            ))}
        </div>
    );
}

function IssueItem({ issue }) {
    const [expanded, setExpanded] = useState(false);

    const getSeverityStyle = (sev) => {
        switch (sev) {
            case 'critical': return 'border-red-500/30 bg-red-500/5 text-red-400';
            case 'major': return 'border-orange-500/30 bg-orange-500/5 text-orange-400';
            default: return 'border-yellow-500/30 bg-yellow-500/5 text-yellow-400';
        }
    };

    return (
        <div
            className={`border rounded-xl overflow-hidden transition-all duration-200 cursor-pointer hover:bg-slate-800/50 ${expanded ? 'bg-slate-800/30' : 'bg-transparent'} border-slate-700/50`}
            onClick={() => setExpanded(!expanded)}
        >
            <div className="p-4 flex items-center gap-4">
                <div className={`p-2 rounded-lg border ${getSeverityStyle(issue.severity)}`}>
                    <AlertTriangle className="w-5 h-5" />
                </div>

                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-white truncate">{issue.message}</span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                            {issue.rule_id}
                        </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-400">
                        <FileCode2 className="w-4 h-4" />
                        <span className="truncate">{issue.file}</span>
                        <span className="text-slate-500">Line {issue.line}</span>
                    </div>
                </div>

                <div className="text-slate-500">
                    <ChevronRight className={`w-5 h-5 transition-transform duration-200 ${expanded ? 'rotate-90' : ''}`} />
                </div>
            </div>

            {expanded && (
                <div className="px-4 pb-4 pt-2 border-t border-slate-700/50 bg-slate-800/10">
                    <p className="text-sm text-slate-300 leading-relaxed">
                        <span className="font-medium text-slate-200">Recommendation: </span>
                        {getRecommendation(issue.rule_id)}
                    </p>
                </div>
            )}
        </div>
    );
}

function getRecommendation(ruleId) {
    if (ruleId.startsWith('SEC')) return 'Refactor code to remove security vulnerabilities. Do not use hardcoded secrets or unsafe functions like eval().';
    if (ruleId.startsWith('QUAL')) return 'Improve code modularity by extracting functions, adding docstrings, and reducing deep nesting.';
    if (ruleId.startsWith('PERF')) return 'Optimize loops and minimize repetitive computations inside iteration blocks.';
    return 'Review the code and apply best practices.';
}
