'use client';

import { useWebSocket } from '@/hooks/useWebSocket';
import { useTransactionForm } from '@/hooks/useTransactionForm';
import { TransactionForm } from '@/components/TransactionForm';
import { ReActTimeline } from '@/components/ReActTimeline';
import { ResultCard } from '@/components/ResultCard';
import { RiskScoreGauge } from '@/components/RiskScoreGauge';
import { ShieldAlert, Info } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function Home() {
  // WebSocket connection
  const {
    isConnected,
    steps,
    finalResult,
    error,
    isAnalyzing,
    analyzeTransaction,
    resetAnalysis
  } = useWebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000');

  // Form state
  const {
    formData,
    errors,
    updateField,
    generateRandomTransaction,
    validate,
    resetForm
  } = useTransactionForm();

  /**
   * Handle form submission
   */
  const handleAnalyze = () => {
    if (!validate()) return;

    // Reset previous analysis
    resetAnalysis();

    // Send to backend
    analyzeTransaction(formData);
  };

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50 backdrop-blur-sm bg-white/80">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-2 rounded-lg">
              <ShieldAlert className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">FraudGuard AI</h1>
              <p className="text-xs text-gray-500">Agentic Analysis Dashboard</p>
            </div>
          </div>

          {/* Connection status */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${isConnected ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-red-100 text-red-700 border border-red-200'
            }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            {isConnected ? 'System Online' : 'System Offline'}
          </div>
        </div>
      </header>

      {/* Main content - 2 column layout */}
      <main className="container mx-auto px-4 py-8">
        {!isConnected && (
          <Alert variant="destructive" className="mb-6">
            <ShieldAlert className="h-4 w-4" />
            <AlertTitle>Connection Error</AlertTitle>
            <AlertDescription>
              Cannot connect to backend server. Please verify the backend is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
          {/* Left column: Form (5 Cols) */}
          <div className="xl:col-span-5 space-y-6">
            <TransactionForm
              formData={formData}
              errors={errors}
              isAnalyzing={isAnalyzing}
              onFieldChange={updateField}
              onGenerate={generateRandomTransaction}
              onSubmit={handleAnalyze}
              onReset={resetForm}
            />
          </div>

          {/* Right column: Analysis stream (7 Cols) */}
          <div className="xl:col-span-7 space-y-6">

            {/* Top Row: Risk Gauge & Result */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Gauge */}
              <div className="bg-white rounded-lg shadow-sm border p-4 flex flex-col justify-center min-h-[200px]">
                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide text-center mb-2">Risk Assessment</h2>
                {finalResult ? (
                  <RiskScoreGauge score={finalResult.risk_score} />
                ) : (
                  <div className="text-center text-gray-400 text-sm flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-gray-100 mb-3" />
                    Waiting for analysis...
                  </div>
                )}
              </div>

              {/* Result Placeholder or Card */}
              <div className="min-h-[200px]">
                {finalResult ? (
                  <ResultCard result={finalResult} />
                ) : (
                  <div className="h-full bg-white rounded-lg shadow-sm border p-8 flex flex-col items-center justify-center text-center text-gray-400 border-dashed">
                    <Info className="w-8 h-8 mb-2 opacity-50" />
                    <p>Final decision will appear here</p>
                  </div>
                )}
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-lg shadow-sm border p-6 min-h-[500px]">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-bold text-gray-900">Agent Reasoning Timeline</h2>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">Live Stream</span>
              </div>

              {steps.length === 0 && !isAnalyzing && (
                <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                  <div className="w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center mb-4">
                    <ShieldAlert className="w-8 h-8 text-blue-200" />
                  </div>
                  <p>Submit a transaction to start the investigation.</p>
                </div>
              )}

              <ReActTimeline steps={steps} isAnalyzing={isAnalyzing} />
            </div>

            {/* Error display */}
            {error && (
              <Alert variant="destructive">
                <AlertTitle>Analysis Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
