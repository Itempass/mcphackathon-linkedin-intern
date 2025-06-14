import pytest
from fastapi.testclient import TestClient
from src.main import app
import datetime

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_send_messages(mocker):
    # Mock the background task function
    mock_task = mocker.patch("src.background_tasks.run_thread_processing")

    payload = {
        "user_id": "test_user",
        "thread_name": "test_thread",
        "messages": [
            {
                "message_id": "msg1",
                "sender_name": "sender1",
                "date": str(datetime.date.today()),
                "time": str(datetime.time(12, 30)),
                "message_content": "Hello world"
            }
        ]
    }
    response = client.post("/send-messages/", json=payload)
    assert response.status_code == 202
    assert response.json() == {"message": "Message processing started in the background"}
    # Assert that the task was called once
    mock_task.assert_called_once()

def test_process_feedback(mocker):
    # Mock the background task function
    mock_task = mocker.patch("src.background_tasks.run_feedback_processing")

    payload = {
        "user_id": "test_user",
        "draft_message_id": "draft123",
        "feedback": "This is great!"
    }
    response = client.post("/process-feedback/", json=payload)
    assert response.status_code == 202
    assert response.json() == {"message": "Feedback processing started in the background"}
    # Assert that the task was called once
    mock_task.assert_called_once()

def test_reject_draft():
    payload = {
        "user_id": "test_user",
        "draft_message_id": "draft123"
    }
    response = client.post("/reject-draft/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Draft rejected"}

def test_get_draft_messages():
    response = client.get("/draft-messages/?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "draft_messages" in data
    assert isinstance(data["draft_messages"], list)
    assert len(data["draft_messages"]) > 0
    # Check structure of the first draft
    draft = data["draft_messages"][0]
    assert "thread_name" in draft
    assert "draft_message_id" in draft
    assert "draft_message_content" in draft 