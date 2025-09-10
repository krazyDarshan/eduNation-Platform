# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## EcoLearn Platform Overview

EcoLearn is a Flask-based gamified environmental education platform that combines interactive learning with gamification elements. The platform supports multiple user roles (students, educators, admins) and provides comprehensive course management with points, achievements, and leaderboards.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Database Management
```bash
# Initialize database with sample data
python init_db.py

# Flask migrations (if schema changes)
flask db init
flask db migrate -m "Migration description"
flask db upgrade

# Reset database (development only)
rm ecolearn.db
python init_db.py
```

### Running the Application
```bash
# Development server
python run.py

# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Flask Shell Context
```bash
# Access Flask shell with models pre-imported
flask shell
# Available: db, User, Course, Lesson, Quiz, Question, Answer, Badge, Achievement, UserProgress
```

### Testing and Debugging
```bash
# Run specific route debugging
flask routes  # List all routes

# Check database content
python -c "from app import create_app, db; from app.models.user import User; app = create_app(); app.app_context().push(); print(User.query.count())"
```

## Architecture Overview

### Application Structure
- **Flask Application Factory Pattern**: `app/__init__.py` creates app with extensions
- **Blueprint-based Routing**: Routes organized by functionality (auth, courses, gamification, api, main)
- **SQLAlchemy ORM**: Database models with relationships and business logic
- **Flask-Login**: Session management and user authentication
- **Flask-Migrate**: Database schema versioning

### Core Models & Relationships
- **User**: Authentication, gamification data, progress tracking
  - One-to-many: Enrollments, UserProgress, UserAchievements, QuizAttempts
- **Course**: Educational content container
  - One-to-many: Lessons, Quizzes, Enrollments
- **Lesson**: Individual learning units with content
  - One-to-many: UserProgress records
- **Quiz**: Assessments with Questions and Answers
  - One-to-many: Questions, QuizAttempts
- **Gamification Models**: Achievement, Badge, UserAchievement for rewards system

### Key Business Logic

#### Gamification System
- **Points**: Lesson completion (100), Quiz completion (150, score-based)
- **Levels**: 1-5 based on point thresholds (100, 500, 1500, 3000)
- **Achievements**: Triggered by point milestones or activity completion
- **Progress Tracking**: Per-lesson completion status with timestamps

#### User Progression Flow
1. User registers/logs in (`auth.py`)
2. Browses and enrolls in courses (`courses.py`)
3. Completes lessons → earns points → updates progress (`api.py`)
4. Takes quizzes → earns additional points based on score
5. Achievements automatically awarded via `check_achievements()`
6. Progress visible on dashboard and leaderboards

#### Route Organization
- **Main** (`/`): Homepage, dashboard, profile, static pages
- **Auth** (`/auth`): Login, register, logout
- **Courses** (`/courses`): Course listing, details, lesson viewing, enrollment
- **Gamification** (`/gamification`): Leaderboards, achievements display
- **API** (`/api`): AJAX endpoints for quiz submission, progress updates, search

### Database Configuration
- **Development**: SQLite (`ecolearn.db`)
- **Production**: PostgreSQL (via `DATABASE_URL` env var)
- **Testing**: In-memory SQLite (configured in `config.py`)

### Configuration Management
- **Environment-based configs**: Development, Production, Testing classes
- **Key settings**: Database URLs, secret keys, gamification point values
- **Feature flags**: Pagination limits, file upload constraints

### Sample Data Structure
The `init_db.py` script creates:
- Sample courses: Environmental Science, Climate Change, Sustainable Living, Renewable Energy
- Pre-built lessons with rich HTML content
- Quiz questions with multiple choice answers
- Achievement definitions and badge requirements
- Test user accounts (admin/admin123, student1/student123, student2/student123)

### Frontend Integration Points
- **Templates**: Jinja2 templates in organized subdirectories
- **Static Assets**: CSS/JS in `/static` with Bootstrap 5 framework
- **AJAX APIs**: Real-time progress updates, quiz submissions, search functionality
- **Flash Messages**: User feedback for actions (enrollment, completion, errors)

### Security & Authentication
- **Password Hashing**: Werkzeug's secure password hashing
- **Session Management**: Flask-Login with "remember me" functionality
- **Role-based Access**: Student/Educator/Admin roles with route protection
- **CSRF Protection**: Built into forms (can be disabled for testing via config)

### Extension Points
When adding new features, consider:
- **New Models**: Add to appropriate model file, create migration
- **New Routes**: Create new blueprint or extend existing ones
- **Gamification**: Update `check_achievements()` logic for new triggers
- **Points System**: Modify point values in `config.py`
- **Templates**: Follow existing template inheritance pattern

### Common Development Patterns
- Route functions return `render_template()` with context data
- Database operations wrapped in try/except with `db.session.commit()`
- User authentication via `@login_required` decorator
- Progress tracking via AJAX calls to `/api` endpoints
- Flash messages for user feedback on actions
- Pagination using SQLAlchemy's `paginate()` method
