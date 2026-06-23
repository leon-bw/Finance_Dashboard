import pytest
from fastapi import status

from app.models import (
    Course,
    Lesson,
    Notification,
    Question,
    Unit,
)


@pytest.fixture
def auth_headers(client, test_user):
    """
    Get auth headers for the test user
    """
    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "test1234"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def notification(test_db, test_user):
    """
    A single unread notification owned by the test user
    """
    note = Notification(
        user_id=test_user.id,
        type="achievement",
        title="Welcome",
        message="Thanks for joining!",
        icon="🎉",
    )
    test_db.add(note)
    test_db.commit()
    test_db.refresh(note)
    return note


@pytest.fixture
def lesson_with_questions(test_db):
    """
    A lesson with two questions for triggering achievement notifications
    """
    course = Course(title="Budgeting Basics", slug="budgeting-basics", order=1)
    test_db.add(course)
    test_db.flush()
    unit = Unit(course_id=course.id, title="Getting Started", order=1)
    test_db.add(unit)
    test_db.flush()
    lesson = Lesson(unit_id=unit.id, title="What is a budget?", order=1, xp_reward=10)
    test_db.add(lesson)
    test_db.flush()
    questions = [
        Question(
            lesson_id=lesson.id,
            prompt="What is a budget?",
            type="multiple_choice",
            options=["A spending plan", "A bank account"],
            correct_answer="A spending plan",
            order=1,
        ),
        Question(
            lesson_id=lesson.id,
            prompt="Budgets help avoid overspending.",
            type="true_false",
            options=["True", "False"],
            correct_answer="True",
            order=2,
        ),
    ]
    test_db.add_all(questions)
    test_db.commit()
    test_db.refresh(lesson)
    return {"lesson": lesson, "questions": questions}


class TestNotificationsEndpoints:
    def test_requires_auth(self, client):
        response = client.get("/notifications/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_notifications(self, client, auth_headers, notification):
        response = client.get("/notifications/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Welcome"
        assert data[0]["is_read"] is False

    def test_unread_count(self, client, auth_headers, notification):
        response = client.get("/notifications/unread-count", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["unread"] == 1

    def test_mark_read(self, client, auth_headers, notification):
        response = client.post(
            f"/notifications/{notification.id}/read", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_read"] is True

        count = client.get("/notifications/unread-count", headers=auth_headers)
        assert count.json()["unread"] == 0

    def test_mark_read_missing(self, client, auth_headers):
        from uuid import uuid4

        response = client.post(
            f"/notifications/{uuid4()}/read", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_all_read(self, client, auth_headers, notification):
        response = client.post("/notifications/read-all", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        count = client.get("/notifications/unread-count", headers=auth_headers)
        assert count.json()["unread"] == 0

    def test_unread_only_filter(self, client, auth_headers, notification):
        client.post("/notifications/read-all", headers=auth_headers)
        response = client.get(
            "/notifications/?unread_only=true", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestNotificationGeneration:
    def test_completing_lesson_creates_notifications(
        self, client, auth_headers, lesson_with_questions
    ):
        lesson = lesson_with_questions["lesson"]
        questions = lesson_with_questions["questions"]
        payload = {
            "answers": [
                {"question_id": str(q.id), "answer": q.correct_answer}
                for q in questions
            ]
        }
        client.post(
            f"/learn/lessons/{lesson.id}/submit",
            json=payload,
            headers=auth_headers,
        )

        response = client.get("/notifications/", headers=auth_headers)
        notes = response.json()
        types = {n["type"] for n in notes}
        # First completion: lesson_completed + streak (1-day) notifications.
        assert "lesson_completed" in types
        assert "streak" in types

    def test_failing_lesson_creates_no_completion_notification(
        self, client, auth_headers, lesson_with_questions
    ):
        lesson = lesson_with_questions["lesson"]
        questions = lesson_with_questions["questions"]
        payload = {
            "answers": [
                {"question_id": str(q.id), "answer": "wrong"} for q in questions
            ]
        }
        client.post(
            f"/learn/lessons/{lesson.id}/submit",
            json=payload,
            headers=auth_headers,
        )

        response = client.get("/notifications/", headers=auth_headers)
        types = {n["type"] for n in response.json()}
        assert "lesson_completed" not in types
