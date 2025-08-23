const RAW_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
// normalize: remove trailing slash
export const BASE = RAW_BASE.replace(/\/$/, "");

export type GeneratedQuestion = { type: "technical" | "behavioral"; text: string };
export type QuestionOut = {
  id: number;
  set_id: number;
  type: string;
  text: string;
  user_answer?: string | null;
  difficulty?: number | null;
  flagged: boolean;
};

async function safeJson<T>(res: Response): Promise<T | null> {
  // Gracefully handle 204 or empty body
  if (res.status === 204) return null;
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export async function generate(jobTitle: string): Promise<GeneratedQuestion[]> {
  if (jobTitle.length > 50) throw new Error("Job title must be 50 characters or less");
  if (jobTitle.trim().length === 0) throw new Error("Job title cannot be empty");

  const res = await fetch(`${BASE}/api/questions/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title: jobTitle }),
  });

  if (!res.ok) {
    const err = await safeJson<{ detail?: string }>(res);
    throw new Error(err?.detail || "Failed to generate");
  }

  const data = await safeJson<{ questions: GeneratedQuestion[] }>(res);
  return data?.questions ?? [];
}

export async function saveSet(jobTitle: string, questions: GeneratedQuestion[], name?: string) {
  if (jobTitle.length > 50) throw new Error("Job title must be 50 characters or less");
  if (jobTitle.trim().length === 0) throw new Error("Job title cannot be empty");

  const res = await fetch(`${BASE}/api/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title: jobTitle, name, questions }),
  });

  if (!res.ok) {
    const err = await safeJson<{ detail?: string }>(res);
    throw new Error(err?.detail || "Failed to save set");
  }

  return safeJson(res);
}

export async function updateQuestion(
  qid: number,
  payload: Partial<{ user_answer: string; difficulty: number; flagged: boolean }>
) {
  const res = await fetch(`${BASE}/api/questions/${qid}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await safeJson<{ detail?: string }>(res);
    throw new Error(err?.detail || "Failed to update");
  }
  return safeJson(res);
}

export async function deleteQuestion(qid: number): Promise<void> {
  const res = await fetch(`${BASE}/api/questions/${qid}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await safeJson<{ detail?: string }>(res);
    throw new Error(err?.detail || "Failed to delete question");
  }
}

export type Stats = { totalSets: number; totalQuestions: number; lastSavedAt?: string };

export async function getStats(signal?: AbortSignal): Promise<Stats | null> {
  const res = await fetch(`${BASE}/api/stats`, { signal, headers: { Accept: "application/json" } });
  if (!res.ok) {
    // don’t throw → let UI show a friendly error, not spin forever
    return null;
  }
  return (await safeJson<Stats>(res)) ?? null;
}

export async function listQuestionsPaged(page: number = 1, pageSize: number = 10, setId?: number) {
  const params = new URLSearchParams({ page: String(page), size: String(pageSize) });
  if (setId !== undefined) params.set("set_id", String(setId));

  const res = await fetch(`${BASE}/api/questions?${params.toString()}`);
  if (!res.ok) {
    const err = await safeJson<{ detail?: string }>(res);
    throw new Error(err?.detail || "Failed to fetch paged");
  }
  return safeJson(res);
}
