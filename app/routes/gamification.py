from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.gamification import LeaderboardView, Achievement, Badge, UserAchievement

bp = Blueprint('gamification', __name__)

@bp.route('/leaderboard')
@login_required
def leaderboard():
    """Display leaderboard with top users"""
    top_users = LeaderboardView.top_users(50)
    current_user_rank = current_user.get_leaderboard_rank()
    
    # Add rank to each user
    for i, user in enumerate(top_users):
        user.rank = i + 1
        user.is_current_user = (user.id == current_user.id)
    
    return render_template('gamification/leaderboard.html',
                         top_users=top_users,
                         current_user_rank=current_user_rank)

@bp.route('/achievements')
@login_required
def achievements():
    """Display user's achievements and available badges"""
    user_achievements = current_user.get_achievements()
    all_achievements = Achievement.query.all()
    all_badges = Badge.query.all()
    
    # Mark which achievements/badges user has earned
    earned_achievement_ids = {a.id for a in user_achievements}
    
    for achievement in all_achievements:
        achievement.earned = achievement.id in earned_achievement_ids
    
    # Calculate progress toward badges
    user_badges = []
    for badge in all_badges:
        earned = current_user.total_points >= badge.points_required
        progress = min((current_user.total_points / badge.points_required) * 100, 100) if badge.points_required > 0 else 100
        user_badges.append({
            'badge': badge,
            'earned': earned,
            'progress': progress
        })
    
    return render_template('gamification/achievements.html',
                         achievements=all_achievements,
                         badges=user_badges,
                         user_points=current_user.total_points)

@bp.route('/api/user-stats')
@login_required
def user_stats():
    """API endpoint for user gamification stats"""
    return jsonify({
        'total_points': current_user.total_points,
        'level': current_user.get_level(),
        'level_progress': current_user.get_level_progress(),
        'rank': current_user.get_leaderboard_rank(),
        'achievements_count': current_user.achievements.count(),
        'streak_days': current_user.streak_days
    })
