from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, current_user
from models import db, User, EmailVerification, PasswordReset
from services.email_service import send_verification_email, send_password_reset_email, send_welcome_email
from utils.decorators import login_required
import re
import os
from authlib.integrations.flask_client import OAuth

bp = Blueprint('auth', __name__)
oauth = OAuth()


def init_oauth(app):
    """初始化 OAuth"""
    oauth.init_app(app)
    
    # 註冊 Google OAuth
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    return oauth


def validate_email(email):
    """驗證 email 格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """驗證密碼強度（至少 8 個字元）"""
    return len(password) >= 8


@bp.route('/api/auth/register', methods=['POST'])
def register():
    """使用者註冊"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        username = data.get('username', '').strip()
        
        # 驗證輸入
        if not email or not password or not username:
            return jsonify({"error": "請填寫所有必填欄位"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Email 格式不正確"}), 400
        
        if not validate_password(password):
            return jsonify({"error": "密碼至少需要 8 個字元"}), 400
        
        # 檢查 email 是否已註冊
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "此 Email 已被註冊"}), 400
        
        # 建立新使用者
        user = User(email=email, username=username)
        user.set_password(password)
        
        # 開發模式：自動驗證使用者
        dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
        if dev_mode:
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                "message": "註冊成功！（開發模式：已自動驗證）",
                "user": user.to_dict()
            }), 201
        
        # 正式模式：需要 email 驗證
        db.session.add(user)
        db.session.commit()
        
        # 建立驗證 token 並發送驗證郵件
        verification = EmailVerification.create_for_user(user.id)
        db.session.add(verification)
        db.session.commit()
        
        # 發送驗證郵件
        email_sent = send_verification_email(user.email, user.username, verification.token)
        
        if email_sent:
            return jsonify({
                "message": "註冊成功！請檢查您的 email 收件匣以完成驗證。",
                "user": user.to_dict()
            }), 201
        else:
            return jsonify({
                "message": "註冊成功！但驗證郵件發送失敗，請稍後從個人資料頁面重新發送。",
                "user": user.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"註冊失敗: {str(e)}"}), 500


@bp.route('/api/auth/login', methods=['POST'])
def login():
    """使用者登入"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "請填寫 Email 和密碼"}), 400
        
        # 查找使用者
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Email 或密碼錯誤"}), 401
        
        # 登入使用者
        login_user(user, remember=True)
        
        return jsonify({
            "message": "登入成功",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"登入失敗: {str(e)}"}), 500


@bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """使用者登出"""
    try:
        logout_user()
        return jsonify({"message": "登出成功"}), 200
    except Exception as e:
        return jsonify({"error": f"登出失敗: {str(e)}"}), 500


@bp.route('/api/auth/user', methods=['GET'])
@login_required
def get_current_user():
    """取得當前使用者資訊"""
    try:
        return jsonify({"user": current_user.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": f"取得使用者資訊失敗: {str(e)}"}), 500


@bp.route('/api/auth/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新個人資料"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        theme_preference = data.get('theme_preference', '').strip()
        
        # 更新使用者名稱
        if username:
            current_user.username = username
        
        # 更新主題偏好
        if theme_preference:
            # 驗證主題名稱
            valid_themes = ['modern-light', 'modern-dark', 'vibrant', 'academic', 'nature']
            if theme_preference in valid_themes:
                current_user.theme_preference = theme_preference
            else:
                return jsonify({"error": "無效的主題名稱"}), 400
        
        db.session.commit()
        
        return jsonify({
            "message": "個人資料更新成功",
            "user": current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500


@bp.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密碼"""
    try:
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({"error": "請填寫舊密碼和新密碼"}), 400
        
        # 驗證舊密碼
        if not current_user.check_password(old_password):
            return jsonify({"error": "舊密碼錯誤"}), 401
        
        # 驗證新密碼強度
        if not validate_password(new_password):
            return jsonify({"error": "新密碼至少需要 8 個字元"}), 400
        
        # 更新密碼
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({"message": "密碼修改成功"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"密碼修改失敗: {str(e)}"}), 500


@bp.route('/api/auth/resend-verification', methods=['POST'])
@login_required
def resend_verification():
    """重新發送驗證郵件"""
    try:
        if current_user.is_verified:
            return jsonify({"error": "您的帳號已經驗證過了"}), 400
        
        # 刪除舊的未使用驗證 token
        EmailVerification.query.filter_by(user_id=current_user.id).delete()
        
        # 建立新的驗證 token
        verification = EmailVerification.create_for_user(current_user.id)
        db.session.add(verification)
        db.session.commit()
        
        # 發送驗證郵件
        email_sent = send_verification_email(current_user.email, current_user.username, verification.token)
        
        if email_sent:
            return jsonify({"message": "驗證郵件已重新發送，請檢查您的收件匣"}), 200
        else:
            return jsonify({"error": "驗證郵件發送失敗，請稍後再試"}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"發送失敗: {str(e)}"}), 500


