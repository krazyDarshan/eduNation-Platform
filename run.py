from app import create_app, db
from app.models.user import User
from app.models.course import Course, Lesson, Quiz, Question, Answer
from app.models.gamification import Badge, Achievement, UserProgress

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Course': Course,
        'Lesson': Lesson,
        'Quiz': Quiz,
        'Question': Question,
        'Answer': Answer,
        'Badge': Badge,
        'Achievement': Achievement,
        'UserProgress': UserProgress
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
