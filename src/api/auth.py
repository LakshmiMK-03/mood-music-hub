from flask import Blueprint, request, jsonify, session
import hashlib
from src.services import supabase_service
from src.core.exceptions import AuthError, ValidationError
from src.utils.logger import setup_logging

logger = setup_logging("auth_api")
auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([name, email, password]):
        raise ValidationError("All fields are required")

    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters")

    if supabase_service.get_user_by_email(email):
        raise ValidationError("Email already registered")

    if supabase_service.get_user_by_username(name):
        raise ValidationError("Username already taken")

    success = supabase_service.create_user(name, hash_password(password), email)
    
    if success:
        logger.info(f"Registered new user: {email}")
        return jsonify({'success': True, 'message': 'Registration successful!'})
    
    return jsonify({'success': False, 'message': 'Registration failed'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Hardcoded bypass for testing
    if email == "lakshmi@gmail.com" and password == "test123":
        logger.info(f"Hardcoded user logged in: {email}")
        session['user'] = {
            'id': 'hardcoded-test-id-12345',
            'name': 'Lakshmi (Admin)',
            'email': email,
            'role': 'admin'
        }
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': {'name': 'Lakshmi (Admin)', 'role': 'admin'}
        })

    user = supabase_service.get_user_by_email(email)

    if not user or user['password'] != hash_password(password):
        logger.warning(f"Failed login attempt: {email}")
        raise AuthError("Invalid email or password")

    role = user.get('role', 'user')
    session['user'] = {
        'id': user['id'], 
        'name': user['username'], 
        'email': user['email'], 
        'role': role
    }
    
    logger.info(f"User logged in: {email}")
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {'name': user['username'], 'role': role}
    })

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})
