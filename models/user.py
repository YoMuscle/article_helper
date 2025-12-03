from datetime import datetime
from flask_login import UserMixin
from . import db
import bcrypt


class User(UserMixin, db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Google OAuth 使用者可能沒有密碼
    username = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    theme_preference = db.Column(db.String(50), default='modern-light', nullable=False)  # 主題偏好
    is_premium = db.Column(db.Boolean, default=False, nullable=False)  # 是否為付費會員
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關聯
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    email_verifications = db.relationship('EmailVerification', backref='user', lazy=True, cascade='all, delete-orphan')
    password_resets = db.relationship('PasswordReset', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    task_tags = db.relationship('TaskTag', backref='user', lazy=True, cascade='all, delete-orphan')
    goal_statistics = db.relationship('GoalStatistics', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """設定密碼（使用 bcrypt 加密）"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """驗證密碼"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_verified': self.is_verified,
            'has_google_login': self.google_id is not None,
            'theme_preference': self.theme_preference,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

