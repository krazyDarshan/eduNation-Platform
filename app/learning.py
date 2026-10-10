"""Shared, transactional learning actions for HTML and JSON routes."""
from datetime import datetime
from app import db
from app.models.user import User, Enrollment, UserProgress
from app.models.course import QuizAttempt
from config import Config


def lock_learner(user):
    # Serialize simultaneous requests so retries cannot award points twice.
    return User.query.filter_by(id=user.id).populate_existing().with_for_update().one()


def finish_lesson(user, lesson):
    user = lock_learner(user)
    enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=lesson.course_id).first()
    if not enrollment:
        raise ValueError('Enroll in this course first.')
    progress = UserProgress.query.filter_by(user_id=user.id, lesson_id=lesson.id).first()
    if not progress:
        progress = UserProgress(user_id=user.id, lesson_id=lesson.id)
        db.session.add(progress)
    points = 0
    if not progress.completed:
        progress.mark_completed()
        points = Config.POINTS_PER_LESSON
        user.add_points(points)
    db.session.flush()
    percentage = user.get_course_progress(lesson.course_id)
    if percentage == 100 and not enrollment.is_completed:
        enrollment.is_completed = True
        enrollment.completed_at = datetime.utcnow()
    from app.routes.api import check_achievements
    achievements = check_achievements(user)
    db.session.commit()
    return progress, points, percentage, achievements


def grade_quiz(user, quiz, answers):
    user = lock_learner(user)
    if not Enrollment.query.filter_by(user_id=user.id, course_id=quiz.course_id).first():
        raise ValueError('Enroll in this course first.')
    questions = quiz.questions.order_by('order').all()
    if not questions:
        raise ValueError('This quiz has no questions yet.')
    score = 0
    correct_ids = []
    for question in questions:
        answer = answers.get(str(question.id))
        if answer is None or not any(str(a.id) == str(answer) for a in question.answers):
            raise ValueError('Please answer every question with one of its options.')
        correct = question.answers.filter_by(is_correct=True).first()
        if correct:
            correct_ids.append(correct.id)
            score += str(correct.id) == str(answer)
    percentage = score / len(questions) * 100
    earned = Config.POINTS_PER_QUIZ if percentage >= 80 else Config.POINTS_PER_QUIZ // 2 if percentage >= 60 else 0
    attempt = QuizAttempt.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    previous_points = attempt.points_earned if attempt else 0
    if not attempt:
        attempt = QuizAttempt(user_id=user.id, quiz_id=quiz.id, score=score, points_earned=earned)
        db.session.add(attempt)
    elif score > attempt.score:
        attempt.score = score
        attempt.points_earned = max(previous_points, earned)
        attempt.attempted_at = datetime.utcnow()
    points = max(0, earned - previous_points)
    user.add_points(points)
    from app.routes.api import check_achievements
    achievements = check_achievements(user)
    db.session.commit()
    return dict(score=score, total_questions=len(questions), percentage=percentage,
                points_earned=points, correct_answers=correct_ids,
                new_achievements=[dict(id=a.id, name=a.name, description=a.description, icon=a.icon) for a in achievements])
