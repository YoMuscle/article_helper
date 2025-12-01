from datetime import datetime
import secrets
from . import db


class InviteCode(db.Model):
    """邀請碼模型 - 用於升級用戶為 Premium"""
    __tablename__ = 'invite_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    used_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # None = 永不過期
    
    # 關聯
    used_by = db.relationship('User', backref='used_invite_code', foreign_keys=[used_by_id])
    
    @classmethod
    def generate_code(cls, length=12):
        """產生隨機邀請碼"""
        # 產生易讀的邀請碼（大寫字母+數字，排除容易混淆的字符）
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @classmethod
    def create(cls, expires_at=None):
        """建立新邀請碼"""
        code = cls.generate_code()
        # 確保唯一
        while cls.query.filter_by(code=code).first():
            code = cls.generate_code()
        
        invite = cls(code=code, expires_at=expires_at)
        db.session.add(invite)
        db.session.commit()
        return invite
    
    def is_valid(self):
        """檢查邀請碼是否有效"""
        if self.is_used:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def redeem(self, user):
        """兌換邀請碼"""
        if not self.is_valid():
            return False
        
        self.is_used = True
        self.used_by_id = user.id
        self.used_at = datetime.utcnow()
        user.is_premium = True
        user.is_verified = True  # 同時驗證 email
        db.session.commit()
        return True
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'code': self.code,
            'is_used': self.is_used,
            'used_by': self.used_by.email if self.used_by else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_valid': self.is_valid()
        }

