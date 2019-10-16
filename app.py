from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

app = Flask(__name__)

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/XYearPlan')

client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
courses = db.courses
terms = db.terms

@app.route("/")
def courses_index():
    """Show all courses."""
    return render_template('terms_index.html', courses = courses.find(), terms = terms.find())

@app.route("/terms/courses/new")
def courses_new():
    """Create a new course."""
    return render_template("courses_new.html", course = {}, title = 'New Course')

@app.route("/terms/courses", methods=["POST"])
def courses_submit():
    """Submit a new course."""
    course = {
        'subject': request.form.get("course_subject"),
        'code': request.form.get("course_code"),
        'title': request.form.get("course_title"),
        'description': request.form.get("course_description")
    }
    course_id = courses.insert_one(course).inserted_id
    return redirect(url_for('courses_show', course_id = course_id))
    
@app.route("/terms/courses/<course_id>")
def courses_show(course_id):
    """Show a single course."""
    course = courses.find_one({'_id': ObjectId(course_id)})
    return render_template('courses_show.html', course = course)

@app.route('/courses/<course_id>', methods=['POST'])
def courses_update(course_id):
    """Submit an edited course."""
    updated_course = {
        'subject': request.form.get("course_subject"),
        'code': request.form.get("course_code"),
        'title': request.form.get("course_title"),
        'description': request.form.get("course_description")
    }
    courses.update_one(
        {'_id': ObjectId(course_id)},
        {'$set': updated_course})
    return redirect(url_for('courses_show', course_id = course_id))

@app.route("/terms/courses/<course_id>/edit")
def courses_edit(course_id):
    """Show the edit form for a course."""
    course = courses.find_one({'_id': ObjectId(course_id)})
    return render_template("courses_edit.html", course = course)

@app.route('/terms/courses/<course_id>/delete', methods=['POST'])
def courses_delete(course_id):
    """Delete one course."""
    courses.delete_one({'_id': ObjectId(course_id)})
    return redirect(url_for('courses_index'))

@app.route("/terms/new")
def terms_new():
    """Create a new term."""
    return render_template("terms_new.html", term = {}, title = 'New Term')

@app.route("/terms", methods=["POST"])
def terms_submit():
    """Submit a new term."""
    term = {
        'name': request.form.get("term_name"),
        'start_date': datetime.strptime(request.form.get("start_date"), '%Y-%m-%d'),
        'end_date': datetime.strptime(request.form.get("end_date"), '%Y-%m-%d')
    }
    term_id = terms.insert_one(term).inserted_id
    return redirect(url_for('terms_show', term_id = term_id))

@app.route("/terms/<term_id>")
def terms_show(term_id):
    """Show a single term."""
    term = terms.find_one({'_id': ObjectId(term_id)})
    return render_template('terms_show.html', term = term)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))