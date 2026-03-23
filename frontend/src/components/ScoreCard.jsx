import React from 'react';
import { ShieldCheck, Crosshair, Cpu } from 'lucide-react';

export default function ScoreCard({ summary }) {
    const getGradeColor = (grade) => {
        switch (grade) {
            case 'A': return 'text-green-400 bg-green-400/10 border-green-400/20';
            case 'B': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
            case 'C': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
            case 'D': return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
            case 'F': return 'text-red-400 bg-red-400/10 border-red-400/20';
            default: return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
        }
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Overall Grade */}
            <div className={`p-6 rounded-2xl border flex flex-col items-center justify-center ${getGradeColor(summary.overall_grade)}`}>
                <p className="text-sm uppercase tracking-wider font-semibold opacity-80 mb-2">Overall Grade</p>
                <h2 className="text-6xl font-black drop-shadow-md">{summary.overall_grade}</h2>
                <p className="mt-2 text-xs opacity-70">Analyzed {summary.total_files_reviewed} files</p>
            </div>

            {/* Sub Scores */}
            <ScoreMetric
                title="Security"
                score={summary.security_score}
                icon={<ShieldCheck className="w-5 h-5" />}
                colorClass="text-emerald-400"
            />
            <ScoreMetric
                title="Code Quality"
                score={summary.code_quality_score}
                icon={<Crosshair className="w-5 h-5" />}
                colorClass="text-blue-400"
            />
            <ScoreMetric
                title="Maintainability"
                score={summary.maintainability_score}
                icon={<Cpu className="w-5 h-5" />}
                colorClass="text-purple-400"
            />
        </div>
    );
}

function ScoreMetric({ title, score, icon, colorClass }) {
    const percentage = (score / 10) * 100;

    return (
        <div className="bg-surface p-6 rounded-2xl border border-slate-700/50 flex flex-col justify-between hover:border-slate-600 transition-colors">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-slate-300 font-medium">{title}</h3>
                <div className={`p-2 rounded-lg bg-slate-800 border border-slate-700 ${colorClass}`}>
                    {icon}
                </div>
            </div>

            <div>
                <div className="flex items-end gap-2 mb-2">
                    <span className="text-3xl font-bold text-white">{score}</span>
                    <span className="text-slate-500 font-medium mb-1">/ 10</span>
                </div>

                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                        className={`h-full rounded-full transition-all duration-1000 ease-out ${score >= 8 ? 'bg-green-500' : score >= 5 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                        style={{ width: `${percentage}%` }}
                    />
                </div>
            </div>
        </div>
    );
}
