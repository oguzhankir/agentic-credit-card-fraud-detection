export interface TransactionInput {
    transaction_id?: string;
    amount: number;
    merchant: string;
    category: TransactionCategory;
    time: string;
    location: Location;
    customer_id: string;
    customer_history?: CustomerHistory;
    connection_id?: string;

    // Raw Fields for Simulation
    cc_num?: string;
    first?: string;
    last?: string;
    gender?: string;
    street?: string;
    zip?: string | number;
    city?: string;
    state?: string;
    job?: string;
    dob?: string;
    trans_num?: string;
    unix_time?: number;
    merch_lat?: number;
    merch_long?: number;
}

export interface Location {
    lat: number;
    long: number;
    distance_from_home: number;
    city?: string;
    state?: string;
}

export interface CustomerHistory {
    avg_amount: number;
    std_amount?: number;
    usual_hours: number[];
    transaction_count: number;
    first_transaction_date?: string;
}

export type TransactionCategory =
    | 'grocery_pos'
    | 'gas_transport'
    | 'shopping_net'
    | 'shopping_pos'
    | 'food_dining'
    | 'entertainment'
    | 'health_fitness'
    | 'travel'
    | 'personal_care'
    | 'kids_pets'
    | 'home'
    | 'misc_net'
    | 'misc_pos';

export interface AnalysisResponse {
    transaction_id: string;
    analysis_timestamp: string;
    decision: Decision;
    risk_score: number;
    model_prediction: ModelPrediction;
    anomalies: Anomalies;
    react_steps: ReActStep[];
    recommended_actions: string[];
    processing_time_ms: number;
    llm_calls_made: number;
    total_tokens_used: number;
}

export interface Decision {
    action: 'APPROVE' | 'BLOCK' | 'MANUAL_REVIEW';
    reasoning: string;
    confidence: number;
    key_factors: string[];
}

export interface ModelPrediction {
    fraud_probability: number;
    binary_prediction: 0 | 1;
    model_name: string;
    ensemble_predictions?: {
        xgboost?: number;
        lightgbm?: number;
        randomforest?: number;
    };
    consensus: 'HIGH_AGREEMENT' | 'MODERATE_AGREEMENT' | 'LOW_AGREEMENT';
    top_features?: FeatureContribution[];
}

export interface FeatureContribution {
    feature: string;
    contribution: number;
    explanation?: string;
}

export interface Anomalies {
    amount: AnomalyDetail;
    time: AnomalyDetail;
    location: AnomalyDetail;
    overall_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    explanation: string;
    red_flags: string[];
}

export interface AnomalyDetail {
    score: number;
    is_anomaly: boolean;
    explanation: string;
    severity?: 'low' | 'medium' | 'high';
}

export interface ReActStep {
    step: number;
    type: 'THOUGHT' | 'ACTION' | 'OBSERVATION' | 'DECISION';
    agent: 'coordinator' | 'data' | 'model';
    content: string;
    timestamp: string;
    metadata: StepMetadata;
}

export interface StepMetadata {
    llm_used: boolean;
    llm_purpose?: 'PLANNING' | 'INTERPRETATION' | 'DECISION';
    phase?: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
}
