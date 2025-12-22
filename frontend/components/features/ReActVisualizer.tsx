import React, { useEffect, useRef } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ReActStep } from "@/lib/types";
import { Brain, Zap, Eye, CheckCircle, Search } from "lucide-react";
import { cn } from "@/lib/utils";

interface ReActVisualizerProps {
    steps: ReActStep[];
    isAnalyzing: boolean;
}

export const ReActVisualizer: React.FC<ReActVisualizerProps> = ({ steps, isAnalyzing }) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [steps]);

    const getIcon = (type: string) => {
        switch (type) {
            case 'THOUGHT': return <Brain className="w-4 h-4 text-blue-400" />;
            case 'ACTION': return <Search className="w-4 h-4 text-emerald-400" />;
            case 'OBSERVATION': return <Eye className="w-4 h-4 text-purple-400" />;
            case 'DECISION': return <CheckCircle className="w-4 h-4 text-blue-500" />;
            default: return <Zap className="w-4 h-4 text-yellow-500" />;
        }
    };

    const getColors = (type: string) => {
        switch (type) {
            case 'THOUGHT': return "border-blue-500/20 bg-blue-500/5 text-blue-100";
            case 'ACTION': return "border-emerald-500/20 bg-emerald-500/5 text-emerald-100";
            case 'OBSERVATION': return "border-purple-500/20 bg-purple-500/5 text-purple-100";
            case 'DECISION': return "border-blue-500/40 bg-blue-500/10 text-white font-bold";
            default: return "border-white/10 bg-white/5 text-gray-300";
        }
    };

    return (
        <div className="w-full space-y-8">
            <div className="space-y-6 relative before:absolute before:left-[19px] before:top-2 before:bottom-2 before:w-[2px] before:bg-gradient-to-b before:from-blue-500/50 before:via-purple-500/50 before:to-transparent">
                {steps.map((step, idx) => (
                    <div key={idx} className="relative pl-12 animate-in slide-in-from-left-4 fade-in duration-500">
                        {/* Timeline Icon */}
                        <div className={cn(
                            "absolute left-0 top-1 w-10 h-10 rounded-xl border border-white/10 flex items-center justify-center z-10 backdrop-blur-3xl shadow-2xl",
                            step.type === 'THOUGHT' ? 'bg-blue-500/20 border-blue-500/30' :
                                step.type === 'ACTION' ? 'bg-emerald-500/20 border-emerald-500/30' :
                                    step.type === 'OBSERVATION' ? 'bg-purple-500/20 border-purple-500/30' :
                                        'bg-slate-800 border-white/20'
                        )}>
                            {getIcon(step.type)}
                        </div>

                        <Card className={cn("p-5 border shadow-2xl transition-all duration-300 rounded-[20px]", getColors(step.type))}>
                            <div className="flex justify-between items-center mb-4">
                                <div className="flex gap-3 items-center">
                                    <Badge variant="outline" className="text-[9px] font-black uppercase tracking-[0.1em] border-current opacity-70">
                                        {step.type}
                                    </Badge>
                                    <span className="text-[10px] font-bold uppercase text-gray-500 tracking-wider">
                                        Agent: {step.agent}
                                    </span>
                                </div>
                                <span className="text-[10px] font-mono text-gray-600">
                                    {new Date(step.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                </span>
                            </div>

                            <div className="text-sm font-medium leading-relaxed opacity-90 whitespace-pre-wrap">
                                {step.content}
                            </div>

                            {/* Metadata Footer */}
                            <div className="mt-4 pt-4 border-t border-white/5 flex flex-wrap gap-3 items-center">
                                {step.metadata.llm_used ? (
                                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 text-[9px] font-black uppercase tracking-widest border border-blue-500/20">
                                        <Zap className="w-2.5 h-2.5" /> Cognitive
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[9px] font-black uppercase tracking-widest border border-emerald-500/20">
                                        <Search className="w-2.5 h-2.5" /> Statistical
                                    </div>
                                )}

                                {step.metadata.llm_purpose && (
                                    <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest italic opacity-50">
                                        {step.metadata.llm_purpose}
                                    </span>
                                )}

                                {step.metadata.confidence && (
                                    <Badge className="ml-auto bg-white/5 border-white/10 text-white text-[9px]">
                                        Conf: {step.metadata.confidence}%
                                    </Badge>
                                )}
                            </div>
                        </Card>
                    </div>
                ))}

                {isAnalyzing && (
                    <div className="relative pl-12 animate-pulse">
                        <div className="absolute left-[3px] top-1 w-8 h-8 rounded-lg bg-white/5 border border-dashed border-white/20 flex items-center justify-center">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping" />
                        </div>
                        <div className="p-4 rounded-[20px] border border-dashed border-white/10 bg-white/[0.02] text-gray-500 text-xs font-bold uppercase tracking-[0.2em] italic">
                            Synthesizing Neural Vectors...
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>
        </div>
    );
};
