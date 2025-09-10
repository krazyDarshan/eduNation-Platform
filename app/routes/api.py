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
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    answers = data.get('answers', {})
    
    # Check if user already attempted this quiz
    existing_attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).first()
    
    if existing_attempt:
        return jsonify({'success': False, 'message': 'Quiz already completed'})
    
    # Calculate score
    questions = quiz.questions.all()
    correct_answers = []
    score = 0
    
    for question in questions:
        question_id_str = str(question.id)
        if question_id_str in answers:
            selected_answer_id = int(answers[question_id_str])
            correct_answer = question.answers.filter_by(is_correct=True).first()
            
            if correct_answer and selected_answer_id == correct_answer.id:
                score += 1
                correct_answers.append(correct_answer.id)
            
    total_questions = len(questions)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculate points earned
    points_earned = int((percentage / 100) * Config.POINTS_PER_QUIZ)
    
    # Save quiz attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        points_earned=points_earned
    )
    db.session.add(attempt)
    
    # Add points to user
    current_user.add_points(points_earned)
    
    # Check for new achievements
    new_achievements = check_achievements(current_user)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'points_earned': points_earned,
        'correct_answers': correct_answers,
        'new_achievements': [
            {
                'id': a.id,
                'name': a.name,
                'description': a.description,
                'icon': a.icon
            } for a in new_achievements
        ]
    })

@bp.route('/lesson/<int:lesson_id>/progress', methods=['POST'])
@login_required
def update_lesson_progress(lesson_id):
    """Update lesson progress"""
    data = request.get_json()
    completed = data.get('completed', True)
    
    # Get or create progress record
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
    
    # Update progress
    if completed and not progress.completed:
        progress.mark_completed()
        current_user.add_points(Config.POINTS_PER_LESSON)
        points_earned = Config.POINTS_PER_LESSON
    else:
        points_earned = 0
    
    # Get course progress
    from app.models.course import Lesson
    lesson = Lesson.query.get(lesson_id)
    course_progress = current_user.get_course_progress(lesson.course_id) if lesson else 0
    
    # Check for new achievements
    new_achievements = check_achievements(current_user)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'completed': progress.completed,
        'points_earned': points_earned,
        'progress_percentage': course_progress,
        'new_achievements': [
            {
                'id': a.id,
                'name': a.name,
                'description': a.description,
                'icon': a.icon
            } for a in new_achievements
        ]
    })

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
