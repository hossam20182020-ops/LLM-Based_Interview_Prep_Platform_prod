from .config import settings
from typing import List, Dict
import json , time , random

# Using Google AI Studio (Gemini) via google-generativeai
# If key is not provided, we return a simple fallback.
def _fallback_questions(job_title: str) -> List[Dict]:
    return [
        {"type": "technical", "text": f"What are common data structures used by a {job_title}?"},
        {"type": "technical", "text": "Explain the difference between concurrency and parallelism."},
        {"type": "behavioral", "text": "Tell me about a time you handled a tight deadline."},
        {"type": "behavioral", "text": "Describe a conflict with a teammate and how you resolved it."},
    ]

def generate_questions(job_title: str) -> List[Dict]:
    api_key = settings.gemini_api_key
    if not api_key:
        return _fallback_questions(job_title)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        system_prompt = """
            You are generating interview questions. Respond ONLY with valid compact JSON.
            Schema: {"questions": [{"type": "technical|behavioral", "text": "string"}, ...]}.
            No markdown, no backticks, no commentary.
            """

        user_prompt = (
            f"Generate 8 interview questions (4 technical, 4 behavioral) for the job title: '{job_title}'. "
            "Vary difficulty. Use concise phrasing."
        )

        resp = model.generate_content([system_prompt, user_prompt])
        text = resp.text.strip()

        # If it isn't clean JSON, try to extract the JSON object best-effort
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end+1]

        data = json.loads(text)
        questions = data.get("questions", [])
        cleaned = []
        for q in questions:
            t = q.get("type", "").lower()
            if t not in ("technical", "behavioral"):
                continue
            cleaned.append({"type": t, "text": q.get("text", "").strip()})
        if not cleaned:
            return _fallback_questions(job_title)
        return cleaned
    except Exception:
        return _fallback_questions(job_title)
