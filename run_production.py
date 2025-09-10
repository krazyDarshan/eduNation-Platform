"""
Production runner for eduNation Platform
Tests the production setup locally before deployment
"""
import os
import subprocess
import sys

def run_production():
    """Run the application in production mode using gunicorn"""
    
    # Set environment variables for production testing
    os.environ['FLASK_ENV'] = 'production'
    
    print("🚀 Starting eduNation in production mode...")
    print("📍 Application will be available at: http://127.0.0.1:8000")
    print("🔧 Using gunicorn with 2 workers")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Run gunicorn
        subprocess.run([
            'gunicorn',
            '--bind', '127.0.0.1:8000',
            '--workers', '2',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            'run:app'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Production server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting production server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_production()
