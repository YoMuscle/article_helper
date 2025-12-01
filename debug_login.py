"""
診斷登入問題的腳本
"""

from app import app, db
from models import User
import bcrypt

def check_user(email):
    """檢查使用者資料"""
    with app.app_context():
        user = User.query.filter_by(email=email.lower()).first()
        
        if not user:
            print(f"[ERROR] User not found: {email}")
            return None
        
        print(f"[INFO] User found:")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Is Verified: {user.is_verified}")
        print(f"  Has Password: {user.password_hash is not None}")
        print(f"  Has Google ID: {user.google_id is not None}")
        print(f"  Is Premium: {user.is_premium}")
        
        if user.password_hash:
            print(f"  Password Hash (first 20 chars): {user.password_hash[:20]}...")
        else:
            print(f"  Password Hash: None (Google-only user)")
        
        return user

def test_password(email, password):
    """測試密碼是否正確"""
    with app.app_context():
        user = User.query.filter_by(email=email.lower()).first()
        
        if not user:
            print(f"[ERROR] User not found: {email}")
            return False
        
        if not user.password_hash:
            print(f"[ERROR] User has no password (Google-only user)")
            return False
        
        # 測試密碼
        try:
            result = user.check_password(password)
            if result:
                print(f"[SUCCESS] Password is correct!")
            else:
                print(f"[FAILED] Password is incorrect!")
            return result
        except Exception as e:
            print(f"[ERROR] Password check failed: {e}")
            return False

def reset_password(email, new_password):
    """重設使用者密碼"""
    with app.app_context():
        user = User.query.filter_by(email=email.lower()).first()
        
        if not user:
            print(f"[ERROR] User not found: {email}")
            return False
        
        user.set_password(new_password)
        db.session.commit()
        print(f"[SUCCESS] Password reset for {email}")
        return True

def list_all_users():
    """列出所有使用者"""
    with app.app_context():
        users = User.query.all()
        print(f"\n[INFO] Total users: {len(users)}")
        for user in users:
            print(f"  - {user.email} (verified: {user.is_verified}, has_password: {user.password_hash is not None})")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python debug_login.py check <email>")
        print("  python debug_login.py test <email> <password>")
        print("  python debug_login.py reset <email> <new_password>")
        print("  python debug_login.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check' and len(sys.argv) >= 3:
        check_user(sys.argv[2])
    elif command == 'test' and len(sys.argv) >= 4:
        test_password(sys.argv[2], sys.argv[3])
    elif command == 'reset' and len(sys.argv) >= 4:
        reset_password(sys.argv[2], sys.argv[3])
    elif command == 'list':
        list_all_users()
    else:
        print("Invalid command or missing arguments")

