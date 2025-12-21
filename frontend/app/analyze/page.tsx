"use client";

import React, { useState } from 'react';
import { TransactionForm } from '@/components/features/TransactionForm';
import { ReActVisualizer } from '@/components/features/ReActVisualizer';
import { TransactionInput, AnalysisResponse, ReActStep } from '@/lib/types';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, ShieldAlert, Info } from 'lucide-react';
import { cn } from "@/lib/utils";
import { analyzeTransaction } from '@/lib/api';

export default function AnalyzePage() {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
    const [steps, setSteps] = useState<ReActStep[]>([]);
    const [error, setError] = useState<string | null>(null);

    const handleAnalyze = async (data: TransactionInput) => {
        setIsAnalyzing(true);
        setAnalysis(null);
        setSteps([]);
        setError(null);

        try {
            // 1. Try Real API
            try {
                const res = await analyzeTransaction(data);

                if (res.react_steps) {
                    for (const step of res.react_steps) {
                        await new Promise(r => setTimeout(r, 600)); // Faster step replay
                        setSteps(prev => [...prev, step]);
                    }
                }
                setAnalysis(res);
                return;
            } catch (apiErr) {
                console.warn("API unavailable, falling back to Demo Mode", apiErr);
                setError("Backend unavailable. Switching to Demo Mode (Offline).");
            }

            // 2. Fallback to Demo Mode
            const mockRes = await fetch('/mock-data/sample_analysis_1.json').then(r => r.json());

            if (mockRes.react_steps) {
                for (const step of mockRes.react_steps) {
                    await new Promise(r => setTimeout(r, 600));
                    setSteps(prev => [...prev, step]);
                }
            }
            setAnalysis(mockRes);

        } catch (error) {
            console.error("Analysis failed", error);
            setError("Analysis failed completely. Please check console.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="container mx-auto p-6 max-w-7xl min-h-screen bg-gray-50/50">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Fraud Detection Agent</h1>
                <p className="text-gray-500 mt-2">Hybrid AI Architecture: LLM Reasoning + ML Precision</p>
            </div>

            {error && (
                <div className="mb-6 p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Panel: Input */}
                <div className="lg:col-span-4 space-y-6">
                    <TransactionForm onSubmit={handleAnalyze} isLoading={isAnalyzing} />

                    {/* Guidelines Card */}
                    <Card className="p-6 bg-white shadow-sm border-gray-100">
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <Info className="w-4 h-4 text-blue-500" />
                            How it works
                        </h3>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li className="flex gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5" />
                                Agent plans investigation strategy
                            </li>
                            <li className="flex gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-1.5" />
                                Python calculates statistical usage
                            </li>
                            <li className="flex gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1.5" />
                                ML Models predict probability
                            </li>
                            <li className="flex gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5" />
                                LLM makes final decision
                            </li>
                        </ul>
                    </Card>
                </div>

                {/* Right Panel: Visualization */}
                <div className="lg:col-span-8 space-y-6">

                    {/* Status / Result Card */}
                    {analysis && (
                        <div className="animate-in fade-in slide-in-from-top-4 duration-500">
                            <Card className={cn("overflow-hidden border-0 shadow-lg",
                                analysis.decision.action === 'BLOCK' ? 'ring-1 ring-red-200' : 'ring-1 ring-green-200'
                            )}>
                                {/* Header Banner */}
                                <div className={cn("p-4 px-6 flex items-center justify-between",
                                    analysis.decision.action === 'BLOCK' ? 'bg-red-50' : 'bg-green-50'
                                )}>
                                    <div className="flex items-center gap-3">
                                        {analysis.decision.action === 'BLOCK'
                                            ? <ShieldAlert className="w-8 h-8 text-red-600" />
                                            : <CheckCircle className="w-8 h-8 text-green-600" />
                                        }
                                        <div>
                                            <h2 className={cn("text-xl font-bold",
                                                analysis.decision.action === 'BLOCK' ? "text-red-900" : "text-green-900"
                                            )}>
                                                {analysis.decision.action}
                                            </h2>
                                        </div>
                                    </div>

                                    <div className="text-right">
                                        <div className={cn("text-3xl font-black",
                                            analysis.risk_score > 80 ? 'text-red-600' : 'text-gray-900'
                                        )}>
                                            {analysis.risk_score}
                                            <span className="text-base font-normal text-gray-400 ml-1">/100</span>
                                        </div>
                                        <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">Risk Score</div>
                                    </div>
                                </div>

                                {/* Body */}
                                <div className="p-6 bg-white">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                        <div>
                                            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Reasoning</h4>
                                            <p className="text-gray-800 leading-relaxed font-medium">
                                                {analysis.decision.reasoning}
                                            </p>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Key Factors</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {analysis.decision.key_factors.map((flag, idx) => (
                                                    <Badge key={idx} variant="secondary" className="bg-gray-100 text-gray-700 hover:bg-gray-200">
                                                        {flag}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4 pt-4 border-t border-gray-100">
                                        <div className="group relative cursor-help">
                                            <Badge variant="outline" className="pl-1 pr-3 py-1 gap-1.5 border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors">
                                                <Info className="w-3.5 h-3.5" />
                                                Confidence: {analysis.decision.confidence}%
                                            </Badge>
                                            {/* Simple Tooltip */}
                                            <div className="absolute bottom-full left-0 mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 shadow-xl z-50">
                                                Based on agreement between ML models (XGBoost, RF) and logical consistency of anomalies detected. High agreement = High confidence.
                                            </div>
                                        </div>

                                        <span className="text-xs text-gray-400">
                                            Analysis ID: {analysis.transaction_id.slice(0, 8)}...
                                        </span>
                                    </div>
                                </div>
                            </Card>
                        </div>
                    )}

                    {/* ReAct Visualizer */}
                    <ReActVisualizer steps={steps} isAnalyzing={isAnalyzing} />
                </div>
            </div>
        </div>
    );
}
