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

root = Path(__file__).resolve().parent
shutil.copytree(root / 'static', root / 'public' / 'static', dirs_exist_ok=True)
with app.app_context():
    db.create_all()
    if Course.query.count() == 0:
        create_comprehensive_content()
    print('Database ready; static assets prepared.')
