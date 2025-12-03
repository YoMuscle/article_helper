from functools import wraps
from flask import jsonify, redirect, url_for, flash
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


def premium_required(f):
    """裝飾器：需要使用者為 Premium 會員（用於 API）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "需要登入才能使用此功能"}), 401
        if not current_user.is_verified:
            return jsonify({"error": "請先驗證您的 email 地址"}), 403
        if not current_user.is_premium:
            return jsonify({"error": "此功能僅限 Premium 會員使用"}), 403
        return f(*args, **kwargs)
    return decorated_function


def premium_required_page(f):
    """裝飾器：需要使用者為 Premium 會員（用於頁面，會重導向）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/')
        if not current_user.is_verified:
            return redirect('/')
        if not current_user.is_premium:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

