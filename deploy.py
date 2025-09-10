"""
Deployment script for eduNation Platform
Handles database initialization and migrations for production deployment
"""
import os
from app import create_app, db
from app.models.user import User, Enrollment, UserProgress
from app.models.course import Course, Lesson, Quiz, Question, Answer
from app.models.gamification import Achievement, Badge, UserAchievement, LeaderboardView
from enhanced_db_init import create_comprehensive_content

def deploy():
    """Run deployment tasks."""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if we need to populate with initial data
        if Course.query.count() == 0:
            print("🚀 Initializing eduNation with course content...")
            create_comprehensive_content()
            print("✅ eduNation content initialized successfully!")
        else:
            print("✅ Database already contains content")
        
        print("✅ Deployment completed successfully!")

if __name__ == '__main__':
    deploy()
