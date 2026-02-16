from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from emotion_model import analyze_text, analyze_image_emotion
import os
import json
import hashlib
from dotenv import load_dotenv
from youtube_client import YouTubeClient

load_dotenv()
youtube_client = YouTubeClient()

app = Flask(__name__)
app.secret_key = 'mood-music-hub-secret-key-2025'
CORS(app)

# Ensure directories exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize users file with default admin
if not os.path.exists(USERS_FILE):
    default_admin = {
        'name': 'Admin',
        'email': 'admin@moodmusic.com',
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin'
    }
    with open(USERS_FILE, 'w') as f:
        json.dump([default_admin], f, indent=2)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

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

    users = load_users()

    # Check if email already exists
    if any(u['email'] == email for u in users):
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    # Create user (default role: user)
    users.append({
        'name': name,
        'email': email,
        'password': hash_password(password),
        'role': 'user'
    })
    save_users(users)

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

    users = load_users()
    user = next((u for u in users if u['email'] == email), None)

    if not user or user['password'] != hash_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    role = user.get('role', 'user')
    session['user'] = {'name': user['name'], 'email': user['email'], 'role': role}
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {'name': user['name'], 'role': role}
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
    users = load_users()
    # Return users without passwords
    safe_users = [{'name': u['name'], 'email': u['email'], 'role': u.get('role', 'user')} for u in users]
    return jsonify({'users': safe_users})


@app.route('/api/admin/users/delete', methods=['POST'])
def api_admin_delete_user():
    """Delete a user (admin only)."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if email == 'admin@moodmusic.com':
        return jsonify({'success': False, 'message': 'Cannot delete the default admin'}), 400

    users = load_users()
    users = [u for u in users if u['email'] != email]
    save_users(users)
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

    users = load_users()
    for u in users:
        if u['email'] == email:
            u['role'] = new_role
            break
    save_users(users)
    return jsonify({'success': True, 'message': f'Role changed to {new_role}'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
