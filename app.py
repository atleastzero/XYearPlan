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
    return render_template('terms_index.html', 
                courses = courses.find().sort([("subject", 1), ("code", 1)]), 
                terms = terms.find().sort([("start_date", 1), ("end_date", 1)]))

@app.route("/terms/courses/new")
def courses_new():
    """Create a new course."""
    return render_template("courses_new.html", course = {}, title = 'New Course',
                terms = terms.find().sort([("start_date", 1), ("end_date", 1)]))

@app.route("/terms/courses", methods=["POST"])
def courses_submit():
    """Submit a new course."""
    term = request.form.get("course_term")
    course = { 
        'subject': request.form.get("course_subject"),
        'code': request.form.get("course_code"),
        'title': request.form.get("course_title"),
        'description': request.form.get("course_description"), 
        'credits': request.form.get("course_credits"),
        'term': term
    }
    course_id = courses.insert_one(course).inserted_id

    if term != "Unassigned":
        term_id = terms.find({'name': term})[0]['_id']
        terms.update(
            {"_id": term_id}, 
            {"$push": {'courses': ObjectId(course_id)}})

    return redirect(url_for('courses_show', course_id = course_id))
    
@app.route("/terms/courses/<course_id>")
def courses_show(course_id):
    """Show a single course."""
    course = courses.find_one({'_id': ObjectId(course_id)})
    term_id = "Unassigned"
    if course['term'] != "Unassigned":
        term_id = terms.find({'name': course['term']})[0]['_id']
    return render_template('courses_show.html', course = course, term_id = term_id)

@app.route('/terms/courses/<course_id>', methods=['POST'])
def courses_update(course_id):
    """Submit an edited course."""

    term = request.form.get("course_term")
    updated_course = {
        'subject': request.form.get("course_subject"),
        'code': request.form.get("course_code"),
        'title': request.form.get("course_title"),
        'description': request.form.get("course_description"), 
        'credits': request.form.get("course_credits"),
        'term': term
    }
    courses.update_one(
        {'_id': ObjectId(course_id)},
        {'$set': updated_course})

    if term != "Unassigned":
        term_id = terms.find({'name': term})[0]['_id']
        terms.update(
            {"_id": term_id}, 
            {"$push": {'courses': {ObjectId(course_id)}}})

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
        'end_date': datetime.strptime(request.form.get("end_date"), '%Y-%m-%d'),
        'courses': []
    }
    term_id = terms.insert_one(term).inserted_id
    return redirect(url_for('terms_show', term_id = term_id))

@app.route("/terms/<term_id>")
def terms_show(term_id):
    """Show a single term."""
    term = terms.find_one({'_id': ObjectId(term_id)})
    term_courses = []
    for course in term['courses']:
        term_courses.append(courses.find_one({'_id': course}))
    return render_template('terms_show.html', term = term, 
            course_ids = term['courses'], term_courses = term_courses, 
            number = len(term_courses))

@app.route('/terms/<term_id>', methods=['POST'])
def terms_update(term_id):
    """Submit an edited term."""
    updated_term = {
        'name': request.form.get("term_name"),
        'start_date': datetime.strptime(request.form.get("start_date"), '%Y-%m-%d'),
        'end_date': datetime.strptime(request.form.get("end_date"), '%Y-%m-%d')
    }
    terms.update_one(
        {'_id': ObjectId(term_id)},
        {'$set': updated_term})
    return redirect(url_for('terms_show', term_id = term_id))

@app.route("/terms/<term_id>/edit")
def terms_edit(term_id):
    """Show the edit form for a term."""
    term = terms.find_one({'_id': ObjectId(term_id)})
    return render_template("terms_edit.html", term = term)

@app.route('/terms/<term_id>/delete', methods=['POST'])
def terms_delete(term_id):
    """Delete one term."""
    terms.delete_one({'_id': ObjectId(term_id)})
    return redirect(url_for('courses_index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))