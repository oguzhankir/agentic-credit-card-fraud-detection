import { CompleteAnalysis } from '@/types/analysis';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, Ban, AlertTriangle, Activity, Database, Clock } from 'lucide-react';

interface Props {
    result: CompleteAnalysis | null;
}

export function ResultCard({ result }: Props) {
    if (!result || !result.decision) return null;

    const { decision, risk_score } = result;

    // Color based on action
    const configs = {
        APPROVE: {
            style: 'bg-green-50 border-green-200',
            text: 'text-green-700',
            icon: CheckCircle2,
            title: 'Transaction Approved'
        },
        BLOCK: {
            style: 'bg-red-50 border-red-200',
            text: 'text-red-700',
            icon: Ban,
            title: 'Transaction Blocked'
        },
        MANUAL_REVIEW: {
            style: 'bg-yellow-50 border-yellow-200',
            text: 'text-yellow-700',
            icon: AlertTriangle,
            title: 'Manual Review Required'
        }
    };

    const config = configs[decision.action] || configs.MANUAL_REVIEW;
    const Icon = config.icon;

    return (
        <Card className={`border-l-4 animate-slide-up ${config.style}`}>
            <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                    <Icon className={`w-8 h-8 ${config.text}`} />
                    <div>
                        <CardTitle className={`text-xl ${config.text}`}>
                            {config.title}
                        </CardTitle>
                        <div className="text-sm text-gray-500 mt-1">
                            Confidence: <span className="font-semibold">{decision.confidence}%</span>
                        </div>
                    </div>
                </div>
            </CardHeader>

            <CardContent>
                {/* Reasoning */}
                <div className="mb-6">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Reasoning</h3>
                    <p className="text-gray-600 leading-relaxed bg-white/50 p-3 rounded-md">
                        {decision.reasoning}
                    </p>
                </div>

                {/* Key factors */}
                {decision.key_factors && decision.key_factors.length > 0 && (
                    <div className="mb-6">
                        <h3 className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Risk Factors</h3>
                        <ul className="space-y-1">
                            {decision.key_factors.map((factor, i) => (
                                <li key={i} className="text-sm flex items-center gap-2 text-gray-600">
                                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />
                                    {factor}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Stats Grid */}
                <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center p-2 bg-white/60 rounded-lg">
                        <div className="text-gray-500 flex items-center justify-center gap-1 mb-1">
                            <Activity className="w-3 h-3" /> Risk Score
                        </div>
                        <div className="font-bold text-lg">{risk_score}/100</div>
                    </div>
                    <div className="text-center p-2 bg-white/60 rounded-lg">
                        <div className="text-gray-500 flex items-center justify-center gap-1 mb-1">
                            <Clock className="w-3 h-3" /> Duration
                        </div>
                        <div className="font-bold text-lg">{result.processing_time_ms}ms</div>
                    </div>
                    <div className="text-center p-2 bg-white/60 rounded-lg">
                        <div className="text-gray-500 flex items-center justify-center gap-1 mb-1">
                            <Database className="w-3 h-3" /> Tokens
                        </div>
                        <div className="font-bold text-lg">{result.total_tokens_used || result.llm_calls_made || 0}</div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
