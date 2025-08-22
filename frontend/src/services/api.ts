const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export type GeneratedQuestion = { type: 'technical'|'behavioral', text: string };
export type QuestionOut = {
  id: number;
  set_id: number;
  type: string;
  text: string;
  user_answer?: string | null;
  difficulty?: number | null;
  flagged: boolean;
}

export async function generate(jobTitle: string): Promise<GeneratedQuestion[]> {
  const res = await fetch(`${BASE}/api/questions/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_title: jobTitle })
  });
  if (!res.ok) throw new Error('Failed to generate');
  const data = await res.json();
  return data.questions;
}

export async function saveSet(jobTitle: string, questions: GeneratedQuestion[], name?: string) {
  const res = await fetch(`${BASE}/api/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_title: jobTitle, name, questions })
  });
  if (!res.ok) throw new Error('Failed to save set');
  return res.json();
}

export async function listQuestions(setId?: number): Promise<QuestionOut[]> {
  const url = setId ? `${BASE}/api/questions?set_id=${setId}` : `${BASE}/api/questions`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

export async function updateQuestion(qid: number, payload: Partial<{user_answer: string; difficulty: number; flagged: boolean;}>) {
  const res = await fetch(`${BASE}/api/questions/${qid}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to update');
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${BASE}/api/stats`);
  if (!res.ok) throw new Error('Failed to load stats');
  return res.json();
}

export async function listQuestionsPaged(page:number=1, pageSize:number=10, setId?: number) {
  const params = new URLSearchParams({ 
    page: String(page), 
    size: String(pageSize)  // Changed from page_size to size
  });
  if (setId !== undefined) params.set('set_id', String(setId));
  const res = await fetch(`${BASE}/api/questions?${params.toString()}`); // Removed /page
  if (!res.ok) throw new Error('Failed to fetch paged');
  return res.json();
}
