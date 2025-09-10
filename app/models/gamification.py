from datetime import datetime
from app import db

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), default='fa-medal')
    points_required = db.Column(db.Integer, default=0)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), default='fa-award')

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    achievement = db.relationship('Achievement', backref=db.backref('user_achievements', lazy='dynamic'))

class LeaderboardView:
    @staticmethod
    def top_users(limit=10):
        from app.models.user import User
        return User.query.order_by(User.total_points.desc()).limit(limit).all()

class UserProgress(db.Model):
    # Defined in user.py; left here for type reference only
    pass

