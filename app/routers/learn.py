from datetime import date, datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.gamification import PASS_THRESHOLD, calculate_streak, level_for_xp
from app.notifications import create_notification
from app.models import (
    Course,
    Lesson,
    LessonProgress,
    User,
    UserLearningStats,
)
from app.schemas import (
    CourseDetail,
    CourseSummary,
    LearningStatsResponse,
    LessonResponse,
    LessonResult,
    LessonSubmission,
    LessonSummary,
    ProgressResponse,
    QuestionResult,
    UnitResponse,
)

router = APIRouter(prefix="/learn", tags=["Learning"])


def get_or_create_stats(db: Session, user: User) -> UserLearningStats:
    """
    Fetch the user's learning stats, creating a fresh record on first use.
    """
    stats = (
        db.query(UserLearningStats)
        .filter(UserLearningStats.user_id == user.id)
        .first()
    )
    if not stats:
        stats = UserLearningStats(user_id=user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats


def _completed_lesson_ids(db: Session, user: User) -> set:
    """
    Set of lesson IDs the user has completed.
    """
    rows = (
        db.query(LessonProgress.lesson_id)
        .filter(
            LessonProgress.user_id == user.id,
            LessonProgress.status == "completed",
        )
        .all()
    )
    return {row.lesson_id for row in rows}


@router.get("/courses", response_model=List[CourseSummary])
def list_courses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all courses with the current user's completion progress.
    """
    courses = db.query(Course).order_by(Course.order).all()
    completed_ids = _completed_lesson_ids(db, current_user)

    summaries = []
    for course in courses:
        lesson_ids = [lesson.id for unit in course.units for lesson in unit.lessons]
        total = len(lesson_ids)
        completed = sum(1 for lid in lesson_ids if lid in completed_ids)
        percentage = round(completed / total * 100, 1) if total else 0.0

        summaries.append(
            CourseSummary(
                id=course.id,
                title=course.title,
                slug=course.slug,
                description=course.description,
                icon=course.icon,
                colour=course.colour,
                order=course.order,
                total_lessons=total,
                completed_lessons=completed,
                progress_percentage=percentage,
            )
        )
    return summaries


@router.get("/courses/{course_id}", response_model=CourseDetail)
def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a course with its units and lessons, including per-lesson status.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )

    progress_map = {
        p.lesson_id: p
        for p in db.query(LessonProgress).filter(
            LessonProgress.user_id == current_user.id
        )
    }

    units = []
    for unit in course.units:
        lessons = []
        for lesson in unit.lessons:
            progress = progress_map.get(lesson.id)
            lessons.append(
                LessonSummary(
                    id=lesson.id,
                    title=lesson.title,
                    order=lesson.order,
                    xp_reward=lesson.xp_reward,
                    status=progress.status if progress else "not_started",
                    score=progress.score if progress else None,
                )
            )
        units.append(
            UnitResponse(
                id=unit.id,
                title=unit.title,
                description=unit.description,
                order=unit.order,
                lessons=lessons,
            )
        )

    return CourseDetail(
        id=course.id,
        title=course.title,
        slug=course.slug,
        description=course.description,
        icon=course.icon,
        colour=course.colour,
        order=course.order,
        units=units,
    )


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a lesson and its questions (correct answers are not exposed).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )
    return lesson


@router.post("/lessons/{lesson_id}/submit", response_model=LessonResult)
def submit_lesson(
    lesson_id: UUID,
    submission: LessonSubmission,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Grade a lesson submission, record progress, award XP and update the streak.
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )

    questions = lesson.questions
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This lesson has no questions",
        )

    answer_map = {a.question_id: a.answer for a in submission.answers}

    results = []
    correct_count = 0
    for question in questions:
        given = answer_map.get(question.id)
        is_correct = (
            given is not None
            and str(given).strip().lower()
            == str(question.correct_answer).strip().lower()
        )
        if is_correct:
            correct_count += 1
        results.append(
            QuestionResult(
                question_id=question.id,
                correct=is_correct,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
            )
        )

    total = len(questions)
    score = round(correct_count / total * 100, 1)
    passed = (correct_count / total) >= PASS_THRESHOLD

    progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
        .first()
    )
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id, lesson_id=lesson_id, status="not_started"
        )
        db.add(progress)

    stats = get_or_create_stats(db, current_user)
    previous_level = stats.level
    previous_streak = stats.current_streak

    xp_earned = 0
    newly_completed = False
    if passed:
        was_completed = progress.status == "completed"
        progress.status = "completed"
        progress.completed_at = datetime.now(timezone.utc)
        # XP is only awarded the first time a lesson is completed.
        if not was_completed:
            xp_earned = lesson.xp_reward
            newly_completed = True

    progress.score = (
        max(progress.score, score) if progress.score is not None else score
    )

    today = date.today()
    new_streak = calculate_streak(stats.last_activity_date, stats.current_streak, today)
    stats.current_streak = new_streak
    stats.longest_streak = max(stats.longest_streak, new_streak)
    stats.last_activity_date = today

    if xp_earned:
        stats.xp_total += xp_earned
        stats.level = level_for_xp(stats.xp_total)

    # Raise notifications for achievements unlocked by this submission.
    if newly_completed:
        create_notification(
            db,
            user_id=current_user.id,
            type="lesson_completed",
            title="Lesson complete!",
            message=f"You completed '{lesson.title}' and earned {xp_earned} XP.",
            icon="🎓",
        )
    if stats.level > previous_level:
        create_notification(
            db,
            user_id=current_user.id,
            type="level_up",
            title="Level up!",
            message=f"You reached level {stats.level}. Keep it up!",
            icon="⭐",
        )
    if new_streak > previous_streak:
        create_notification(
            db,
            user_id=current_user.id,
            type="streak",
            title=f"{new_streak}-day streak!",
            message=f"You're on a {new_streak}-day learning streak. Don't stop now!",
            icon="🔥",
        )

    db.commit()
    db.refresh(stats)

    return LessonResult(
        lesson_id=lesson_id,
        score=score,
        correct_count=correct_count,
        total_questions=total,
        passed=passed,
        xp_earned=xp_earned,
        results=results,
        stats=LearningStatsResponse.model_validate(stats),
    )


@router.get("/me/stats", response_model=LearningStatsResponse)
def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the current user's gamification stats.
    """
    return get_or_create_stats(db, current_user)


@router.get("/me/progress", response_model=ProgressResponse)
def get_my_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the current user's overall learning progress.
    """
    total_courses = db.query(Course).count()
    total_lessons = db.query(Lesson).count()
    completed = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == current_user.id,
            LessonProgress.status == "completed",
        )
        .count()
    )
    percentage = round(completed / total_lessons * 100, 1) if total_lessons else 0.0
    stats = get_or_create_stats(db, current_user)

    return ProgressResponse(
        total_courses=total_courses,
        total_lessons=total_lessons,
        completed_lessons=completed,
        progress_percentage=percentage,
        stats=LearningStatsResponse.model_validate(stats),
    )
