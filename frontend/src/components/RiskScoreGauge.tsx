interface Props {
    score: number | null;
}

export function RiskScoreGauge({ score }: Props) {
    if (score === null) return null;

    // Color based on risk level
    const getColor = (score: number) => {
        if (score >= 80) return 'text-red-600';
        if (score >= 50) return 'text-orange-600';
        if (score >= 20) return 'text-yellow-600';
        return 'text-green-600';
    };

    const getLabel = (score: number) => {
        if (score >= 80) return 'CRITICAL';
        if (score >= 50) return 'HIGH';
        if (score >= 20) return 'MEDIUM';
        return 'LOW';
    };

    const circumference = 2 * Math.PI * 56; // r=56 implies C ~= 351.8
    const strokeDashoffset = circumference - ((score / 100) * circumference);

    return (
        <div className="flex flex-col items-center p-6 animate-fade-in">
            {/* Circular gauge */}
            <div className="relative w-40 h-40">
                <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 128 128">
                    {/* Background circle */}
                    <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="10"
                        fill="none"
                        className="text-gray-100"
                    />

                    {/* Progress circle */}
                    <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="10"
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        className={`transition-all duration-1000 ease-out ${getColor(score)}`}
                    />
                </svg>

                {/* Score text in center */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className={`text-4xl font-bold ${getColor(score)}`}>{score}</div>
                    <div className="text-xs text-gray-400 font-medium uppercase mt-1">Risk Score</div>
                </div>
            </div>

            {/* Label */}
            <div className={`mt-2 text-xl font-bold tracking-tight ${getColor(score)}`}>
                {getLabel(score)} RISK
            </div>
        </div>
    );
}
