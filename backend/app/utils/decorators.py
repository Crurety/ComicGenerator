from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JWT middleware already handles token validation
        # This decorator is for additional custom logic if needed
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        # Add admin check logic here
        # For now, we'll just pass through
        return f(*args, **kwargs)
    return decorated_function