# Google OAuth 路由
@bp.route('/api/auth/google')
def google_login():
    """導向 Google 登入頁面"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/api/auth/google/callback')
def google_callback():
    """Google OAuth 回調處理"""
    try:
        # 取得 Google 的 token
        token = oauth.google.authorize_access_token()
        
        # 取得使用者資訊
        user_info = token.get('userinfo')
        if not user_info:
            return redirect('/?error=google_auth_failed')
        
        email = user_info.get('email')
        google_id = user_info.get('sub')
        username = user_info.get('name', email.split('@')[0])
        
        # 查找或建立使用者
        user = User.query.filter_by(email=email).first()
        
        if user:
            # 使用者已存在，更新 Google ID
            if not user.google_id:
                user.google_id = google_id
                user.is_verified = True  # Google 帳號視為已驗證
                db.session.commit()
        else:
            # 建立新使用者
            user = User(
                email=email,
                username=username,
                google_id=google_id,
                is_verified=True  # Google 帳號視為已驗證
            )
            db.session.add(user)
            db.session.commit()
            
            # 發送歡迎郵件
            send_welcome_email(user.email, user.username)
        
        # 登入使用者
        login_user(user, remember=True)
        
        return redirect('/')
        
    except Exception as e:
        print(f"Google OAuth 錯誤: {str(e)}")
        return redirect('/?error=google_auth_failed')


@bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """請求密碼重設"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "請輸入 Email"}), 400
        
        # 查找使用者
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # 為了安全，即使使用者不存在也回傳成功訊息
            return jsonify({"message": "如果該 Email 已註冊，您將收到密碼重設郵件"}), 200
        
        # 如果使用者只使用 Google 登入，沒有密碼
        if not user.password_hash:
            return jsonify({"error": "您使用 Google 帳號登入，無法重設密碼"}), 400
        
        # 刪除舊的未使用重設 token
        PasswordReset.query.filter_by(user_id=user.id, used=False).delete()
        
        # 建立新的重設 token
        reset = PasswordReset.create_for_user(user.id)
        db.session.add(reset)
        db.session.commit()
        
        # 發送密碼重設郵件
        email_sent = send_password_reset_email(user.email, user.username, reset.token)
        
        if email_sent:
            return jsonify({"message": "如果該 Email 已註冊，您將收到密碼重設郵件"}), 200
        else:
            return jsonify({"error": "郵件發送失敗，請稍後再試"}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"處理失敗: {str(e)}"}), 500


@bp.route('/api/auth/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """重設密碼"""
    try:
        data = request.get_json()
        new_password = data.get('password', '')
        
        if not new_password:
            return jsonify({"error": "請輸入新密碼"}), 400
        
        if not validate_password(new_password):
            return jsonify({"error": "密碼至少需要 8 個字元"}), 400
        
        # 查找 token
        reset = PasswordReset.query.filter_by(token=token).first()
        
        if not reset or not reset.is_valid():
            return jsonify({"error": "無效或已過期的重設連結"}), 400
        
        # 更新密碼
        user = User.query.get(reset.user_id)
        if not user:
            return jsonify({"error": "使用者不存在"}), 404
        
        user.set_password(new_password)
        reset.mark_as_used()
        db.session.commit()
        
        return jsonify({"message": "密碼重設成功，請使用新密碼登入"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"重設失敗: {str(e)}"}), 500


@bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """驗證 email"""
    try:
        # 查找驗證 token
        verification = EmailVerification.query.filter_by(token=token).first()
        
        if not verification:
            return render_template('verify_result.html', 
                                 success=False, 
                                 message="無效的驗證連結")
        
        if verification.is_expired():
            return render_template('verify_result.html', 
                                 success=False, 
                                 message="驗證連結已過期，請重新發送驗證郵件")
        
        # 驗證使用者
        user = User.query.get(verification.user_id)
        if not user:
            return render_template('verify_result.html', 
                                 success=False, 
                                 message="使用者不存在")
        
        if user.is_verified:
            return render_template('verify_result.html', 
                                 success=True, 
                                 message="您的帳號已經驗證過了")
        
        user.is_verified = True
        db.session.delete(verification)
        db.session.commit()
        
        return render_template('verify_result.html', 
                             success=True, 
                             message="Email 驗證成功！您現在可以使用所有功能了。")
        
    except Exception as e:
        db.session.rollback()
        return render_template('verify_result.html', 
                             success=False, 
                             message=f"驗證失敗: {str(e)}")

