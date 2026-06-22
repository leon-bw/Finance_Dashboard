from datetime import date, timedelta

import pytest
from fastapi import status

from app.gamification import calculate_streak, level_for_xp
from app.models import Course, Lesson, Question, Unit


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
def course_with_lesson(test_db):
    """
    A course -> unit -> lesson -> questions tree for testing.
    """
    course = Course(
        title="Budgeting Basics",
        slug="budgeting-basics",
        description="Learn the fundamentals.",
        icon="📘",
        colour="#58CC02",
        order=1,
    )
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
            explanation="A budget is a plan for your money.",
            order=1,
        ),
        Question(
            lesson_id=lesson.id,
            prompt="A budget helps avoid overspending.",
            type="true_false",
            options=["True", "False"],
            correct_answer="True",
            explanation="Planning ahead keeps spending in check.",
            order=2,
        ),
    ]
    test_db.add_all(questions)
    test_db.commit()
    test_db.refresh(course)
    test_db.refresh(lesson)
    return {"course": course, "unit": unit, "lesson": lesson, "questions": questions}


class TestGamificationHelpers:
    def test_level_for_xp(self):
        assert level_for_xp(0) == 1
        assert level_for_xp(99) == 1
        assert level_for_xp(100) == 2
        assert level_for_xp(250) == 3

    def test_streak_starts_at_one(self):
        assert calculate_streak(None, 0) == 1

    def test_streak_increments_after_consecutive_day(self):
        today = date(2026, 6, 22)
        yesterday = today - timedelta(days=1)
        assert calculate_streak(yesterday, 3, today=today) == 4

    def test_streak_unchanged_same_day(self):
        today = date(2026, 6, 22)
        assert calculate_streak(today, 5, today=today) == 5

    def test_streak_resets_after_gap(self):
        today = date(2026, 6, 22)
        old = today - timedelta(days=3)
        assert calculate_streak(old, 5, today=today) == 1


class TestCoursesEndpoints:
    def test_requires_auth(self, client):
        response = client.get("/learn/courses")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_courses(self, client, auth_headers, course_with_lesson):
        response = client.get("/learn/courses", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "budgeting-basics"
        assert data[0]["total_lessons"] == 1
        assert data[0]["completed_lessons"] == 0
        assert data[0]["progress_percentage"] == 0.0

    def test_get_course_detail(self, client, auth_headers, course_with_lesson):
        course_id = str(course_with_lesson["course"].id)
        response = client.get(f"/learn/courses/{course_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["units"]) == 1
        assert data["units"][0]["lessons"][0]["status"] == "not_started"

    def test_get_missing_course(self, client, auth_headers):
        from uuid import uuid4

        response = client.get(f"/learn/courses/{uuid4()}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLessonEndpoints:
    def test_get_lesson_hides_answers(
        self, client, auth_headers, course_with_lesson
    ):
        lesson_id = str(course_with_lesson["lesson"].id)
        response = client.get(f"/learn/lessons/{lesson_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["questions"]) == 2
        for question in data["questions"]:
            assert "correct_answer" not in question

    def test_submit_all_correct_awards_xp(
        self, client, auth_headers, course_with_lesson
    ):
        lesson_id = str(course_with_lesson["lesson"].id)
        questions = course_with_lesson["questions"]
        payload = {
            "answers": [
                {"question_id": str(q.id), "answer": q.correct_answer}
                for q in questions
            ]
        }

        response = client.post(
            f"/learn/lessons/{lesson_id}/submit", json=payload, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["passed"] is True
        assert data["correct_count"] == 2
        assert data["score"] == 100.0
        assert data["xp_earned"] == 10
        assert data["stats"]["xp_total"] == 10
        assert data["stats"]["current_streak"] == 1

    def test_submit_incorrect_does_not_pass(
        self, client, auth_headers, course_with_lesson
    ):
        lesson_id = str(course_with_lesson["lesson"].id)
        questions = course_with_lesson["questions"]
        payload = {
            "answers": [
                {"question_id": str(q.id), "answer": "definitely wrong"}
                for q in questions
            ]
        }

        response = client.post(
            f"/learn/lessons/{lesson_id}/submit", json=payload, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["passed"] is False
        assert data["correct_count"] == 0
        assert data["xp_earned"] == 0
        assert data["stats"]["xp_total"] == 0

    def test_resubmitting_does_not_double_award_xp(
        self, client, auth_headers, course_with_lesson
    ):
        lesson_id = str(course_with_lesson["lesson"].id)
        questions = course_with_lesson["questions"]
        payload = {
            "answers": [
                {"question_id": str(q.id), "answer": q.correct_answer}
                for q in questions
            ]
        }

        first = client.post(
            f"/learn/lessons/{lesson_id}/submit", json=payload, headers=auth_headers
        )
        second = client.post(
            f"/learn/lessons/{lesson_id}/submit", json=payload, headers=auth_headers
        )

        assert first.json()["xp_earned"] == 10
        assert second.json()["xp_earned"] == 0
        assert second.json()["stats"]["xp_total"] == 10

    def test_submit_marks_course_progress(
        self, client, auth_headers, course_with_lesson
    ):
        lesson_id = str(course_with_lesson["lesson"].id)
        course_id = str(course_with_lesson["course"].id)
        questions = course_with_lesson["questions"]
        payload = {
            "answers": [
                {"question_id": str(q.id), "answer": q.correct_answer}
                for q in questions
            ]
        }
        client.post(
            f"/learn/lessons/{lesson_id}/submit", json=payload, headers=auth_headers
        )

        response = client.get("/learn/courses", headers=auth_headers)
        assert response.json()[0]["completed_lessons"] == 1
        assert response.json()[0]["progress_percentage"] == 100.0

        detail = client.get(f"/learn/courses/{course_id}", headers=auth_headers)
        assert detail.json()["units"][0]["lessons"][0]["status"] == "completed"


class TestStatsAndProgress:
    def test_stats_created_on_first_access(self, client, auth_headers, test_user):
        response = client.get("/learn/me/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["xp_total"] == 0
        assert data["level"] == 1
        assert data["hearts"] == 5

    def test_progress_summary(self, client, auth_headers, course_with_lesson):
        response = client.get("/learn/me/progress", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_courses"] == 1
        assert data["total_lessons"] == 1
        assert data["completed_lessons"] == 0
        assert "stats" in data
