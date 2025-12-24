/**
 * WebSocket message types from backend
 */
export type MessageType =
    | 'connected'
    | 'thought'
    | 'action'
    | 'observation'
    | 'decision'
    | 'complete'
    | 'error';

/**
 * WebSocket message structure
 */
export interface WebSocketMessage {
    type: MessageType;
    step?: number;
    agent?: string;
    content?: string;
    tool?: string;
    metadata?: {
        llm_used?: boolean;
        tokens_used?: number;
        processing_time_ms?: number;
        tool?: string;
        tool_input?: any;
        status?: string;
    };
    // For 'decision' type in some payloads
    action?: 'APPROVE' | 'BLOCK' | 'MANUAL_REVIEW';
    reasoning?: string;
    confidence?: number;
    // For 'complete' type
    analysis?: CompleteAnalysis;
}

/**
 * Complete analysis result
 */
export interface CompleteAnalysis {
    transaction_id?: string;
    decision: {
        action: 'APPROVE' | 'BLOCK' | 'MANUAL_REVIEW';
        reasoning: string;
        confidence: number;
        key_factors: string[];
    };
    risk_score: number;
    processing_time_ms: number;
    llm_calls_made?: number;
    total_tokens_used: number;
}

/**
 * ReAct step for timeline display
 */
export interface ReActStep {
    step: number;
    type: 'THOUGHT' | 'ACTION' | 'OBSERVATION' | 'DECISION';
    agent: string;
    content: string;
    timestamp: string;
    metadata?: {
        llm_used?: boolean;
        tokens_used?: number;
        tool?: string;
        tool_input?: any;
    };
}
