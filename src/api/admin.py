from flask import Blueprint, request, jsonify, session
from src.services import supabase_service
from src.core.exceptions import AuthError, ValidationError

admin_bp = Blueprint('admin', __name__)

def is_admin():
    user = session.get('user')
    return user and user.get('role') == 'admin'

@admin_bp.before_request
def check_admin_access():
    if not is_admin():
        raise AuthError("Unauthorized access to admin features.")

@admin_bp.route('/api/admin/users', methods=['GET'])
def get_users():
    users = supabase_service.get_all_users()
    safe_users = [{'name': u['username'], 'email': u['email'], 'role': u['role']} for u in users]
    return jsonify({'users': safe_users})

@admin_bp.route('/api/admin/stats', methods=['GET'])
def get_stats():
    return jsonify(supabase_service.get_stats())

@admin_bp.route('/api/admin/users/delete', methods=['POST'])
def delete_user():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if email == 'admin@moodmusic.com':
        raise ValidationError("Cannot delete the root admin.")

    supabase_service.delete_user(email)
    return jsonify({'success': True, 'message': 'User deleted'})

@admin_bp.route('/api/admin/users/role', methods=['POST'])
def change_role():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    new_role = data.get('role', 'user')

    if email == 'admin@moodmusic.com':
        raise ValidationError("Cannot change root admin role.")

    if new_role not in ('admin', 'user'):
        raise ValidationError("Invalid role designated.")

    success = supabase_service.update_user_role(email, new_role)
    if success:
        return jsonify({'success': True, 'message': f'Role changed to {new_role}'})
    return jsonify({'success': False, 'message': 'User not found'}), 404
