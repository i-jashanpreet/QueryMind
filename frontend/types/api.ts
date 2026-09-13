export interface ClarificationOption {
  label: string;
  value: string;
}

export interface ClarificationResponse {
  needs_clarification: boolean;
  clarification_type: string | null;
  question: string | null;
  options: ClarificationOption[];
  reason: string | null;
}

export interface QueryRequest {
  question: string;
  conversation_id?: string | null;
}

export interface QueryResponse {
  conversation_id: string | null;
  question: string;
  needs_clarification: boolean;
  clarification: ClarificationResponse | null;
  sql: string | null;
  results: Record<string, any>[] | null;
}

export interface ErrorResponse {
  error: string;
  detail?: string | null;
}
