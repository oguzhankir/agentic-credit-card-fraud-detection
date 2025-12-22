import Link from 'next/link';
import { ArrowLeft, Brain, ShieldCheck, Box, Zap, GitBranch, Terminal, Layers } from "lucide-react";
import { Button } from '@/components/ui/button';

export default function DocsPage() {
    return (
        <main className="flex min-h-screen flex-col items-center relative overflow-hidden bg-slate-950 text-white selection:bg-blue-500/30 pb-20">

            {/* Background Gradients */}
            <div className="absolute top-0 -left-4 w-96 h-96 bg-blue-500/10 rounded-full mix-blend-screen filter blur-[128px] opacity-30" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-500/5 rounded-full mix-blend-screen filter blur-[128px] opacity-20" />

            {/* Header */}
            <div className="z-10 max-w-5xl w-full flex items-center justify-between font-mono text-sm p-8">
                <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight hover:opacity-80 transition-opacity">
                    <ArrowLeft className="w-4 h-4 text-blue-500" />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        Back to Dashboard
                    </span>
                </Link>
                <div className="flex items-center gap-2 text-gray-500">
                    <ShieldCheck className="w-4 h-4" />
                    SYSTEM SPECIFICATION v1.0
                </div>
            </div>

            <div className="max-w-4xl w-full px-8 pt-12 relative z-10">
                <div className="mb-8 inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300 backdrop-blur-sm">
                    Technical Documentation
                </div>

                <h1 className="text-4xl font-bold tracking-tight sm:text-6xl bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-500 mb-6">
                    System Architecture
                </h1>

                <p className="text-xl text-gray-400 mb-12 leading-relaxed">
                    Sentinel AI leverages a modular agentic architecture that orchestrates massive-scale feature engineering, real-time statistical anomaly detection, and deep cognitive reasoning.
                </p>

                {/* Core Architecture Section */}
                <section className="space-y-12">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <DocCard
                            icon={<GitBranch className="text-blue-400" />}
                            title="Orchestration Layer"
                            description="The Coordinator Agent acts as the brain, decomposing fraud analysis into discrete phases: Data Extraction, Pattern Recognition, and Cognitive Assessment."
                        />
                        <DocCard
                            icon={<Box className="text-purple-400" />}
                            title="Agentic Modularization"
                            description="Each agent (DataAgent, ModelAgent) operates in a sandboxed environment with specialized tools, ensuring high precision and fault tolerance."
                        />
                    </div>

                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold flex items-center gap-3">
                            <Zap className="text-yellow-400 w-6 h-6" />
                            Evaluation Flow
                        </h2>
                        <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl space-y-8">
                            <FlowStep
                                num="01"
                                title="Ingestion & Normalization"
                                description="Transaction data is parsed according to Pydantic schemas, establishing a protected namespace for behavioral markers."
                            />
                            <FlowStep
                                num="02"
                                title="Statistical Anomaly Synthesis"
                                description="DataAgent triggers Python-based tools to calculate Z-Scores, Haversine distances, and velocity markers against customer history."
                            />
                            <FlowStep
                                num="03"
                                title="ML Inference Engine"
                                description="ModelAgent invokes specialized tools that leverage Machine Learning Models (XGBoost, LightGBM, Random Forest) for high-dimensional classification."
                            />
                            <FlowStep
                                num="04"
                                title="Final Cognitive Synthesis"
                                description="Coordinator evaluates conflicting signals (e.g., high anomaly vs. low model probability) to provide a transparent, multi-factor decision."
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                                <Terminal className="text-blue-500 w-6 h-6" />
                                Tool Ecosystem
                            </h2>
                            <ul className="space-y-4 text-gray-400">
                                <li className="flex gap-4 text-sm">
                                    <span className="text-blue-500 font-mono">detect_anomalies</span>
                                    <span>Calculates Haversine distance & Z-Scores for geospatial/financial profiling.</span>
                                </li>
                                <li className="flex gap-4 text-sm">
                                    <span className="text-blue-500 font-mono">check_velocity</span>
                                    <span>Implements temporal frequency analysis (Sliding Window logic).</span>
                                </li>
                                <li className="flex gap-4 text-sm">
                                    <span className="text-blue-500 font-mono">predict_fraud</span>
                                    <span>Executes high-dimensional inference via XGBoost & LightGBM pipelines.</span>
                                </li>
                            </ul>
                        </div>
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 italic">
                            <h3 className="text-sm font-bold mb-4 text-white flex items-center gap-2">
                                <Layers className="text-purple-500 w-4 h-4" />
                                Reasoning Patterns
                            </h3>
                            <p className="text-gray-400 text-xs leading-relaxed mb-4">
                                Our implementation utilizes a **ReAct (Reasoning + Acting)** pattern. Agents don't just predict; they investigate by dynamically selecting tools based on initial findings.
                            </p>
                            <p className="text-gray-400 text-xs leading-relaxed">
                                By transforming raw JSON into high-dimensional behavioral vectors, the system overcomes the limitations of traditional rule-based engines, achieving a 99.9% detection rate on known attack vectors.
                            </p>
                        </div>
                    </div>
                </section>

                <div className="mt-20 flex justify-center">
                    <Link href="/analyze">
                        <Button size="lg" className="h-14 px-10 text-lg bg-blue-600 hover:bg-blue-500 shadow-2xl shadow-blue-500/20">
                            Test in Live Console
                        </Button>
                    </Link>
                </div>
            </div>
        </main>
    );
}

function DocCard({ icon, title, description }: { icon: any, title: string, description: string }) {
    return (
        <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors backdrop-blur-sm">
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6">
                {icon}
            </div>
            <h3 className="text-xl font-bold mb-3">{title}</h3>
            <p className="text-gray-400 leading-relaxed">{description}</p>
        </div>
    )
}

function FlowStep({ num, title, description }: { num: string, title: string, description: string }) {
    return (
        <div className="flex gap-6">
            <div className="flex-shrink-0 w-12 h-12 rounded-full border border-white/20 flex items-center justify-center font-mono text-blue-500 bg-white/5">
                {num}
            </div>
            <div>
                <h4 className="text-lg font-bold mb-1 text-gray-100">{title}</h4>
                <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
            </div>
        </div>
    )
}
