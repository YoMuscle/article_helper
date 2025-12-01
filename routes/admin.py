from flask import Blueprint, request, jsonify
from flask_login import current_user
from models import db, User, InviteCode
from functools import wraps
import os

bp = Blueprint('admin', __name__)


def admin_required(f):
    """管理員權限裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 檢查是否登入
        if not current_user.is_authenticated:
            return jsonify({"error": "請先登入"}), 401
        
        # 檢查是否為管理員
        admin_emails = os.getenv('ADMIN_EMAILS', '').lower().split(',')
        admin_emails = [e.strip() for e in admin_emails if e.strip()]
        
        if current_user.email.lower() not in admin_emails:
            return jsonify({"error": "您沒有管理員權限"}), 403
        
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/api/admin/users', methods=['GET'])
@admin_required
def list_users():
    """列出所有用戶"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            "users": [u.to_dict() for u in users],
            "total": len(users)
        }), 200
    except Exception as e:
        return jsonify({"error": f"取得用戶列表失敗: {str(e)}"}), 500


@bp.route('/api/admin/upgrade-user', methods=['POST'])
@admin_required
def upgrade_user():
    """升級用戶為 Premium"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "請提供用戶 Email"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": f"找不到用戶: {email}"}), 404
        
        if user.is_premium:
            return jsonify({"message": f"{email} 已經是 Premium 用戶"}), 200
        
        user.is_premium = True
        user.is_verified = True
        db.session.commit()
        
        return jsonify({
            "message": f"成功升級 {email} 為 Premium 用戶",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"升級失敗: {str(e)}"}), 500


@bp.route('/api/admin/downgrade-user', methods=['POST'])
@admin_required
def downgrade_user():
    """降級用戶（移除 Premium）"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "請提供用戶 Email"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": f"找不到用戶: {email}"}), 404
        
        if not user.is_premium:
            return jsonify({"message": f"{email} 不是 Premium 用戶"}), 200
        
        user.is_premium = False
        db.session.commit()
        
        return jsonify({
            "message": f"已移除 {email} 的 Premium 權限",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"降級失敗: {str(e)}"}), 500


@bp.route('/api/admin/invite-codes', methods=['GET'])
@admin_required
def list_invite_codes():
    """列出所有邀請碼"""
    try:
        codes = InviteCode.query.order_by(InviteCode.created_at.desc()).all()
        return jsonify({
            "codes": [c.to_dict() for c in codes],
            "total": len(codes),
            "unused": len([c for c in codes if not c.is_used])
        }), 200
    except Exception as e:
        return jsonify({"error": f"取得邀請碼列表失敗: {str(e)}"}), 500


@bp.route('/api/admin/invite-codes', methods=['POST'])
@admin_required
def create_invite_code():
    """產生新邀請碼"""
    try:
        data = request.get_json() or {}
        count = min(data.get('count', 1), 10)  # 最多一次產生 10 個
        
        codes = []
        for _ in range(count):
            invite = InviteCode.create()
            codes.append(invite.to_dict())
        
        return jsonify({
            "message": f"成功產生 {count} 個邀請碼",
            "codes": codes
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"產生邀請碼失敗: {str(e)}"}), 500


@bp.route('/api/admin/invite-codes/<code>', methods=['DELETE'])
@admin_required
def delete_invite_code(code):
    """刪除邀請碼"""
    try:
        invite = InviteCode.query.filter_by(code=code.upper()).first()
        if not invite:
            return jsonify({"error": "找不到此邀請碼"}), 404
        
        if invite.is_used:
            return jsonify({"error": "無法刪除已使用的邀請碼"}), 400
        
        db.session.delete(invite)
        db.session.commit()
        
        return jsonify({"message": "邀請碼已刪除"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"刪除失敗: {str(e)}"}), 500


# ===== 用戶兌換邀請碼 API（不需要管理員權限）=====

@bp.route('/api/redeem-code', methods=['POST'])
def redeem_invite_code():
    """用戶兌換邀請碼"""
    try:
        # 檢查是否登入
        if not current_user.is_authenticated:
            return jsonify({"error": "請先登入"}), 401
        
        data = request.get_json()
        code = data.get('code', '').strip().upper()
        
        if not code:
            return jsonify({"error": "請輸入邀請碼"}), 400
        
        # 查找邀請碼
        invite = InviteCode.query.filter_by(code=code).first()
        
        if not invite:
            return jsonify({"error": "邀請碼不存在"}), 404
        
        if invite.is_used:
            return jsonify({"error": "此邀請碼已被使用"}), 400
        
        if invite.expires_at and invite.expires_at < __import__('datetime').datetime.utcnow():
            return jsonify({"error": "此邀請碼已過期"}), 400
        
        if current_user.is_premium:
            return jsonify({"error": "您已經是 Premium 用戶"}), 400
        
        # 兌換
        if invite.redeem(current_user):
            return jsonify({
                "message": "恭喜！您已成功升級為 Premium 用戶！",
                "user": current_user.to_dict()
            }), 200
        else:
            return jsonify({"error": "兌換失敗，請稍後再試"}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"兌換失敗: {str(e)}"}), 500

