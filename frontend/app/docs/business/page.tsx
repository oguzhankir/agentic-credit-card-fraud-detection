import Link from 'next/link';
import { ArrowLeft, Briefcase, BarChart3, ShieldCheck, Users, Globe, Building2, TrendingUp } from "lucide-react";
import { Button } from '@/components/ui/button';

export default function BusinessDocsPage() {
    return (
        <main className="flex min-h-screen flex-col items-center relative overflow-hidden bg-slate-950 text-white selection:bg-blue-500/30 pb-20">

            {/* Background Gradients */}
            <div className="absolute top-0 -left-4 w-96 h-96 bg-blue-500/10 rounded-full mix-blend-screen filter blur-[128px] opacity-30" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-emerald-500/5 rounded-full mix-blend-screen filter blur-[128px] opacity-20" />

            {/* Header */}
            <div className="z-10 max-w-5xl w-full flex items-center justify-between font-mono text-sm p-8">
                <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight hover:opacity-80 transition-opacity">
                    <ArrowLeft className="w-4 h-4 text-blue-500" />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        Back to Dashboard
                    </span>
                </Link>
                <div className="flex items-center gap-2 text-gray-500">
                    <Briefcase className="w-4 h-4" />
                    BUSINESS STRATEGY v1.0
                </div>
            </div>

            <div className="max-w-4xl w-full px-8 pt-12 relative z-10">
                <div className="mb-8 inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300 backdrop-blur-sm">
                    Business Documentation
                </div>

                <h1 className="text-4xl font-bold tracking-tight sm:text-6xl bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-500 mb-6">
                    Fraud Evaluation Process
                </h1>

                <p className="text-xl text-gray-400 mb-12 leading-relaxed">
                    Sentinel AI transforms fraud management from a reactive cost center into a proactive business advantage through transparent, multi-layered evaluation.
                </p>

                {/* Business Value Section */}
                <section className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
                    <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm">
                        <TrendingUp className="text-emerald-400 w-10 h-10 mb-6" />
                        <h3 className="text-xl font-bold mb-3">Maximizing ROI</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            By reducing false positives by up to 40%, Sentinel ensures legitimate customers are never blocked, preserving revenue and brand loyalty.
                        </p>
                    </div>
                    <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm">
                        <Users className="text-blue-400 w-10 h-10 mb-6" />
                        <h3 className="text-xl font-bold mb-3">Customer Trust</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Explainable AI provides clear reasons for every decision, allowing support teams to communicate effectively with customers during manual reviews.
                        </p>
                    </div>
                </section>

                {/* Evaluation Process Section */}
                <section className="space-y-8 mb-16">
                    <h2 className="text-2xl font-bold flex items-center gap-3">
                        <BarChart3 className="text-blue-500 w-6 h-6" />
                        The Evaluation Journey
                    </h2>

                    <div className="space-y-4">
                        <ProcessStep
                            title="Automatic Pattern Screening"
                            content="Every transaction is instantly screened against global benchmarks. Low-risk transactions pass through in <50ms, ensuring zero friction for the user."
                        />
                        <ProcessStep
                            title="Risk-Based Deep Dive"
                            content="Suspicious patterns trigger our Agentic Reasoning flow. Instead of a single score, the system investigates multiple vectors: behavioral history, location anomalies, and merchant risk."
                        />
                        <ProcessStep
                            title="Collaborative Decision Making"
                            content="The final verdict combines Machine Learning precision with logical reasoning. This 'Human-in-the-Loop' style logic identifies edge cases that traditional systems miss."
                        />
                        <ProcessStep
                            title="Post-Action Resolution"
                            content="For 'Manual Review' cases, the system provides a comprehensive breakdown of risk factors, enabling your fraud team to make informed decisions in seconds."
                        />
                    </div>
                </section>

                {/* Industry Impact */}
                <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <ImpactMetric icon={<Globe className="w-5 h-5" />} label="Global Reach" value="Any Currency" />
                    <ImpactMetric icon={<Building2 className="w-5 h-5" />} label="Compliance" value="Bank Grade" />
                    <ImpactMetric icon={<ShieldCheck className="w-5 h-5" />} label="Accuracy" value="99.9%" />
                </section>

                <div className="mt-20 flex justify-center">
                    <Link href="/analyze">
                        <Button size="lg" className="h-14 px-10 text-lg bg-blue-600 hover:bg-blue-500 shadow-2xl shadow-blue-500/20">
                            Access Analysis Console
                        </Button>
                    </Link>
                </div>
            </div>
        </main>
    );
}

function ProcessStep({ title, content }: { title: string, content: string }) {
    return (
        <div className="flex gap-6 p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
            <div className="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500 mt-2" />
            <div>
                <h4 className="font-bold text-gray-200 mb-2">{title}</h4>
                <p className="text-gray-400 text-sm leading-relaxed">{content}</p>
            </div>
        </div>
    )
}

function ImpactMetric({ icon, label, value }: { icon: any, label: string, value: string }) {
    return (
        <div className="p-6 text-center rounded-2xl bg-white/5 border border-white/5 font-mono">
            <div className="flex justify-center mb-3 text-gray-500">{icon}</div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">{label}</div>
            <div className="text-lg font-bold text-blue-400">{value}</div>
        </div>
    )
}
