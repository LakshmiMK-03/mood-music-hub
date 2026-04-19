from flask import jsonify
from src.core.exceptions import AppError

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({'error': 'Resource not found', 'status': 404}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': 'An unexpected internal server error occurred', 'status': 500}), 500
