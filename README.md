# EcoLearn - Gamified Environmental Education Platform

A comprehensive web application built with Flask that provides gamified environmental education for students and colleges. The platform combines interactive learning with gamification elements to create an engaging educational experience.

## 🌿 Features

### Core Features
- **User Authentication**: Registration, login, and role-based access (Student/Educator)
- **Course Management**: Browse, enroll, and track progress through environmental courses
- **Interactive Lessons**: Rich content with multimedia support
- **Quizzes & Assessments**: Test knowledge with interactive quizzes
- **Gamification System**: Points, badges, achievements, and leaderboards
- **Progress Tracking**: Detailed analytics on learning progress
- **Responsive Design**: Professional UI that works on all devices

### Gamification Elements
- **Points System**: Earn points for completing lessons and quizzes
- **Level System**: Progress through levels based on accumulated points
- **Achievements**: Unlock badges for reaching milestones
- **Leaderboards**: Compete with other learners globally
- **Progress Visualization**: Track your learning journey

### Educational Content
- **Climate Change**: Understanding global warming and its impacts
- **Sustainable Living**: Practical tips for eco-friendly lifestyle
- **Renewable Energy**: Solar, wind, and other clean energy sources
- **Waste Management**: Recycling, reduction, and responsible disposal
- **Biodiversity**: Protecting ecosystems and wildlife
- **Environmental Policy**: Understanding environmental regulations

## 🚀 Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login, Bcrypt
- **Database ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/EcoLearn-Platform.git
   cd EcoLearn-Platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///ecolearn.db
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 🗂️ Project Structure

```
EcoLearn-Platform/
├── app/
│   ├── models/             # Database models
│   │   ├── user.py        # User, Enrollment, UserProgress models
│   │   ├── course.py      # Course, Lesson, Quiz models
│   │   └── gamification.py # Achievement, Badge models
│   ├── routes/            # Route handlers
│   │   ├── main.py        # Main application routes
│   │   ├── auth.py        # Authentication routes
│   │   ├── courses.py     # Course management routes
│   │   ├── gamification.py # Gamification features
│   │   └── api.py         # AJAX API endpoints
│   ├── utils/             # Utility functions
│   └── __init__.py        # Application factory
├── static/
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Static images
├── templates/             # Jinja2 templates
│   ├── auth/              # Authentication templates
│   ├── courses/           # Course-related templates
│   ├── main/              # Main application templates
│   └── base.html          # Base template
├── migrations/            # Database migration files
├── config.py              # Configuration settings
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 📊 Database Schema

### Key Models
- **User**: User accounts with authentication and gamification data
- **Course**: Educational courses with metadata
- **Lesson**: Individual lessons within courses
- **Quiz**: Assessments with questions and answers
- **Enrollment**: User enrollment in courses
- **UserProgress**: Tracks lesson completion
- **Achievement**: Available achievements and badges
- **UserAchievement**: User's earned achievements

## 🎮 Gamification System

### Points System
- **Lesson Completion**: 100 points
- **Quiz Completion**: 150 points (based on score)
- **Course Completion**: Bonus points

### Level System
- **Level 1**: 0-99 points (Beginner)
- **Level 2**: 100-499 points (Learner)
- **Level 3**: 500-1499 points (Explorer)
- **Level 4**: 1500-2999 points (Expert)
- **Level 5**: 3000+ points (Champion)

### Achievements
- **First Steps**: Complete your first lesson
- **Knowledge Seeker**: Earn 500 points
- **Eco Warrior**: Earn 1000 points
- **Environmental Expert**: Earn 2500 points

## 🌱 Sample Content

The platform comes with sample environmental education content including:

1. **Introduction to Environmental Science**
   - What is Environmental Science?
   - The Importance of Environmental Protection
   - Basic Ecological Concepts

2. **Climate Change Fundamentals**
   - Understanding Global Warming
   - Greenhouse Effect Explained
   - Impact on Weather Patterns

3. **Sustainable Living Practices**
   - Reducing Your Carbon Footprint
   - Sustainable Transportation
   - Energy Conservation at Home

## 🚀 Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Environment Variables for Production
```
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and commit: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌍 Environmental Impact

This platform is designed to educate and inspire action on environmental issues. By providing gamified learning experiences, we aim to:

- Increase environmental awareness among students
- Promote sustainable lifestyle choices
- Build a community of environmental advocates
- Provide educators with engaging teaching tools

## 📞 Support

For support, email support@ecolearn-platform.com or create an issue in the GitHub repository.

## 🏆 Acknowledgments

- Bootstrap for the responsive UI framework
- Font Awesome for icons
- Flask community for the excellent web framework
- Environmental educators who inspired this platform

---

**Made with 💚 for a sustainable future**
