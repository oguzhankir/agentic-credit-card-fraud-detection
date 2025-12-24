import { useState, useEffect, useCallback, useRef } from 'react';
import { WebSocketMessage, ReActStep, CompleteAnalysis } from '@/types/analysis';

/**
 * Custom hook for WebSocket connection to backend
 * 
 * Manages:
 * - Connection lifecycle (connect, disconnect, reconnect)
 * - Message streaming from backend
 * - Step accumulation for timeline
 * - Error handling
 * 
 * @returns WebSocket state and control functions
 */
export function useWebSocket(url: string) {
    const [isConnected, setIsConnected] = useState(false);
    const [steps, setSteps] = useState<ReActStep[]>([]);
    const [finalResult, setFinalResult] = useState<CompleteAnalysis | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

    /**
     * Connect to WebSocket server
     */
    const connect = useCallback(() => {
        try {
            if (!url) return;

            // Generate unique connection ID
            const connectionId = `conn_${Date.now()}`;
            const wsUrl = `${url}/ws/analyze/${connectionId}`;

            console.log('Connecting to WebSocket:', wsUrl);

            // Create WebSocket connection
            const ws = new WebSocket(wsUrl);

            // Connection opened
            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setError(null);
            };

            // Message received
            ws.onmessage = (event) => {
                try {
                    const message: WebSocketMessage = JSON.parse(event.data);
                    handleMessage(message);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            // Connection closed
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                // Auto-reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(connect, 3000);
            };

            // Error occurred
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                // Don't set user-facing error immediately on connection retry
                // setError('Connection error. Retrying...');
            };

            wsRef.current = ws;
        } catch (err) {
            console.error('Connection exception:', err);
            setError('Failed to connect to backend');
        }
    }, [url]);

    /**
     * Handle incoming WebSocket message
     */
    const handleMessage = (message: WebSocketMessage) => {
        // console.log('WS Message:', message.type, message);

        switch (message.type) {
            case 'connected':
                // Connection confirmed
                break;

            case 'thought':
            case 'action':
            case 'observation':
                // Add to steps timeline
                if (message.step) {
                    setSteps(prev => {
                        // Avoid duplicates
                        if (prev.some(s => s.step === message.step && s.type === message.type.toUpperCase())) {
                            return prev;
                        }
                        return [...prev, {
                            step: message.step!,
                            type: message.type.toUpperCase() as any,
                            agent: message.agent || 'unknown',
                            content: message.content || '',
                            timestamp: new Date().toISOString(),
                            metadata: message.metadata
                        }];
                    });
                }
                break;

            case 'decision':
                // Add decision step
                if (message.step) {
                    setSteps(prev => [...prev, {
                        step: message.step!,
                        type: 'DECISION',
                        agent: message.agent || 'coordinator',
                        content: `Decision: ${message.action} - ${message.reasoning}`,
                        timestamp: new Date().toISOString(),
                        metadata: message.metadata
                    }]);
                }
                break;

            case 'complete':
                // Analysis complete
                if (message.analysis) {
                    setFinalResult(message.analysis);
                    setIsAnalyzing(false);
                }
                break;

            case 'error':
                setError(message.content || 'Analysis failed');
                setIsAnalyzing(false);
                break;
        }
    };

    /**
     * Send transaction for analysis
     */
    const analyzeTransaction = useCallback((transaction: any) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            setError('Not connected to backend');
            return;
        }

        // Reset state
        setSteps([]);
        setFinalResult(null);
        setError(null);
        setIsAnalyzing(true);

        // Send transaction
        wsRef.current.send(JSON.stringify({
            action: 'analyze',
            transaction
        }));
    }, []);

    /**
     * Disconnect WebSocket
     */
    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
    }, []);

    // Auto-connect on mount
    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return {
        isConnected,
        steps,
        finalResult,
        error,
        isAnalyzing,
        analyzeTransaction,
        resetAnalysis: () => {
            setSteps([]);
            setFinalResult(null);
            setError(null);
        }
    };
}
