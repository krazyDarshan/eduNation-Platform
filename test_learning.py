import os
os.environ['DATABASE_URL']='sqlite:///:memory:'
os.environ['SECRET_KEY']='test-only'
import unittest
from app import create_app, db
from config import TestingConfig
from app.models.user import User, Enrollment, UserProgress
from app.models.course import Course, Lesson, Quiz, Question, Answer, QuizAttempt
from app.models.gamification import Achievement

class LearningTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app(TestingConfig)
        self.ctx=self.app.app_context(); self.ctx.push(); db.create_all()
        course=Course(title='Test Course', description='Test'); db.session.add(course); db.session.flush()
        lesson=Lesson(course_id=course.id,title='Test Lesson',content='Test')
        quiz=Quiz(course_id=course.id,title='Test Quiz'); db.session.add_all([lesson,quiz]); db.session.flush()
        q=Question(quiz_id=quiz.id,text='Question'); db.session.add(q); db.session.flush()
        db.session.add_all([Answer(question_id=q.id,text='Yes',is_correct=True),Answer(question_id=q.id,text='No'),Achievement(name='First Steps',description='Complete a lesson')]); db.session.commit()
        self.client=self.app.test_client()
        self.form=dict(username='learner',email='learner@example.com',first_name='Test',last_name='Learner',password='test-password-123',confirm_password='test-password-123')
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop()
    def sign_in(self):
        self.assertEqual(self.client.post('/auth/register',data=self.form).status_code,302)
        self.assertEqual(self.client.post('/auth/login',data=dict(username='LEARNER@EXAMPLE.COM',password=self.form['password']),follow_redirects=True).status_code,200)
    def test_registration_and_login(self):
        self.sign_in()
        user=User.query.one(); self.assertGreater(len(user.password_hash),120); self.assertTrue(user.check_password(self.form['password']))
        self.assertIsNone(getattr(User.__table__.c.password_hash.type,'length',None))
        self.client.get('/auth/logout')
        r=self.client.post('/auth/login?next=https://example.com',data=dict(username='learner',password=self.form['password']))
        self.assertEqual(r.location,'/dashboard')
        self.client.get('/auth/logout')
        r=self.client.post('/auth/register',data={**self.form,'username':' LEARNER '})
        self.assertIn(b'Username already exists',r.data)
        self.assertEqual(User.query.count(),1)
        self.assertIn(b'Invalid username or password',self.client.post('/auth/login',data=dict(username='learner',password='wrong')).data)
    def test_validation(self):
        for change in [dict(first_name='a'*51),dict(email='bad'),dict(role='admin'),dict(confirm_password='wrong')]:
            self.client.post('/auth/register',data={**self.form,**change})
            self.assertEqual(User.query.count(),0)
    def test_learning_flow(self):
        self.sign_in()
        self.assertEqual(self.client.post('/api/lesson/1/progress',json={}).status_code,403)
        self.assertEqual(self.client.post('/courses/1/enroll',follow_redirects=True).status_code,200)
        self.assertEqual(self.client.post('/courses/1/enroll').status_code,302)
        self.assertEqual(Enrollment.query.count(),1)
        self.assertEqual(self.client.get('/courses/1/lessons/1').status_code,200)
        self.assertEqual(self.client.post('/courses/1/lessons/1/complete',follow_redirects=True).status_code,200)
        self.assertEqual(User.query.one().total_points,100)
        self.assertTrue(Enrollment.query.one().is_completed)
        self.assertEqual(User.query.one().get_course_progress(1),100)
        r=self.client.post('/api/lesson/1/progress',json={'completed':True})
        self.assertEqual(r.json['points_earned'],0)
        self.assertEqual(r.json['progress_percentage'],100)
        self.assertEqual(User.query.one().achievements.count(),1)
        self.assertEqual(self.client.post('/api/quiz/1/submit',json={'answers':{'1':'bad'}}).status_code,400)
        self.assertEqual(self.client.post('/courses/1/quiz/1/submit',data={'q1':'1'}).status_code,200)
        self.assertEqual(QuizAttempt.query.count(),1)
        self.assertEqual(User.query.one().total_points,250)
        r=self.client.post('/api/quiz/1/submit',json={'answers':{'1':'1'}})
        self.assertEqual(r.json['points_earned'],0)
        self.assertEqual(User.query.one().total_points,250)
        for path in ['/','/courses/','/courses/1','/courses/1/quiz/1','/dashboard','/profile','/gamification/leaderboard','/gamification/achievements','/gamification/api/user-stats','/api/search?q=Test']:
            self.assertEqual(self.client.get(path).status_code,200,path)
    def test_quiz_retake_improves_once(self):
        self.sign_in(); self.client.post('/courses/1/enroll')
        self.client.post('/courses/1/quiz/1/submit',data={'q1':'2'})
        self.assertEqual(User.query.one().total_points,0)
        self.client.post('/courses/1/quiz/1/submit',data={'q1':'1'})
        self.assertEqual(User.query.one().total_points,150)
        self.assertEqual(QuizAttempt.query.one().score,1)

if __name__=='__main__': unittest.main(verbosity=2)
