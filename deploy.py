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
    try:
        app = create_app()
        
        with app.app_context():
            print("🔗 Testing database connection...")
            
            # Test database connection
            try:
                db.engine.connect()
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return
            
            # Create database tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created")
            
            # Check if we need to populate with initial data
            try:
                course_count = Course.query.count()
                print(f"📚 Found {course_count} existing courses")
                
                if course_count == 0:
                    print("🚀 Initializing eduNation with course content...")
                    create_comprehensive_content()
                    print("✅ eduNation content initialized successfully!")
                else:
                    print("✅ Database already contains content")
                    
            except Exception as e:
                print(f"⚠️ Error checking/creating content: {e}")
                print("🔄 Attempting to create content anyway...")
                try:
                    create_comprehensive_content()
                    print("✅ Content creation completed")
                except Exception as e2:
                    print(f"❌ Content creation failed: {e2}")
            
            print("✅ Deployment completed successfully!")
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    deploy()
