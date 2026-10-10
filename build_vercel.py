"""Prepare static assets and initialize a new production database."""
import os
import shutil
from pathlib import Path

if not os.environ.get('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL must be configured before deploying')
if not os.environ.get('SECRET_KEY'):
    raise RuntimeError('SECRET_KEY must be configured before deploying')

from run import app, db
from app.models.course import Course
from enhanced_db_init import create_comprehensive_content
from sqlalchemy import inspect, text
from app.models.gamification import Achievement, Badge

root = Path(__file__).resolve().parent
shutil.copytree(root / 'static', root / 'public' / 'static', dirs_exist_ok=True)
with app.app_context():
    db.create_all()
    # create_all does not alter existing columns. Preserve accounts while
    # widening legacy password storage for Werkzeug's current hash format.
    if db.engine.dialect.name == 'postgresql':
        column = next(c for c in inspect(db.engine).get_columns('user') if c['name'] == 'password_hash')
        if getattr(column['type'], 'length', None) is not None:
            db.session.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE TEXT'))
            db.session.commit()
    if Course.query.count() == 0:
        create_comprehensive_content()
    for name, description, icon in [
        ('First Steps', 'Complete your first lesson', 'fa-seedling'),
        ('Knowledge Seeker', 'Earn 500 points', 'fa-book'),
        ('Eco Warrior', 'Earn 1000 points', 'fa-shield-alt'),
        ('Environmental Expert', 'Earn 2500 points', 'fa-graduation-cap'),
        ('Green Champion', 'Complete 5 courses', 'fa-trophy'),
    ]:
        if not Achievement.query.filter_by(name=name).first():
            db.session.add(Achievement(name=name, description=description, icon=icon))
    for name, points, icon in [('Beginner', 0, 'fa-seedling'), ('Learner', 100, 'fa-leaf'),
                               ('Explorer', 500, 'fa-compass'), ('Expert', 1500, 'fa-medal'),
                               ('Master', 3000, 'fa-crown')]:
        if not Badge.query.filter_by(name=name).first():
            db.session.add(Badge(name=name, description=f'Earn {points} points',
                                points_required=points, icon=icon))
    db.session.commit()
    print('Database ready; static assets prepared.')
