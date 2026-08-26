import os
import sqlite3
import random
import json
import base64
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
import requests
from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, g, flash)
import click
from werkzeug.security import generate_password_hash, check_password_hash

# --- NEW: Advanced AI Model Imports ---
from transformers import pipeline
from PIL import Image

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_12345'
app.config['DATABASE'] = os.path.join(app.root_path, 'darpan.db')
app.config['UPLOAD_FOLDER_IMG'] = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER_VOICE'] = os.path.join('static', 'voice_notes')
os.makedirs(app.config['UPLOAD_FOLDER_IMG'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_VOICE'], exist_ok=True)

# --- NEW: AI Model Setup (Using OpenAI CLIP) ---
# Initialize the advanced zero-shot image classification pipeline.
# This model understands concepts, not just pre-defined classes.
# The first time you run the app, this will download the model files (approx. 1.7GB).
try:
    image_classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-large-patch14")
    print("AI Model (CLIP) loaded successfully.")
except Exception as e:
    print(f"Could not load AI model: {e}")
    image_classifier = None

def classify_image(image_path):
    """
    Classifies an image using the advanced CLIP model to determine
    if it contains a pothole or garbage.
    """
    if not image_classifier:
        # Fallback in case the model fails to load
        return "Other"
        
    try:
        # These are the concepts we want the model to check for.
        candidate_labels = ["a pothole in the road", "a pile of garbage", "a normal street", "a car", "a person"]
        
        # The model will score the image against each label.
        predictions = image_classifier(image_path, candidate_labels=candidate_labels)
        
        # Get the top prediction
        top_prediction = predictions[0]
        print(f"AI Prediction: {top_prediction['label']} (Score: {top_prediction['score']:.2f})")

        # Check if the top prediction is one of our target categories with reasonable confidence
        if top_prediction['label'] == "a pothole in the road" and top_prediction['score'] > 0.85:
            return "Pothole"
        if top_prediction['label'] == "a pile of garbage" and top_prediction['score'] > 0.85:
            return "Garbage"
            
        return "Other"
        
    except Exception as e:
        print(f"Error during AI classification: {e}")
        return "Other"

# --- Database Management (No Changes) ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM authorities WHERE username = ?", ('authority1',))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO authorities (username, password, city) VALUES (?, ?, ?)",
            ('authority1', generate_password_hash('password123'), 'Greater Noida')
        )
        db.commit()
    print("Initialized the database and added default authority.")

@app.cli.command('init-db')
def init_db_command():
    db_path = app.config['DATABASE']
    if os.path.exists(db_path):
        os.remove(db_path)
    schema_sql = """
    DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS issues; DROP TABLE IF EXISTS authorities; DROP TABLE IF EXISTS upvotes;
    CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, mobile_number TEXT UNIQUE NOT NULL, otp TEXT, otp_generated_at DATETIME);
    CREATE TABLE authorities (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, city TEXT NOT NULL);
    CREATE TABLE issues (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, category TEXT NOT NULL, description TEXT, latitude REAL NOT NULL, longitude REAL NOT NULL, city TEXT, image_path TEXT NOT NULL, voice_note_path TEXT, status TEXT NOT NULL DEFAULT 'Pending', upvotes INTEGER NOT NULL DEFAULT 1, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id));
    CREATE TABLE upvotes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, issue_id INTEGER NOT NULL, UNIQUE (user_id, issue_id), FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (issue_id) REFERENCES issues (id));
    """
    with open('schema.sql', 'w') as f: f.write(schema_sql)
    init_db()
    os.remove('schema.sql')
    click.echo('Database initialized.')

# --- Helper Functions (No Changes) ---
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1; dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)); r = 6371
    return c * r * 1000

# --- Routes (No Changes) ---
@app.route('/')
def index():
    return render_template('index.html')

