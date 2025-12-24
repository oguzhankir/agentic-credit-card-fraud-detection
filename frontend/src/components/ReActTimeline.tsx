import { ReActStep } from '@/types/analysis';
import { Brain, Hammer, Eye, ShieldCheck, Loader2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

interface Props {
    steps: ReActStep[];
    isAnalyzing: boolean;
}

export function ReActTimeline({ steps, isAnalyzing }: Props) {
    const endRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [steps]);

    return (
        <div className="space-y-4">
            {/* Timeline container with connector lines */}
            <div className="relative pl-4">
                {/* Vertical line connector */}
                {steps.length > 0 && (
                    <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />
                )}

                {/* Steps */}
                <div className="space-y-6">
                    {steps.map((step, index) => (
                        <TimelineStep
                            key={step.step}
                            step={step}
                            isLast={index === steps.length - 1}
                        />
                    ))}
                </div>

                {/* Loading indicator if analyzing */}
                {isAnalyzing && (
                    <div className="flex items-center gap-3 p-4 mt-4 animate-fade-in">
                        <div className="relative z-10 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                            <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                        </div>
                        <span className="text-gray-500 text-sm">Agents working...</span>
                    </div>
                )}

                <div ref={endRef} />
            </div>
        </div>
    );
}

function TimelineStep({ step, isLast }: { step: ReActStep; isLast: boolean }) {
    // Different colors and icons for different step types
    const config = {
        THOUGHT: {
            color: 'bg-blue-100 text-blue-600 border-blue-200',
            icon: Brain,
            label: 'Thinking'
        },
        ACTION: {
            color: 'bg-orange-100 text-orange-600 border-orange-200',
            icon: Hammer,
            label: 'Action'
        },
        OBSERVATION: {
            color: 'bg-purple-100 text-purple-600 border-purple-200',
            icon: Eye,
            label: 'Observation'
        },
        DECISION: {
            color: 'bg-green-100 text-green-600 border-green-200',
            icon: ShieldCheck,
            label: 'Decision'
        }
    };

    const { color, icon: Icon, label } = config[step.type] || config.THOUGHT;

    return (
        <div className="relative flex gap-4 animate-fade-in group">
            {/* Icon/dot */}
            <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center border-2 shadow-sm ${color} transition-transform group-hover:scale-110`}>
                <Icon className="w-4 h-4" />
            </div>

            {/* Content */}
            <Card className="flex-1 p-4 shadow-sm border-gray-100 hover:shadow-md transition-shadow overflow-hidden">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${color.split(' ')[0]} ${color.split(' ')[1]}`}>
                            {step.type}
                        </span>
                        <span className="text-xs text-gray-500 font-mono">
                            {step.agent.replace('_', ' ')}
                        </span>
                    </div>
                    <span className="text-xs text-gray-400">
                        {new Date(step.timestamp).toLocaleTimeString()}
                    </span>
                </div>

                <div className="text-sm text-gray-700 font-sans prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1">
                    <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                        {step.content}
                    </ReactMarkdown>
                </div>

                {/* Metadata */}
                {(step.metadata?.llm_used || step.metadata?.tokens_used || step.metadata?.tool) && (
                    <div className="flex gap-4 mt-3 pt-3 border-t border-gray-50 text-xs text-gray-400">
                        {step.metadata.llm_used && (
                            <span className="flex items-center gap-1">
                                <Brain className="w-3 h-3" /> LLM Used
                            </span>
                        )}
                        {step.metadata.tokens_used && (
                            <span>Tokens: {step.metadata.tokens_used}</span>
                        )}
                        {step.metadata?.tool && (
                            <span className="font-mono bg-gray-100 px-1 rounded">
                                Tool: {step.metadata.tool}
                            </span>
                        )}
                    </div>
                )}
            </Card>
        </div>
    );
}
