from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, Lesson, Quiz
from app.models.user import Enrollment, UserProgress

bp = Blueprint('courses', __name__)

@bp.route('/')
def index():
    """Course listing page with filtering and search"""
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    page = request.args.get('page', 1, type=int)
    
    query = Course.query
    
    if search:
        query = query.filter(Course.title.contains(search) | Course.description.contains(search))
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    courses = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Add enrollment status for each course if user is logged in
    if current_user.is_authenticated:
        enrolled_course_ids = {e.course_id for e in current_user.enrollments}
        for course in courses.items:
            course.is_enrolled = course.id in enrolled_course_ids
    
    return render_template('courses/index.html', 
                         courses=courses,
                         search=search,
                         difficulty=difficulty)

@bp.route('/<int:course_id>')
def detail(course_id):
    """Course detail page"""
    course = Course.query.get_or_404(course_id)
    lessons = course.lessons.order_by(Lesson.order).all()
    quizzes = course.quizzes.all()
    
    enrollment = None
    progress_data = {}
    
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, 
            course_id=course_id
        ).first()
        
        if enrollment:
            # Get user progress for each lesson
            user_progress = {
                up.lesson_id: up for up in 
                current_user.user_progress.filter(
                    UserProgress.lesson_id.in_([l.id for l in lessons])
                ).all()
            }
            
            for lesson in lessons:
                progress_data[lesson.id] = {
                    'completed': lesson.id in user_progress and user_progress[lesson.id].completed,
                    'progress': user_progress.get(lesson.id)
                }
    
    return render_template('courses/detail.html',
                         course=course,
                         lessons=lessons,
                         quizzes=quizzes,
                         enrollment=enrollment,
                         progress_data=progress_data)

@bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    """Enroll user in course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Create enrollment
    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in "{course.title}"!', 'success')
    return redirect(url_for('courses.detail', course_id=course_id))

@bp.route('/<int:course_id>/lessons/<int:lesson_id>')
@login_required
def lesson(course_id, lesson_id):
    """Individual lesson view"""
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Verify lesson belongs to course
    if lesson.course_id != course_id:
        flash('Lesson not found in this course', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course to access lessons', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Get or create progress record
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
        db.session.commit()
    
    # Get all lessons for navigation
    all_lessons = course.lessons.order_by(Lesson.order).all()
    current_lesson_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), 0)
    
    prev_lesson = all_lessons[current_lesson_index - 1] if current_lesson_index > 0 else None
    next_lesson = all_lessons[current_lesson_index + 1] if current_lesson_index < len(all_lessons) - 1 else None
    
    return render_template('courses/lesson.html',
                         course=course,
                         lesson=lesson,
                         progress=progress,
                         prev_lesson=prev_lesson,
                         next_lesson=next_lesson,
                         lesson_number=current_lesson_index + 1,
                         total_lessons=len(all_lessons))

@bp.route('/<int:course_id>/quiz/<int:quiz_id>')
@login_required
def quiz(course_id, quiz_id):
    """Quiz view"""
    course = Course.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Verify quiz belongs to course
    if quiz.course_id != course_id:
        flash('Quiz not found in this course', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course to take quizzes', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Get questions with answers
    questions = quiz.questions.order_by('order').all()
    for question in questions:
        question.answers_list = question.answers.all()
    
    return render_template('courses/quiz.html',
                         course=course,
                         quiz=quiz,
                         questions=questions)

@bp.route('/<int:course_id>/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(course_id, quiz_id):
    """Handle quiz submission and scoring"""
    course = Course.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Verify quiz belongs to course
    if quiz.course_id != course_id:
        flash('Quiz not found in this course', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course to take quizzes', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Get questions and process answers
    questions = quiz.questions.order_by('order').all()
    total_questions = len(questions)
    correct_answers = 0
    
    for question in questions:
        submitted_answer_id = request.form.get(f'q{question.id}')
        if submitted_answer_id:
            # Find the correct answer
            correct_answer = question.answers.filter_by(is_correct=True).first()
            if correct_answer and str(correct_answer.id) == submitted_answer_id:
                correct_answers += 1
    
    # Calculate score percentage
    score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Award points based on performance
    from config import Config
    if score_percentage >= 80:
        points_awarded = Config.POINTS_PER_QUIZ
        current_user.total_points += points_awarded
        flash(f'Excellent! You scored {score_percentage:.0f}% and earned {points_awarded} points!', 'success')
    elif score_percentage >= 60:
        points_awarded = Config.POINTS_PER_QUIZ // 2
        current_user.total_points += points_awarded
        flash(f'Good job! You scored {score_percentage:.0f}% and earned {points_awarded} points!', 'info')
    else:
        points_awarded = 0
        flash(f'You scored {score_percentage:.0f}%. Try reviewing the material and take the quiz again!', 'warning')
    
    db.session.commit()
    
    return render_template('courses/quiz_results.html',
                         course=course,
                         quiz=quiz,
                         score_percentage=score_percentage,
                         correct_answers=correct_answers,
                         total_questions=total_questions,
                         points_awarded=points_awarded)

@bp.route('/<int:course_id>/lessons/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(course_id, lesson_id):
    """Mark lesson as completed"""
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Verify lesson belongs to course
    if lesson.course_id != course_id:
        flash('Lesson not found in this course', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course to complete lessons', 'error')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    # Get or create progress record
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
    
    # Mark as completed
    progress.completed = True
    progress.completed_at = db.func.current_timestamp()
    
    # Award points for completion
    if not progress.completed:
        from config import Config
        current_user.total_points += Config.POINTS_PER_LESSON
        points_awarded = Config.POINTS_PER_LESSON
    else:
        points_awarded = 0
    
    db.session.commit()
    
    if points_awarded > 0:
        flash('Lesson completed! You earned {} points.'.format(points_awarded), 'success')
    else:
        flash('Lesson already completed!', 'info')
    return redirect(url_for('courses.lesson', course_id=course_id, lesson_id=lesson_id))
