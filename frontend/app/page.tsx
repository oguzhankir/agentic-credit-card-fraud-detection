import Link from 'next/link';
import { ArrowRight, ShieldCheck, Activity, Brain } from "lucide-react";
import { Button } from '@/components/ui/button';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center relative overflow-hidden bg-slate-950 text-white selection:bg-blue-500/30">

      {/* Background Gradients */}
      <div className="absolute top-0 -left-4 w-96 h-96 bg-blue-500/20 rounded-full mix-blend-screen filter blur-[128px] opacity-50 animate-pulse" />
      <div className="absolute bottom-0 -right-4 w-96 h-96 bg-purple-500/10 rounded-full mix-blend-screen filter blur-[128px] opacity-50" />

      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex absolute top-0 p-8">
        <div className="flex items-center gap-2 font-semibold tracking-tight">
          <ShieldCheck className="w-5 h-5 text-blue-500" />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Sentinel AI
          </span>
        </div>
        <div className="flex gap-4 text-gray-400">
          <Link href="#" className="hover:text-white transition-colors">Documentation</Link>
          <Link href="#" className="hover:text-white transition-colors">API Reference</Link>
        </div>
      </div>

      <div className="relative flex place-items-center flex-col text-center px-4">
        <div className="mb-4 inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300 backdrop-blur-sm">
          <span className="flex h-2 w-2 rounded-full bg-blue-400 mr-2 animate-pulse"></span>
          v1.0 Router Live
        </div>

        <h1 className="text-5xl font-bold tracking-tight sm:text-7xl bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-gray-500 pb-2">
          Autonomous Fraud Defense
        </h1>

        <p className="mt-8 text-lg leading-8 text-gray-400 max-w-2xl mx-auto">
          A hybrid agentic architecture combining the reasoning capabilities of LLMs with the statistical precision of XGBoost.
          Start analyzing transactions in real-time.
        </p>

        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link href="/analyze">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20">
              Launch Console <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
          <Link href="docs/business_justification.md" target="_blank">
            <Button variant="ghost" className="text-gray-300 hover:text-white hover:bg-white/5">
              Architecture Docs
            </Button>
          </Link>
        </div>
      </div>

      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full px-8">
        <FeatureCard
          icon={<Brain className="w-8 h-8 text-blue-400" />}
          title="Cognitive Reasoning"
          description="LLM agents interpret anomalies in business context, providing explainable decisions rather than black-box scores."
        />
        <FeatureCard
          icon={<Activity className="w-8 h-8 text-emerald-400" />}
          title="Statistical Precision"
          description="Ensemble models (XGBoost, LightGBM) handle high-velocity calculations with <50ms latency."
        />
        <FeatureCard
          icon={<ShieldCheck className="w-8 h-8 text-purple-400" />}
          title="Enterprise Ready"
          description="Full fault tolerance with fallback mechanisms, assuring 99.99% availability even during API outages."
        />
      </div>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: any, title: string, description: string }) {
  return (
    <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:bg-white/10 backdrop-blur-sm">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-bold mb-2 text-gray-200">{title}</h3>
      <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
    </div>
  )
}
