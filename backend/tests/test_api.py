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
    assert res.status_code == 200
    set_id = res.json()["id"]

    # List (unpaged)
    res = client.get("/api/questions")
    assert res.status_code == 200
    all_qs = res.json()
    assert len(all_qs) >= 2

    # Paged
    res = client.get("/api/questions/page?page=1&page_size=1&set_id=%d" % set_id)
    assert res.status_code == 200
    page = res.json()
    assert "items" in page and "total" in page and "pages" in page
    assert page["page"] == 1 and page["page_size"] == 1

    # Update a question difficulty + flag
    qid = all_qs[0]["id"]
    res = client.patch(f"/api/questions/{qid}", json={"difficulty": 4, "flagged": True})
    assert res.status_code == 200
    updated = res.json()
    assert updated["difficulty"] == 4 and updated["flagged"] is True

    # Delete it
    res = client.delete(f"/api/questions/{qid}")
    assert res.status_code == 200
