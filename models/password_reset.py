from datetime import datetime, timedelta
from . import db
import secrets


class PasswordReset(db.Model):
    """密碼重設模型"""
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    
    @staticmethod
    def generate_token():
        """產生隨機 token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_for_user(user_id, hours=1):
        """為使用者建立密碼重設 token"""
        token = PasswordReset.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=hours)
        reset = PasswordReset(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        return reset
    
    def is_expired(self):
        """檢查 token 是否過期"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """檢查 token 是否有效（未過期且未使用）"""
        return not self.used and not self.is_expired()
    
    def mark_as_used(self):
        """標記 token 為已使用"""
        self.used = True
    
    def __repr__(self):
        return f'<PasswordReset for User {self.user_id}>'

