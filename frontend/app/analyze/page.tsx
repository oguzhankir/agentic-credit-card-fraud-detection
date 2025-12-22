"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { TransactionForm } from '@/components/features/TransactionForm';
import { ReActVisualizer } from '@/components/features/ReActVisualizer';
import { TransactionInput, AnalysisResponse, ReActStep } from '@/lib/types';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, ShieldAlert, Info, ArrowLeft, ShieldCheck, Zap, Brain } from 'lucide-react';
import { cn } from "@/lib/utils";
import { analyzeTransaction } from '@/lib/api';

export default function AnalyzePage() {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
    const [steps, setSteps] = useState<ReActStep[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [connectionId, setConnectionId] = useState<string | null>(null);
    const socketRef = React.useRef<WebSocket | null>(null);

    // WebSocket Connection Effect
    React.useEffect(() => {
        const wsUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace('http', 'ws') + '/ws';
        const ws = new WebSocket(wsUrl);
        socketRef.current = ws;

        ws.onopen = () => console.log("Connected to WebSocket");
        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'connected') setConnectionId(msg.connection_id);
                else if (msg.type === 'react_step') setSteps(prev => [...prev, msg.data]);
            } catch (e) {
                console.error("WS parse error", e);
            }
        };
        ws.onclose = () => console.log("Disconnected from WebSocket");
        return () => { if (ws.readyState === 1) ws.close(); };
    }, []);

    const handleAnalyze = async (data: TransactionInput) => {
        setIsAnalyzing(true);
        setAnalysis(null);
        setSteps([]);
        setError(null);

        const requestData = { ...data, connection_id: connectionId || undefined };

        try {
            const res = await analyzeTransaction(requestData);
            if (!connectionId || steps.length === 0) {
                if (res.react_steps) {
                    for (const step of res.react_steps) {
                        await new Promise(r => setTimeout(r, 600));
                        setSteps(prev => [...prev, step]);
                    }
                }
            }
            setAnalysis(res);
        } catch (error) {
            console.error("Analysis failed", error);
            setError("The processing engine is currently at capacity or offline. Please try again in 30 seconds.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <main className="min-h-screen bg-slate-950 text-white selection:bg-blue-500/30 overflow-x-hidden pb-20">
            {/* Background Effects */}
            <div className="fixed top-0 -left-4 w-96 h-96 bg-blue-500/10 rounded-full filter blur-[128px] pointer-events-none" />
            <div className="fixed bottom-0 -right-4 w-[600px] h-[600px] bg-purple-500/5 rounded-full filter blur-[128px] pointer-events-none" />

            <div className="container mx-auto p-6 max-w-7xl relative z-10">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6">
                    <div>
                        <Link href="/" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors mb-4">
                            <ArrowLeft className="w-4 h-4" /> Back to Home
                        </Link>
                        <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            Neural Analysis Console
                        </h1>
                        <p className="text-gray-500 mt-2 flex items-center gap-2">
                            Hybrid Engine: LLM Cognitive + ML Predictive
                            {connectionId && (
                                <Badge variant="outline" className="text-[10px] h-5 border-emerald-500/30 bg-emerald-500/10 text-emerald-400 animate-pulse">
                                    LIVE SESSION ACTIVE
                                </Badge>
                            )}
                        </p>
                    </div>

                    <div className="flex gap-4 p-1 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl">
                        <div className="px-4 py-2 text-center border-r border-white/10">
                            <div className="text-xs font-bold text-gray-500 uppercase tracking-widest">Latency</div>
                            <div className="text-lg font-mono text-blue-400">&lt;450ms</div>
                        </div>
                        <div className="px-4 py-2 text-center">
                            <div className="text-xs font-bold text-gray-500 uppercase tracking-widest">Engine</div>
                            <div className="text-lg font-mono text-purple-400">Agentic v1.2</div>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="mb-8 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-200 flex items-center gap-3 animate-in fade-in zoom-in duration-300">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                        <span className="text-sm">{error}</span>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    {/* Left Panel: Transaction Input */}
                    <div className="lg:col-span-4 space-y-8">
                        <div className="p-1 rounded-3xl bg-gradient-to-b from-white/10 to-transparent shadow-2xl">
                            <div className="p-6 rounded-[22px] bg-slate-900/90 backdrop-blur-3xl border border-white/5">
                                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                                    <Zap className="w-5 h-5 text-blue-500" />
                                    Input Parameters
                                </h3>
                                <TransactionForm onSubmit={handleAnalyze} isLoading={isAnalyzing} />
                            </div>
                        </div>

                        {/* Architecture Snippet */}
                        <Card className="p-6 bg-white/5 border-white/10 backdrop-blur-xl rounded-3xl overflow-hidden relative group">
                            <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                            <h3 className="font-bold text-sm text-gray-200 mb-4 flex items-center gap-2">
                                <ShieldCheck className="w-4 h-4 text-blue-500" />
                                Security Standards
                            </h3>
                            <div className="space-y-4">
                                <SecureItem title="Statistical Anomaly" status="Verified" color="blue" />
                                <SecureItem title="ML Prediciton (XGB/LGB)" status="Active" color="emerald" />
                                <SecureItem title="LLM Reasonable Logic" status="Optimized" color="purple" />
                            </div>
                            <Link href="/docs" className="mt-6 block text-[10px] uppercase tracking-widest font-black text-center text-gray-500 hover:text-white transition-colors">
                                View Full Protocol Documentation →
                            </Link>
                        </Card>
                    </div>

                    {/* Right Panel: Reasoning & Result */}
                    <div className="lg:col-span-8 space-y-8">
                        {/* Final Decision Overlay */}
                        {analysis && (
                            <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                                <div className={cn(
                                    "p-[1px] rounded-[32px] overflow-hidden shadow-2xl",
                                    analysis.decision.action === 'BLOCK' ? 'bg-gradient-to-r from-red-500 to-orange-500' : 'bg-gradient-to-r from-emerald-500 to-blue-500'
                                )}>
                                    <div className="bg-slate-900/95 backdrop-blur-3xl rounded-[31px] p-8">
                                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 border-b border-white/5 pb-8">
                                            <div className="flex items-center gap-6">
                                                <div className={cn(
                                                    "w-16 h-16 rounded-[22px] flex items-center justify-center shadow-inner",
                                                    analysis.decision.action === 'BLOCK' ? 'bg-red-500/20 text-red-500' : 'bg-emerald-500/20 text-emerald-500'
                                                )}>
                                                    {analysis.decision.action === 'BLOCK' ? <ShieldAlert className="w-8 h-8" /> : <CheckCircle className="w-8 h-8" />}
                                                </div>
                                                <div>
                                                    <div className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] mb-1">Verdict</div>
                                                    <h2 className={cn(
                                                        "text-4xl font-black italic tracking-tighter",
                                                        analysis.decision.action === 'BLOCK' ? 'text-red-500' : 'text-emerald-500'
                                                    )}>
                                                        {analysis.decision.action}
                                                    </h2>
                                                </div>
                                            </div>

                                            <div className="flex flex-row md:flex-col items-end gap-1 px-8 md:border-l border-white/10">
                                                <div className="flex items-baseline gap-1">
                                                    <span className={cn(
                                                        "text-5xl font-black font-mono tracking-tighter",
                                                        analysis.risk_score > 80 ? 'text-red-500' : 'text-white'
                                                    )}>
                                                        {analysis.risk_score}
                                                    </span>
                                                    <span className="text-gray-600 font-bold mb-1">/100</span>
                                                </div>
                                                <span className="text-[10px] font-black uppercase text-gray-500 tracking-widest">Aggregated Risk</span>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                                            <section>
                                                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4">Neural Synthesis</h4>
                                                <p className="text-gray-200 leading-relaxed text-sm font-medium">
                                                    {analysis.decision.reasoning}
                                                </p>
                                            </section>
                                            <section>
                                                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4">Risk Vectors</h4>
                                                <div className="flex flex-wrap gap-2">
                                                    {analysis.decision.key_factors.map((factor, idx) => (
                                                        <Badge key={idx} variant="outline" className="bg-white/5 border-white/10 text-gray-300 hover:text-white transition-colors">
                                                            {factor}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </section>
                                        </div>

                                        <div className="mt-8 pt-8 border-t border-white/5 flex items-center justify-between">
                                            <div className="flex gap-4">
                                                <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 px-3">
                                                    Precision: {analysis.decision.confidence}%
                                                </Badge>
                                                <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/20 px-3">
                                                    ML Conf: {Math.round(analysis.model_prediction.fraud_probability * 100)}%
                                                </Badge>
                                            </div>
                                            <span className="text-[10px] font-mono text-gray-600">ID: {analysis.transaction_id.slice(0, 12)}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="p-8 rounded-[32px] bg-slate-900/50 backdrop-blur-xl border border-white/5 min-h-[400px]">
                            <h3 className="text-lg font-bold mb-8 flex items-center gap-3">
                                <Brain className="w-6 h-6 text-purple-500" />
                                Agent Reasoning Process
                            </h3>
                            <ReActVisualizer steps={steps} isAnalyzing={isAnalyzing} />
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

function SecureItem({ title, status, color }: { title: string, status: string, color: 'blue' | 'emerald' | 'purple' }) {
    const colorMap = {
        blue: 'text-blue-400 bg-blue-400/10',
        emerald: 'text-emerald-400 bg-emerald-400/10',
        purple: 'text-purple-400 bg-purple-400/10'
    };
    return (
        <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/5">
            <span className="text-xs font-medium text-gray-300">{title}</span>
            <span className={cn("text-[9px] font-black uppercase px-2 py-0.5 rounded-full", colorMap[color])}>
                {status}
            </span>
        </div>
    );
}
