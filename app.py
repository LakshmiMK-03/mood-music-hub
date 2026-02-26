from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from emotion_model import analyze_text, analyze_image_emotion
from analytics import log_analysis, get_stats
import os
import json
import hashlib
from dotenv import load_dotenv
from youtube_client import YouTubeClient

from database import (
    get_user_by_email, create_user, get_all_users, 
    delete_user, update_user_role, get_db_connection
)

load_dotenv()
youtube_client = YouTubeClient()

app = Flask(__name__)
app.secret_key = 'mood-music-hub-secret-key-2025'
CORS(app)

# Ensure directories exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_admin():
    """Check if the current session user is an admin."""
    user = session.get('user')
    if not user:
        return False
    return user.get('role') == 'admin'


# ===== Page Routes =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    return render_template('analyze.html')

@app.route('/music')
def music():
    return render_template('music.html')

@app.route('/relaxation')
def relaxation():
    return render_template('relaxation.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admin')
def admin_panel():
    if not is_admin():
        return redirect('/login')
    return render_template('admin.html')


# ===== API Endpoints =====

@app.route('/api/analyze/text', methods=['POST'])
def api_analyze_text():
    """
    Analyze text input for emotion and stress level.
    Expects JSON: { "text": "user input text" }
    Returns: { "emotion", "stress_level", "confidence" }
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text'].strip()
    if not text:
        return jsonify({'error': 'Text cannot be empty'}), 400

    result = analyze_text(text)
    
    # Log analysis result
    log_analysis('text', text, result['emotion'], result['stress_level'], result['confidence'], result.get('stress_score', 0.0))
    
    return jsonify(result)


@app.route('/api/analyze/image', methods=['POST'])
def api_analyze_image():
    """
    Analyze uploaded face image for emotion.
    Expects: multipart form with 'image' file
    Returns: { "emotion", "stress_level", "confidence", "face_detected" }
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    # Save temporarily
    temp_path = os.path.join(UPLOAD_FOLDER, 'temp_face.jpg')
    file.save(temp_path)

    try:
        result = analyze_image_emotion(temp_path)
        
        # Log analysis result
        if result.get('face_detected'):
            log_analysis('image', None, result['emotion'], result['stress_level'], result['confidence'], result.get('stress_score', 0.0))
            
        return jsonify(result)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/contact', methods=['POST'])
def api_contact():
    """
    Handle contact form submission.
    Expects JSON: { "name", "email", "message" }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not all([name, email, message]):
        return jsonify({'error': 'All fields are required'}), 400

    # In production, save to database or send email
    print(f"Contact form: {name} ({email}): {message}")

    return jsonify({'success': True, 'message': 'Feedback received successfully!'})


@app.route('/api/register', methods=['POST'])
def api_register():
    """
    Register a new user.
    Expects JSON: { "name", "email", "password" }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([name, email, password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Check if email already exists
    if get_user_by_email(email):
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    # Create user (default role: user)
    success = create_user(name, hash_password(password), email, 'user')
    
    if success:
        return jsonify({'success': True, 'message': 'Registration successful!'})
    else:
        return jsonify({'success': False, 'message': 'Database error during registration'}), 500

    return jsonify({'success': True, 'message': 'Registration successful!'})


@app.route('/api/login', methods=['POST'])
def api_login():
    """
    Login a user.
    Expects JSON: { "email", "password" }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = get_user_by_email(email)

    if not user or user['password'] != hash_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    role = user.get('role', 'user')
    session['user'] = {'name': user['username'], 'email': user['email'], 'role': role}
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {'name': user['username'], 'role': role}
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({'success': True})



@app.route('/api/music/recommend', methods=['POST'])
def api_music_recommend():
    """
    Get music recommendations based on emotion.
    Expects JSON: { "emotion": "Happy" }
    """
    data = request.get_json()
    emotion = data.get('emotion', 'Neutral')
    languages = data.get('languages', [])
    
    videos = youtube_client.search_music(emotion, languages)
    return jsonify({'videos': videos})


# ===== Admin API Endpoints =====

@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    """Get all registered users (admin only)."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    users = get_all_users()
    # Map 'username' from DB to 'name' for frontend compatibility
    safe_users = [{'name': u['username'], 'email': u['email'], 'role': u['role']} for u in users]
    return jsonify({'users': safe_users})


@app.route('/api/admin/stats', methods=['GET'])
def api_admin_stats():
    """Get aggregated analytics stats (admin only)."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = get_stats()
    
    # User counts from SQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    admin_users = cursor.fetchone()[0]
    conn.close()

    stats['user_counts'] = {
        'total': total_users,
        'admins': admin_users,
        'users': total_users - admin_users
    }
    
    return jsonify(stats)


@app.route('/api/admin/users/delete', methods=['POST'])
def api_admin_delete_user():
    """Delete a user (admin only)."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if email == 'admin@moodmusic.com':
        return jsonify({'success': False, 'message': 'Cannot delete the default admin'}), 400

    delete_user(email)
    return jsonify({'success': True, 'message': 'User deleted'})


@app.route('/api/admin/users/role', methods=['POST'])
def api_admin_change_role():
    """Change a user's role (admin only)."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    email = data.get('email', '').strip().lower()
    new_role = data.get('role', 'user')

    if email == 'admin@moodmusic.com':
        return jsonify({'success': False, 'message': 'Cannot change default admin role'}), 400

    if new_role not in ('admin', 'user'):
        return jsonify({'success': False, 'message': 'Invalid role'}), 400

    success = update_user_role(email, new_role)
    if success:
        return jsonify({'success': True, 'message': f'Role changed to {new_role}'})
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
