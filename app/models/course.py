from datetime import datetime
from app import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cover_image = db.Column(db.String(200))
    
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    total_points = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    points_earned = db.Column(db.Integer, default=0)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', name='unique_quiz_attempt'),)

