from app import create_app

app = create_app()

@app.route('/test')
def test():
    return "Hello! Flask is working!"

@app.route('/test-db')
def test_db():
    from app.models.course import Course
    courses = Course.query.all()
    return f"Found {len(courses)} courses in database"

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
