import { QueryRequest, QueryResponse } from "../types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function postQuery(
  question: string,
  conversationId?: string | null
): Promise<QueryResponse> {
  const payload: QueryRequest = { question };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  const response = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorDetail = "Something went wrong";
    try {
      const errorData = await response.json();
      if (errorData.detail) errorDetail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      else if (errorData.error) errorDetail = errorData.error;
    } catch (e) {
      // Ignored
    }
    throw new Error(errorDetail);
  }

  return response.json();
}
