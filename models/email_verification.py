from datetime import datetime, timedelta
from . import db
import secrets


class EmailVerification(db.Model):
    """Email 驗證模型"""
    __tablename__ = 'email_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @staticmethod
    def generate_token():
        """產生隨機 token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_for_user(user_id, hours=24):
        """為使用者建立驗證 token"""
        token = EmailVerification.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=hours)
        verification = EmailVerification(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        return verification
    
    def is_expired(self):
        """檢查 token 是否過期"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<EmailVerification for User {self.user_id}>'

