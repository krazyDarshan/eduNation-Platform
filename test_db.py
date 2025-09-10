#!/usr/bin/env python3
"""Test database connectivity"""

from app import create_app, db
from app.models.course import Course

def test_db():
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Test query
            courses = Course.query.all()
            print(f"Found {len(courses)} courses")
            for course in courses:
                print(f"- {course.title}")
                
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

if __name__ == "__main__":
    test_db()
