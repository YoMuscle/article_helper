"""
升級使用者為付費會員的腳本
使用方式: python upgrade_user.py
"""

from app import app, db
from models import User


def upgrade_to_premium(email):
    """將指定 email 的使用者升級為付費會員"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"[ERROR] User not found: {email}")
            return False
        
        if user.is_premium:
            print(f"[INFO] User {email} is already premium")
            return True
        
        user.is_premium = True
        db.session.commit()
        
        print(f"[SUCCESS] Upgraded {email} to premium!")
        print(f"  Username: {user.username}")
        print(f"  Created at: {user.created_at}")
        return True


if __name__ == '__main__':
    # 升級指定使用者
    upgrade_to_premium('ntustcs110@gmail.com')

