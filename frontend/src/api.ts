export type Citation = {
  source: string;
  page: number;
  section: string;
  chunk_id: string;
};

export type ChatResponse = {
  answer: string;
  language: string;
  confidence: string;
  scope_status: string;
  citations: Citation[];
  caveats: string[];
  suggested_followups: string[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function askInsureTutor(question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}
