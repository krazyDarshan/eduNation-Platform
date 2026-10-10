from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.course import Quiz, Question, Answer, QuizAttempt
from app.models.user import UserProgress
from app.models.gamification import Achievement, UserAchievement
from config import Config

bp = Blueprint('api', __name__)

@bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """Submit quiz answers and calculate score"""
    from app.learning import grade_quiz
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('answers'), dict):
        return jsonify(success=False, message='Provide a JSON answers object.'), 400
    try:
        result = grade_quiz(current_user, quiz, data['answers'])
    except ValueError as error:
        db.session.rollback()
        return jsonify(success=False, message=str(error)), 400
    return jsonify(success=True, **result)


@bp.route('/lesson/<int:lesson_id>/progress', methods=['POST'])
@login_required
def update_lesson_progress(lesson_id):
    from app.models.course import Lesson
    from app.learning import finish_lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or data.get('completed', True) is not True:
        return jsonify(success=False, message='Provide completed: true.'), 400
    try:
        progress, points, percentage, achievements = finish_lesson(current_user, lesson)
    except ValueError as error:
        db.session.rollback()
        return jsonify(success=False, message=str(error)), 403
    return jsonify(success=True, completed=progress.completed, points_earned=points,
                   progress_percentage=percentage,
                   new_achievements=[dict(id=a.id, name=a.name, description=a.description, icon=a.icon) for a in achievements])

@bp.route('/search')
def search():
    """Search courses and lessons"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'results': []})
    
    from app.models.course import Course, Lesson
    
    # Search courses
    courses = Course.query.filter(
        Course.title.contains(query) | Course.description.contains(query)
    ).limit(5).all()
    
    # Search lessons
    lessons = Lesson.query.filter(
        Lesson.title.contains(query) | Lesson.content.contains(query)
    ).limit(5).all()
    
    results = []
    
    for course in courses:
        results.append({
            'type': 'course',
            'title': course.title,
            'description': course.description[:150] + '...' if len(course.description) > 150 else course.description,
            'url': f'/courses/{course.id}'
        })
    
    for lesson in lessons:
        results.append({
            'type': 'lesson',
            'title': lesson.title,
            'description': lesson.content[:150] + '...' if len(lesson.content) > 150 else lesson.content,
            'url': f'/courses/{lesson.course_id}/lessons/{lesson.id}'
        })
    
    return jsonify({'results': results})

def check_achievements(user):
    """Check and award new achievements"""
    new_achievements = []
    
    # Get all achievements
    achievements = Achievement.query.all()
    earned_achievement_ids = {ua.achievement_id for ua in user.achievements}
    
    for achievement in achievements:
        if achievement.id not in earned_achievement_ids:
            # Check achievement criteria (simplified logic)
            should_award = False
            
            if 'First Steps' in achievement.name and user.total_points >= 100:
                should_award = True
            elif 'Knowledge Seeker' in achievement.name and user.total_points >= 500:
                should_award = True
            elif 'Eco Warrior' in achievement.name and user.total_points >= 1000:
                should_award = True
            elif 'Green Champion' in achievement.name and user.enrollments.filter_by(is_completed=True).count() >= 5:
                should_award = True
            elif 'Environmental Expert' in achievement.name and user.total_points >= 2500:
                should_award = True
            
            if should_award:
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                new_achievements.append(achievement)
    
    return new_achievements
