from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Enrollment
from app.models.course import Course
from app.models.gamification import LeaderboardView

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page showing featured courses and platform overview"""
    featured_courses = Course.query.limit(6).all()
    top_learners = LeaderboardView.top_users(5)
    
    stats = {
        'total_users': User.query.count(),
        'total_courses': Course.query.count(),
        'total_enrollments': Enrollment.query.count()
    }
    
    return render_template('main/index.html', 
                         featured_courses=featured_courses,
                         top_learners=top_learners,
                         stats=stats)

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing progress and recommendations"""
    user_enrollments = current_user.enrollments.all()
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(4).all()
    
    # Calculate overall progress
    total_progress = 0
    if user_enrollments:
        total_progress = sum(enrollment.get_progress_percentage() for enrollment in user_enrollments) / len(user_enrollments)
    
    user_rank = current_user.get_leaderboard_rank()
    achievements = current_user.get_achievements()
    
    dashboard_data = {
        'enrollments': user_enrollments,
        'recent_courses': recent_courses,
        'overall_progress': total_progress,
        'user_rank': user_rank,
        'achievements': achievements[:5],  # Show latest 5 achievements
        'total_achievements': len(achievements)
    }
    
    return render_template('main/dashboard.html', **dashboard_data)

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_stats = {
        'courses_completed': current_user.enrollments.filter_by(is_completed=True).count(),
        'total_enrollments': current_user.enrollments.count(),
        'achievements_earned': current_user.achievements.count(),
        'current_level': current_user.get_level(),
        'level_progress': current_user.get_level_progress()
    }
    
    recent_activities = current_user.user_progress.order_by(
        current_user.user_progress.c.completed_at.desc()
    ).limit(10).all() if current_user.user_progress else []
    
    return render_template('main/profile.html', 
                         user_stats=user_stats,
                         recent_activities=recent_activities)

@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html')