# ==============================
# SMS / OTP CONFIGURATION
# ==============================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        mobile_number = request.form['mobile_number'].strip()

        # Basic validation
        if not mobile_number.isdigit() or len(mobile_number) != 10:
            flash('Please enter a valid 10-digit mobile number.', 'error')
            return redirect(url_for('register'))

        db = get_db()

        # Check if already registered
        existing_user = db.execute(
            'SELECT * FROM users WHERE mobile_number = ?',
            (mobile_number,)
        ).fetchone()

        if existing_user:
            flash('This mobile number is already registered. Please login.', 'error')
            return redirect(url_for('login'))

        # Create user
        db.execute(
            '''
            INSERT INTO users (mobile_number)
            VALUES (?)
            ''',
            (mobile_number,)
        )

        db.commit()

        # Log user in directly
        user = db.execute(
            'SELECT * FROM users WHERE mobile_number = ?',
            (mobile_number,)
        ).fetchone()

        session.clear()
        session['user_id'] = user['id']
        session['user_mobile'] = user['mobile_number']

        flash('Registration successful! Welcome to Darpan.', 'success')

        return redirect(url_for('user_dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        mobile_number = request.form['mobile_number'].strip()

        # Basic validation
        if not mobile_number.isdigit() or len(mobile_number) != 10:
            flash('Please enter a valid 10-digit mobile number.', 'error')
            return redirect(url_for('login'))

        db = get_db()

        user = db.execute(
            'SELECT * FROM users WHERE mobile_number = ?',
            (mobile_number,)
        ).fetchone()

        # User not found
        if not user:
            flash(
                'Mobile number not registered. Please register first.',
                'error'
            )
            return redirect(url_for('register'))

        # Login directly
        session.clear()

        session['user_id'] = user['id']
        session['user_mobile'] = user['mobile_number']

        flash('Login successful!', 'success')

        return redirect(url_for('user_dashboard'))

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    issues_from_db = db.execute('SELECT i.*, u.mobile_number FROM issues i JOIN users u ON i.user_id = u.id ORDER BY i.created_at DESC').fetchall()
    upvoted_issues = db.execute('SELECT issue_id FROM upvotes WHERE user_id = ?', (session['user_id'],)).fetchall()
    upvoted_issue_ids = list({row['issue_id'] for row in upvoted_issues})
    issues_data = []
    for row in issues_from_db:
        issue = dict(row)
        if isinstance(issue.get('created_at'), str):
             issue['created_at'] = datetime.strptime(issue['created_at'], '%Y-%m-%d %H:%M:%S')
        issues_data.append(issue)
    return render_template('user_dashboard.html', issues=issues_data, upvoted_issue_ids=upvoted_issue_ids)

@app.route('/report', methods=['GET'])
def report_issue_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('report_issue.html')

@app.route('/submit_issue', methods=['POST'])
def submit_issue():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    image_data = data['image_data_url'].split(',')[1]
    latitude = float(data['latitude']); longitude = float(data['longitude'])
    description = data.get('description', ''); city = "Greater Noida" 
    db = get_db()
    existing_issues = db.execute("SELECT * FROM issues WHERE status != 'Completed'").fetchall()
    for issue in existing_issues:
        distance = haversine(longitude, latitude, issue['longitude'], issue['latitude'])
        if distance < 50: return jsonify({'duplicate': True, 'issue_id': issue['id']})
    image_filename = f"issue_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    image_path = os.path.join(app.config['UPLOAD_FOLDER_IMG'], image_filename)
    with open(image_path, "wb") as fh: fh.write(base64.b64decode(image_data))
    category = classify_image(image_path)
    if category == "Other":
        os.remove(image_path)
        return jsonify({'error': 'The image could not be identified as a Pothole or Garbage. Please try a different angle.'}), 400
    voice_note_path = None
    if 'voice_data_url' in data and data['voice_data_url']:
        voice_data = data['voice_data_url'].split(',')[1]
        voice_filename = f"voice_{datetime.now().strftime('%Y%m%d%H%M%S')}.webm"
        voice_note_path = os.path.join(app.config['UPLOAD_FOLDER_VOICE'], voice_filename)
        with open(voice_note_path, "wb") as f: f.write(base64.b64decode(voice_data))
    cursor = db.cursor()
    cursor.execute("""INSERT INTO issues (user_id, category, description, latitude, longitude, city, image_path, voice_note_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (session['user_id'], category, description, latitude, longitude, city, image_path, voice_note_path))
    new_issue_id = cursor.lastrowid
    cursor.execute("INSERT INTO upvotes (user_id, issue_id) VALUES (?, ?)", (session['user_id'], new_issue_id))
    db.commit()
    return jsonify({'success': True, 'message': 'Issue reported successfully!'})
from datetime import datetime


@app.route('/issue/<int:issue_id>')
def issue_detail(issue_id):
    db = get_db()

    issue_row = db.execute(
        'SELECT * FROM issues WHERE id = ?',
        (issue_id,)
    ).fetchone()

    if issue_row is None:
        return "Issue not found", 404

    issue = dict(issue_row)

    if isinstance(issue.get('created_at'), str):
        issue['created_at'] = datetime.strptime(
            issue['created_at'],
            '%Y-%m-%d %H:%M:%S'
        )

    return render_template('issue_detail.html', issue=issue)

@app.route('/upvote/<int:issue_id>', methods=['POST'])
def upvote_issue(issue_id):
    if 'user_id' not in session: return jsonify({'error': 'You must be logged in to upvote'}), 401
    db = get_db()
    user_id = session['user_id']
    existing_upvote = db.execute("SELECT id FROM upvotes WHERE user_id = ? AND issue_id = ?", (user_id, issue_id)).fetchone()
    if existing_upvote: return jsonify({'error': 'You have already upvoted this issue'}), 400
    db.execute("INSERT INTO upvotes (user_id, issue_id) VALUES (?, ?)", (user_id, issue_id))
    db.execute("UPDATE issues SET upvotes = upvotes + 1 WHERE id = ?", (issue_id,))
    db.commit()
    new_count = db.execute("SELECT upvotes FROM issues WHERE id = ?", (issue_id,)).fetchone()['upvotes']
    return jsonify({'success': True, 'new_count': new_count})

@app.route('/authority/login', methods=['GET', 'POST'])
def authority_login():
    if request.method == 'POST':
        username = request.form['username']; password = request.form['password']
        db = get_db()
        authority = db.execute('SELECT * FROM authorities WHERE username = ?', (username,)).fetchone()
        if authority and check_password_hash(authority['password'], password):
            session['authority_id'] = authority['id']
            session['authority_city'] = authority['city']
            return redirect(url_for('authority_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('authority_login.html')

@app.route('/authority/dashboard')
def authority_dashboard():
    if 'authority_id' not in session: return redirect(url_for('authority_login'))
    city = session['authority_city']
    db = get_db()
    status_filter = request.args.get('status_filter', 'all')
    sort_by = request.args.get('sort_by', 'newest')
    query = f"SELECT * FROM issues WHERE city = ?"; params = [city]
    if status_filter != 'all': query += " AND status = ?"; params.append(status_filter)
    if sort_by == 'oldest': query += " ORDER BY created_at ASC"
    elif sort_by == 'upvotes': query += " ORDER BY upvotes DESC"
    else: query += " ORDER BY created_at DESC"
    issues_from_db = db.execute(query, tuple(params)).fetchall()
    issues = []
    for row in issues_from_db:
        issue = dict(row)
        if isinstance(issue.get('created_at'), str):
            issue['created_at'] = datetime.strptime(issue['created_at'], '%Y-%m-%d %H:%M:%S')
        issues.append(issue)
    return render_template('authority_dashboard.html', issues=issues, city=city, current_filter=status_filter, current_sort=sort_by)

@app.route('/authority/update_status/<int:issue_id>', methods=['POST'])
def update_status(issue_id):
    if 'authority_id' not in session: return redirect(url_for('authority_login'))
    new_status = request.form['status']; db = get_db()
    db.execute('UPDATE issues SET status = ? WHERE id = ?', (new_status, issue_id))
    db.commit()
    return redirect(url_for('authority_dashboard'))

@app.route('/authority/logout')
def authority_logout():
    session.pop('authority_id', None); session.pop('authority_city', None)
    return redirect(url_for('authority_login'))





if __name__ == '__main__':
    app.run(debug=True)