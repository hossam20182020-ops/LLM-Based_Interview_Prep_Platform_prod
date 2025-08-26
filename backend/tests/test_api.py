import json
import pytest
from sqlalchemy.orm import Session
from app import models
from app.config import settings


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
    assert len(all_qs["items"]) >= 2

    # Paged - use the main endpoint instead of legacy
    res = client.get(f"/api/questions?page=1&size=1&set_id={set_id}")
    assert res.status_code == 200
    page = res.json()
    assert "items" in page and "total" in page and "pages" in page
    assert page["page"] == 1 and page["size"] == 1

    # Update a question difficulty + flag
    qid = all_qs["items"][0]["id"]
    res = client.patch(f"/api/questions/{qid}", json={"difficulty": 4, "flagged": True})
    assert res.status_code == 200
    updated = res.json()
    assert updated["difficulty"] == 4 and updated["flagged"] is True

    # Delete it
    res = client.delete(f"/api/questions/{qid}")
    assert res.status_code == 200


def test_generate_validation(client):
    """Test job title validation"""
    # Empty job title
    res = client.post("/api/questions/generate", json={"job_title": ""})
    assert res.status_code == 422
    detail = res.json()["detail"]
    if isinstance(detail, list):
        # Pydantic validation returns list of errors
        assert any("at least 1 character" in str(err).lower() or "too short" in str(err).lower() for err in detail)

    else:
        # FastAPI custom validation returns string
        assert "empty" in detail.lower()

    # Too long job title
    res = client.post("/api/questions/generate", json={"job_title": "a" * 51})
    assert res.status_code == 422
    detail = res.json()["detail"]
    if isinstance(detail, list):
        assert any("50 characters" in str(err) for err in detail)
    else:
        assert "50 characters" in detail

    # Valid job title
    res = client.post("/api/questions/generate", json={"job_title": "Software Engineer"})
    assert res.status_code == 200


def test_create_set_validation(client):
    """Test question set creation validation"""
    # Empty job title
    payload = {
        "job_title": "",
        "name": "Test",
        "questions": [{"type": "technical", "text": "Test question"}]
    }
    res = client.post("/api/questions", json=payload)
    assert res.status_code == 422

    # Too long job title
    payload["job_title"] = "a" * 51
    res = client.post("/api/questions", json=payload)
    assert res.status_code == 422

    # Valid payload
    payload["job_title"] = "Valid Job"
    res = client.post("/api/questions", json=payload)
    assert res.status_code == 201


