import json

def test_generate_fallback(client):
    # With no GEMINI_API_KEY set in tests, llm falls back
    res = client.post("/api/questions/generate", json={"job_title": "QA Engineer"})
    assert res.status_code == 200
    data = res.json()
    assert "questions" in data
    assert len(data["questions"]) >= 1
    assert all(q["type"] in ("technical", "behavioral") for q in data["questions"])

def test_create_list_update_delete(client):
    # Create a set with two questions
    payload = {
        "job_title": "Backend Dev",
        "name": "Test Set",
        "questions": [
            {"type": "technical", "text": "Explain async IO."},
            {"type": "behavioral", "text": "Tell me about a conflict."}
        ]
    }
    res = client.post("/api/questions", json=payload)
    assert res.status_code == 201
    set_id = res.json()["id"]
    
    # List (unpaged)
    res = client.get("/api/questions")
    assert res.status_code == 200
    all_qs = res.json()

    # If endpoint returns dict with "items", extract them
    if isinstance(all_qs, dict) and "items" in all_qs:
        questions = all_qs["items"]
    else:
        questions = all_qs

    assert len(questions) >= 2

    # Update a question difficulty + flag
    qid = questions[0]["id"]
    res = client.patch(f"/api/questions/{qid}", json={"difficulty": 4, "flagged": True})
    assert res.status_code == 200
    updated = res.json()
    assert updated["difficulty"] == 4 and updated["flagged"] is True


    # Delete it
    res = client.delete(f"/api/questions/{qid}")
    assert res.status_code == 200
