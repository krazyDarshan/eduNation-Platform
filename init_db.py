#!/usr/bin/env python3
"""
Database initialization script for EcoLearn Platform
Adds sample courses, lessons, quizzes, and achievements
"""

from app import create_app, db
from app.models.course import Course, Lesson, Quiz, Question, Answer
from app.models.gamification import Achievement, Badge
from app.models.user import User

def init_sample_data():
    """Initialize database with sample educational content"""
    
    # Create achievements
    achievements = [
        Achievement(name="First Steps", description="Complete your first lesson", icon="fa-baby-carriage"),
        Achievement(name="Knowledge Seeker", description="Earn 500 points", icon="fa-book"),
        Achievement(name="Eco Warrior", description="Earn 1000 points", icon="fa-shield-alt"),
        Achievement(name="Environmental Expert", description="Earn 2500 points", icon="fa-graduation-cap"),
        Achievement(name="Green Champion", description="Complete 5 courses", icon="fa-trophy"),
    ]
    
    for achievement in achievements:
        db.session.add(achievement)
    
    # Create badges
    badges = [
        Badge(name="Beginner", description="Welcome to EcoLearn!", icon="fa-seedling", points_required=0),
        Badge(name="Learner", description="You're making progress!", icon="fa-leaf", points_required=100),
        Badge(name="Explorer", description="Keep exploring!", icon="fa-compass", points_required=500),
        Badge(name="Expert", description="You're an expert!", icon="fa-medal", points_required=1500),
        Badge(name="Master", description="Environmental master!", icon="fa-crown", points_required=3000),
    ]
    
    for badge in badges:
        db.session.add(badge)
    
    # Create sample courses
    course1 = Course(
        title="Introduction to Environmental Science",
        description="Learn the fundamentals of environmental science and understand the complex relationships between natural systems and human activities.",
        difficulty="beginner"
    )
    db.session.add(course1)
    
    course2 = Course(
        title="Climate Change Fundamentals",
        description="Explore the science behind climate change, its causes, impacts, and potential solutions for a sustainable future.",
        difficulty="intermediate"
    )
    db.session.add(course2)
    
    course3 = Course(
        title="Sustainable Living Practices",
        description="Discover practical ways to reduce your environmental footprint and live more sustainably in daily life.",
        difficulty="beginner"
    )
    db.session.add(course3)
    
    course4 = Course(
        title="Renewable Energy Systems",
        description="Deep dive into solar, wind, hydroelectric, and other renewable energy technologies shaping our future.",
        difficulty="advanced"
    )
    db.session.add(course4)
    
    db.session.commit()
    
    # Add lessons to Course 1
    lessons1 = [
        Lesson(
            course_id=course1.id,
            title="What is Environmental Science?",
            content="""
            <h3>Understanding Environmental Science</h3>
            <p>Environmental science is an interdisciplinary field that combines physical, biological, and information sciences to study the environment and solve environmental problems.</p>
            
            <h4>Key Components:</h4>
            <ul>
                <li><strong>Ecology:</strong> Study of interactions between organisms and their environment</li>
                <li><strong>Geology:</strong> Study of Earth's physical structure and processes</li>
                <li><strong>Atmospheric Science:</strong> Study of the atmosphere and weather patterns</li>
                <li><strong>Chemistry:</strong> Understanding chemical processes in the environment</li>
            </ul>
            
            <h4>Why It Matters:</h4>
            <p>Environmental science helps us understand how our actions affect the planet and how we can make better decisions for a sustainable future.</p>
            """,
            order=1
        ),
        Lesson(
            course_id=course1.id,
            title="The Importance of Environmental Protection",
            content="""
            <h3>Why Protect Our Environment?</h3>
            <p>Environmental protection is crucial for maintaining the health of our planet and ensuring the survival of all living organisms, including humans.</p>
            
            <h4>Benefits of Environmental Protection:</h4>
            <ul>
                <li>Clean air and water for human health</li>
                <li>Preservation of biodiversity</li>
                <li>Climate stability</li>
                <li>Sustainable resource availability</li>
                <li>Economic benefits from healthy ecosystems</li>
            </ul>
            
            <h4>Consequences of Environmental Degradation:</h4>
            <ul>
                <li>Air and water pollution</li>
                <li>Loss of biodiversity</li>
                <li>Climate change</li>
                <li>Resource depletion</li>
                <li>Health problems</li>
            </ul>
            """,
            order=2
        ),
        Lesson(
            course_id=course1.id,
            title="Basic Ecological Concepts",
            content="""
            <h3>Understanding Ecosystems</h3>
            <p>An ecosystem is a community of living organisms interacting with each other and their physical environment.</p>
            
            <h4>Key Concepts:</h4>
            <ul>
                <li><strong>Producers:</strong> Plants that make their own food through photosynthesis</li>
                <li><strong>Consumers:</strong> Animals that eat other organisms</li>
                <li><strong>Decomposers:</strong> Bacteria and fungi that break down dead material</li>
                <li><strong>Food Chains:</strong> Linear sequences showing who eats whom</li>
                <li><strong>Food Webs:</strong> Complex networks of interconnected food chains</li>
            </ul>
            
            <h4>Energy Flow:</h4>
            <p>Energy flows through ecosystems from the sun to producers, then to consumers, and finally to decomposers.</p>
            """,
            order=3
        )
    ]
    
    for lesson in lessons1:
        db.session.add(lesson)
    
    # Add lessons to Course 2
    lessons2 = [
        Lesson(
            course_id=course2.id,
            title="Understanding Global Warming",
            content="""
            <h3>What is Global Warming?</h3>
            <p>Global warming refers to the long-term increase in Earth's average surface temperature due to human activities and natural factors.</p>
            
            <h4>Main Causes:</h4>
            <ul>
                <li>Burning fossil fuels (coal, oil, gas)</li>
                <li>Deforestation</li>
                <li>Industrial processes</li>
                <li>Agriculture</li>
                <li>Transportation</li>
            </ul>
            
            <h4>Evidence of Global Warming:</h4>
            <ul>
                <li>Rising global temperatures</li>
                <li>Melting ice caps and glaciers</li>
                <li>Rising sea levels</li>
                <li>Changing weather patterns</li>
                <li>Ocean acidification</li>
            </ul>
            """,
            order=1
        ),
        Lesson(
            course_id=course2.id,
            title="The Greenhouse Effect Explained",
            content="""
            <h3>How the Greenhouse Effect Works</h3>
            <p>The greenhouse effect is a natural process that warms Earth's surface by trapping heat from the sun in the atmosphere.</p>
            
            <h4>Natural Greenhouse Effect:</h4>
            <ol>
                <li>Sun's energy reaches Earth</li>
                <li>Earth's surface absorbs energy and warms up</li>
                <li>Earth radiates heat back toward space</li>
                <li>Greenhouse gases trap some heat in the atmosphere</li>
                <li>This keeps Earth warm enough to support life</li>
            </ol>
            
            <h4>Enhanced Greenhouse Effect:</h4>
            <p>Human activities have increased greenhouse gas concentrations, trapping more heat and causing global warming.</p>
            
            <h4>Main Greenhouse Gases:</h4>
            <ul>
                <li>Carbon dioxide (CO₂) - 76%</li>
                <li>Methane (CH₄) - 16%</li>
                <li>Nitrous oxide (N₂O) - 6%</li>
                <li>Fluorinated gases - 2%</li>
            </ul>
            """,
            order=2
        )
    ]
    
    for lesson in lessons2:
        db.session.add(lesson)
    
    db.session.commit()
    
    # Add quizzes
    quiz1 = Quiz(
        course_id=course1.id,
        title="Environmental Science Basics Quiz",
        total_points=100
    )
    db.session.add(quiz1)
    
    quiz2 = Quiz(
        course_id=course2.id,
        title="Climate Change Knowledge Check",
        total_points=100
    )
    db.session.add(quiz2)
    
    db.session.commit()
    
    # Add questions for quiz 1
    q1 = Question(
        quiz_id=quiz1.id,
        text="What is environmental science?",
        order=1
    )
    db.session.add(q1)
    
    q2 = Question(
        quiz_id=quiz1.id,
        text="Which of the following is a producer in an ecosystem?",
        order=2
    )
    db.session.add(q2)
    
    # Add questions for quiz 2
    q3 = Question(
        quiz_id=quiz2.id,
        text="What is the main cause of global warming?",
        order=1
    )
    db.session.add(q3)
    
    db.session.commit()
    
    # Add answers
    answers = [
        # Q1 answers
        Answer(question_id=q1.id, text="Study of only plants and animals", is_correct=False),
        Answer(question_id=q1.id, text="Interdisciplinary field studying the environment", is_correct=True),
        Answer(question_id=q1.id, text="Study of only weather patterns", is_correct=False),
        Answer(question_id=q1.id, text="Study of only pollution", is_correct=False),
        
        # Q2 answers
        Answer(question_id=q2.id, text="Lion", is_correct=False),
        Answer(question_id=q2.id, text="Mushroom", is_correct=False),
        Answer(question_id=q2.id, text="Green plants", is_correct=True),
        Answer(question_id=q2.id, text="Bacteria", is_correct=False),
        
        # Q3 answers
        Answer(question_id=q3.id, text="Natural climate variation", is_correct=False),
        Answer(question_id=q3.id, text="Burning fossil fuels", is_correct=True),
        Answer(question_id=q3.id, text="Solar radiation changes", is_correct=False),
        Answer(question_id=q3.id, text="Volcanic activity", is_correct=False),
    ]
    
    for answer in answers:
        db.session.add(answer)
    
    # Create admin user
    admin = User(
        username="admin",
        email="admin@ecolearn.com",
        first_name="Admin",
        last_name="User",
        role="admin",
        total_points=5000,
        level=5
    )
    admin.set_password("admin123")
    db.session.add(admin)
    
    # Create sample students
    student1 = User(
        username="student1",
        email="student1@example.com",
        first_name="Alice",
        last_name="Johnson",
        role="student",
        total_points=750,
        level=3
    )
    student1.set_password("student123")
    db.session.add(student1)
    
    student2 = User(
        username="student2",
        email="student2@example.com",
        first_name="Bob",
        last_name="Smith",
        role="student",
        total_points=1200,
        level=3
    )
    student2.set_password("student123")
    db.session.add(student2)
    
    db.session.commit()
    print("✅ Sample data initialized successfully!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        init_sample_data()