def test_question_operations(client):
    """Test question CRUD operations"""
    # Create a question set first
    payload = {
        "job_title": "Test Engineer",
        "name": "CRUD Test",
        "questions": [
            {"type": "technical", "text": "What is testing?"},
            {"type": "behavioral", "text": "Describe your testing approach."}
        ]
    }
    res = client.post("/api/questions", json=payload)
    assert res.status_code == 201
    set_id = res.json()["id"]

    # List questions
    res = client.get("/api/questions")
    assert res.status_code == 200
    questions = res.json()["items"]
    assert len(questions) >= 2
    
    question_id = questions[0]["id"]

    # Update question - valid difficulty
    res = client.patch(f"/api/questions/{question_id}", json={"difficulty": 3.5})
    assert res.status_code == 200
    assert res.json()["difficulty"] == 3.5

    # Update question - invalid difficulty
    res = client.patch(f"/api/questions/{question_id}", json={"difficulty": 6})
    assert res.status_code == 422

    # Update question - flag
    res = client.patch(f"/api/questions/{question_id}", json={"flagged": True})
    assert res.status_code == 200
    assert res.json()["flagged"] is True

    # Update question - user answer
    res = client.patch(f"/api/questions/{question_id}", json={"user_answer": "My answer"})
    assert res.status_code == 200
    assert res.json()["user_answer"] == "My answer"

    # Delete non-existent question
    res = client.delete("/api/questions/99999")
    assert res.status_code == 404

    # Delete existing question
    res = client.delete(f"/api/questions/{question_id}")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_pagination(client):
    """Test pagination functionality"""
    # Create multiple questions
    for i in range(15):
        payload = {
            "job_title": f"Job {i}",
            "name": f"Set {i}",
            "questions": [{"type": "technical", "text": f"Question {i}"}]
        }
        client.post("/api/questions", json=payload)

    # Test pagination
    res = client.get("/api/questions?page=1&size=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) <= 5
    assert data["page"] == 1
    assert data["size"] == 5
    assert data["total"] >= 15
    assert data["pages"] >= 3

    # Test page 2
    res = client.get("/api/questions?page=2&size=5")
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 2

    # Test legacy endpoint - check if it works first
    res = client.get("/api/questions/page?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    # Check for page_size if the legacy endpoint is properly implemented
    if "page_size" in data:
        assert data["page_size"] == 10
    else:
        # Fallback to checking size if page_size not implemented
        assert data["size"] == 10

def test_stats_endpoint(client):
    """Test stats endpoint"""
    # Create some test data
    payload = {
        "job_title": "Stats Test",
        "name": "Stats Set",
        "questions": [
            {"type": "technical", "text": "Stats question 1"},
            {"type": "behavioral", "text": "Stats question 2"}
        ]
    }
    res = client.post("/api/questions", json=payload)
    assert res.status_code == 201

    # Get stats
    res = client.get("/api/stats")
    assert res.status_code == 200
    stats = res.json()
    
    assert "total_sets" in stats
    assert "total_questions" in stats
    assert "flagged_questions" in stats
    assert "avg_difficulty" in stats
    
    assert stats["total_sets"] >= 1
    assert stats["total_questions"] >= 2
    assert stats["flagged_questions"] >= 0


def test_health_check(client):
    """Test health check endpoint"""
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_filtering_by_set_id(client):
    """Test filtering questions by set_id"""
    # Create two sets
    set1_payload = {
        "job_title": "Set 1 Job",
        "name": "Set 1",
        "questions": [{"type": "technical", "text": "Set 1 question"}]
    }
    res1 = client.post("/api/questions", json=set1_payload)
    set1_id = res1.json()["id"]

    set2_payload = {
        "job_title": "Set 2 Job", 
        "name": "Set 2",
        "questions": [{"type": "behavioral", "text": "Set 2 question"}]
    }
    res2 = client.post("/api/questions", json=set2_payload)
    set2_id = res2.json()["id"]

    # Filter by set1_id
    res = client.get(f"/api/questions?set_id={set1_id}")
    assert res.status_code == 200
    questions = res.json()["items"]
    assert len(questions) == 1
    assert questions[0]["set_id"] == set1_id

    # Filter by set2_id
    res = client.get(f"/api/questions?set_id={set2_id}")
    assert res.status_code == 200
    questions = res.json()["items"]
    assert len(questions) == 1
    assert questions[0]["set_id"] == set2_id


def test_edge_cases(client):
    """Test various edge cases"""
    # Test updating non-existent question
    res = client.patch("/api/questions/99999", json={"difficulty": 3})
    assert res.status_code == 404

    # Test invalid query parameters
    res = client.get("/api/questions?page=0")  # page must be >= 1
    assert res.status_code == 422

    res = client.get("/api/questions?size=0")  # size must be >= 1
    assert res.status_code == 422

    res = client.get("/api/questions?size=101")  # size must be <= 100
    assert res.status_code == 422


def test_config_and_database(db_session):
    """Test configuration and database utilities"""
    # Test config
    assert settings.database_url is not None
    assert settings.cors_origins is not None
    
    # Test database session
    assert db_session is not None
    
    # Test model creation
    qa_set = models.QASet(job_title="Test Job", name="Test Set")
    db_session.add(qa_set)
    db_session.flush()
    
    question = models.Question(
        set_id=qa_set.id,
        type=models.QuestionType.technical,
        text="Test question"
    )
    db_session.add(question)
    db_session.commit()
    
    # Verify data was saved
    saved_set = db_session.query(models.QASet).filter_by(job_title="Test Job").first()
    assert saved_set is not None
    assert saved_set.name == "Test Set"
    
    saved_question = db_session.query(models.Question).filter_by(text="Test question").first()
    assert saved_question is not None
    assert saved_question.type == models.QuestionType.technical


def test_database_utilities():
    """Test database initialization functions"""
    from app.database import init_db, init_db_for_tests
    
    # These should not raise exceptions
    init_db()  # Should be no-op in production
    init_db_for_tests()  # Should create tables for tests


def test_model_representations():
    """Test model __repr__ methods"""
    qa_set = models.QASet(id=1, job_title="Test Job")
    repr_str = repr(qa_set)
    assert "QASet" in repr_str
    assert "Test Job" in repr_str
    
    question = models.Question(id=1, set_id=1, type=models.QuestionType.technical)
    repr_str = repr(question)
    assert "Question" in repr_str
    assert "technical" in repr_str


def test_question_type_enum():
    """Test QuestionType enum"""
    assert models.QuestionType.technical == "technical"
    assert models.QuestionType.behavioral == "behavioral"
    
    # Test enum conversion
    tech_type = models.QuestionType("technical")
    assert tech_type == models.QuestionType.technical


def test_error_handling_in_endpoints(client):
    """Test error handling in various endpoints"""
    # Test malformed JSON
    res = client.post("/api/questions/generate", 
                     data="invalid json", 
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422

    # Test missing required fields
    res = client.post("/api/questions/generate", json={})
    assert res.status_code == 422

    # Test invalid field types
    res = client.post("/api/questions/generate", json={"job_title": 123})
    assert res.status_code == 422