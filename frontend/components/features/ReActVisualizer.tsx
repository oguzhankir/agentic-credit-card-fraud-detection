import React, { useEffect, useRef } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ReActStep } from "@/lib/types";
import { Brain, Zap, Eye, CheckCircle, StopCircle, AlertTriangle } from "lucide-react";
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
            case 'THOUGHT': return <Brain className="w-5 h-5 text-blue-500" />;
            case 'ACTION': return <Zap className="w-5 h-5 text-green-500" />;
            case 'OBSERVATION': return <Eye className="w-5 h-5 text-yellow-500" />;
            case 'DECISION': return <CheckCircle className="w-5 h-5 text-red-500" />; // Dynamic based on action ideally
            default: return <Brain className="w-5 h-5" />;
        }
    };

    const getBgColor = (type: string) => {
        switch (type) {
            case 'THOUGHT': return "bg-blue-50 border-blue-100";
            case 'ACTION': return "bg-green-50 border-green-100";
            case 'OBSERVATION': return "bg-yellow-50 border-yellow-100";
            case 'DECISION': return "bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200";
            default: return "bg-white";
        }
    };

    return (
        <div className="w-full space-y-4 p-4">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Brain className="w-6 h-6" />
                Agent Reasoning Process
            </h2>

            <div className="space-y-4 relative before:absolute before:left-8 before:top-4 before:bottom-4 before:w-0.5 before:bg-gray-200">
                {steps.map((step, idx) => (
                    <div key={idx} className="relative pl-16 animate-in slide-in-from-bottom-2 fade-in duration-300">
                        {/* Timeline Icon */}
                        <div className={`absolute left-5 top-4 w-7 h-7 rounded-full bg-white border-2 flex items-center justify-center z-10
              ${step.type === 'THOUGHT' ? 'border-blue-500' :
                                step.type === 'ACTION' ? 'border-green-500' :
                                    step.type === 'OBSERVATION' ? 'border-yellow-500' : 'border-red-500'}`}>
                            {getIcon(step.type)}
                        </div>

                        <Card className={cn("p-4 border shadow-sm transition-all hover:shadow-md", getBgColor(step.type))}>
                            <div className="flex justify-between items-start mb-2">
                                <div className="flex gap-2 items-center">
                                    <Badge variant={step.type === 'DECISION' ? "destructive" : "outline"} className="font-bold">
                                        {step.type}
                                    </Badge>
                                    <span className="text-xs text-muted-foreground uppercase tracking-wider">{step.agent}</span>
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    {new Date(step.timestamp).toLocaleTimeString()}
                                </span>
                            </div>

                            <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                                {step.content}
                            </div>

                            {/* Metadata Footer */}
                            <div className="mt-3 pt-3 border-t border-black/5 flex gap-2 text-xs text-gray-500">
                                {step.metadata.llm_used ? (
                                    <Badge variant="secondary" className="text-[10px] h-5 bg-blue-100 text-blue-700 hover:bg-blue-100">
                                        🤖 LLM: {step.metadata.llm_purpose}
                                    </Badge>
                                ) : (
                                    <Badge variant="secondary" className="text-[10px] h-5 bg-green-100 text-green-700 hover:bg-green-100">
                                        ⚙️ Python Execution
                                    </Badge>
                                )}
                                {step.metadata.confidence && (
                                    <span className="ml-auto font-medium">Confidence: {step.metadata.confidence}%</span>
                                )}
                            </div>
                        </Card>
                    </div>
                ))}

                {isAnalyzing && (
                    <div className="relative pl-16 animate-pulse">
                        <div className="absolute left-6 top-4 w-5 h-5 rounded-full bg-gray-300 z-10" />
                        <div className="p-4 rounded-lg border border-dashed bg-gray-50 text-gray-400 text-sm">
                            Agent is thinking...
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>
        </div>
    );
};
