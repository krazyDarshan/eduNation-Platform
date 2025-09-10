from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(200))
    
    # User role and permissions
    role = db.Column(db.String(20), default='student')  # student, educator, admin
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    
    # Gamification fields
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    user_progress = db.relationship('UserProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_level(self):
        """Calculate user level based on points"""
        if self.total_points < 100:
            return 1
        elif self.total_points < 500:
            return 2
        elif self.total_points < 1500:
            return 3
        elif self.total_points < 3000:
            return 4
        else:
            return 5
    
    def get_level_progress(self):
        """Get progress to next level as percentage"""
        level_thresholds = [0, 100, 500, 1500, 3000, 10000]
        current_level = self.get_level()
        
        if current_level >= 5:
            return 100
        
        current_threshold = level_thresholds[current_level - 1]
        next_threshold = level_thresholds[current_level]
        
        progress = ((self.total_points - current_threshold) / (next_threshold - current_threshold)) * 100
        return min(progress, 100)
    
    def add_points(self, points):
        """Add points to user and update level"""
        self.total_points += points
        self.level = self.get_level()
        self.last_activity = datetime.utcnow()
    
    def get_achievements(self):
        """Get user's achievements"""
        return [ua.achievement for ua in self.achievements.all()]
    
    def has_achievement(self, achievement_id):
        """Check if user has specific achievement"""
        return self.achievements.filter_by(achievement_id=achievement_id).first() is not None
    
    def get_course_progress(self, course_id):
        """Get user's progress in a specific course"""
        from app.models.course import Course
        course = Course.query.get(course_id)
        if not course:
            return 0
        
        total_lessons = len(course.lessons)
        if total_lessons == 0:
            return 0
        
        completed_lessons = self.user_progress.filter_by(
            lesson_id=db.any_([lesson.id for lesson in course.lessons]),
            completed=True
        ).count()
        
        return (completed_lessons / total_lessons) * 100
    
    def get_leaderboard_rank(self):
        """Get user's rank on leaderboard"""
        return User.query.filter(User.total_points > self.total_points).count() + 1
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'total_points': self.total_points,
            'level': self.level,
            'created_at': self.created_at.isoformat(),
            'role': self.role
        }

class Enrollment(db.Model):
    """User course enrollment model"""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_enrollment'),)
    
    def __repr__(self):
        return f'<Enrollment User:{self.user_id} Course:{self.course_id}>'
    
    def get_progress_percentage(self):
        """Get enrollment progress as percentage"""
        from app.models.course import Lesson
        
        course_lessons = Lesson.query.filter_by(course_id=self.course_id).all()
        if not course_lessons:
            return 0
        
        completed_lessons = UserProgress.query.filter_by(
            user_id=self.user_id,
            completed=True
        ).filter(UserProgress.lesson_id.in_([lesson.id for lesson in course_lessons])).count()
        
        return (completed_lessons / len(course_lessons)) * 100

class UserProgress(db.Model):
    """Track user progress through lessons"""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_spent = db.Column(db.Integer, default=0)  # in seconds
    
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_progress'),)
    
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Lesson:{self.lesson_id}>'
    
    def mark_completed(self):
        """Mark lesson as completed"""
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.utcnow()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
