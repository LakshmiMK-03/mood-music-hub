from flask import Blueprint, render_template, session, redirect, current_app
from src.services import supabase_service
from src.core.constants import RELAXATION_DATA

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/analyze')
def analyze():
    if not session.get('user'):
        return redirect('/login')
    return render_template('analyze.html')

@views_bp.route('/music')
def music():
    return render_template('music.html')

@views_bp.route('/relaxation')
def relaxation():
    return render_template('relaxation.html')

@views_bp.route('/about')
def about():
    return render_template('about.html')

@views_bp.route('/contact')
def contact():
    return render_template('contact.html')

@views_bp.route('/login')
def login():
    return render_template('login.html')

@views_bp.route('/register')
def register():
    return render_template('register.html')

@views_bp.route('/admin')
def admin_panel():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin.html')

@views_bp.route('/api/relaxation/tips', methods=['GET'])
def get_relaxation_tips():
    user = session.get('user')
    last_emotion = session.get('last_emotion', 'Neutral')
    
    if user:
        db_emotion = supabase_service.get_latest_emotion(user.get('id'))
        if db_emotion: last_emotion = db_emotion

    data = RELAXATION_DATA.get(last_emotion, RELAXATION_DATA['Neutral'])
    return {
        'emotion': last_emotion,
        'tips': data['tips'],
        'affirmation': data['affirmation']
    }
