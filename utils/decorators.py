from functools import wraps
from flask import jsonify
from flask_login import current_user


def login_required(f):
    """裝飾器：需要使用者登入"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "需要登入才能使用此功能"}), 401
        return f(*args, **kwargs)
    return decorated_function


def verified_required(f):
    """裝飾器：需要使用者已驗證 email"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "需要登入才能使用此功能"}), 401
        if not current_user.is_verified:
            return jsonify({"error": "請先驗證您的 email 地址"}), 403
        return f(*args, **kwargs)
    return decorated_function

