import React from 'react';
import { Layers, RefreshCw, Box } from 'lucide-react';

export default function MetricsPanel({ metrics, crossFile }) {
    return (
        <div className="space-y-8">

            {/* Metrics Section */}
            <div>
                <h3 className="text-lg font-medium text-white mb-4">File Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(metrics.line_counts).map(([file, lines]) => (
                        <div key={file} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                            <h4 className="font-medium text-slate-200 truncate mb-3" title={file}>{file}</h4>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-slate-400">Total Lines:</span>
                                <span className="text-white font-medium">{lines}</span>
                            </div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-slate-400">Functions:</span>
                                <span className="text-white font-medium">{metrics.function_counts[file]}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-400">Complexity:</span>
                                <span className={`font-medium ${metrics.cyclomatic_complexity[file] > 10 ? 'text-red-400' : 'text-green-400'}`}>
                                    {metrics.cyclomatic_complexity[file]}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Cross File Section */}
            <div>
                <h3 className="text-lg font-medium text-white mb-4">Cross-File Analysis</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <CrossFileCard
                        title="Circular Imports"
                        items={crossFile.circular_imports}
                        icon={<RefreshCw className="w-5 h-5 text-orange-400" />}
                    />
                    <CrossFileCard
                        title="Duplicate Classes"
                        items={crossFile.duplicate_classes}
                        icon={<Layers className="w-5 h-5 text-blue-400" />}
                    />
                </div>
            </div>

        </div>
    );
}

function CrossFileCard({ title, items, icon }) {
    return (
        <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-5">
            <div className="flex items-center gap-3 mb-4">
                {icon}
                <h4 className="font-medium text-white">{title}</h4>
                <span className="ml-auto bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded-full">{items.length}</span>
            </div>

            {items.length === 0 ? (
                <p className="text-sm text-slate-400 italic">No issues detected.</p>
            ) : (
                <ul className="space-y-2">
                    {items.map((item, idx) => (
                        <li key={idx} className="text-sm text-slate-300 flex items-start gap-2 bg-slate-800/80 p-2 rounded">
                            <Box className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" />
                            <span>{item}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
