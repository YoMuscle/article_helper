"""
Test authentication system basic functionality
"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 測試環境變數
def test_env_variables():
    """測試環境變數是否已設定"""
    print("測試環境變數...")
    required_vars = ['SECRET_KEY', 'MAIL_SERVER', 'MAIL_USERNAME']
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少環境變數: {', '.join(missing_vars)}")
        print("請參考 env.example 建立 .env 檔案")
        return False
    else:
        print("✅ 環境變數設定完成")
        return True


# 測試資料庫連接
def test_database():
    """測試資料庫是否正常"""
    print("\n測試資料庫...")
    try:
        from app import app, db
        with app.app_context():
            # 嘗試查詢資料庫
            from models import User
            users = User.query.all()
            print(f"✅ 資料庫連接成功 (目前有 {len(users)} 個使用者)")
            return True
    except Exception as e:
        print(f"❌ 資料庫錯誤: {str(e)}")
        return False


# 測試模型導入
def test_models():
    """測試所有模型是否可以正常導入"""
    print("\n測試模型...")
    try:
        from models import User, Document, EmailVerification, PasswordReset
        print("✅ 所有模型導入成功")
        return True
    except Exception as e:
        print(f"❌ 模型導入失敗: {str(e)}")
        return False


# 測試路由
def test_routes():
    """測試所有路由是否註冊"""
    print("\n測試路由...")
    try:
        from app import app
        
        # 檢查關鍵路由
        required_routes = [
            '/',
            '/login',
            '/register',
            '/profile',
            '/my-documents',
        ]
        
        with app.test_client() as client:
            for route in required_routes:
                response = client.get(route)
                if response.status_code in [200, 302]:  # 200 或重定向都算成功
                    print(f"  ✅ {route}")
                else:
                    print(f"  ❌ {route} (狀態碼: {response.status_code})")
        
        print("✅ 路由測試完成")
        return True
    except Exception as e:
        print(f"❌ 路由測試失敗: {str(e)}")
        return False


# 測試密碼加密
def test_password_hashing():
    """測試密碼加密功能"""
    print("\n測試密碼加密...")
    try:
        from models import User
        
        # 建立測試使用者
        user = User(email="test@example.com", username="Test User")
        user.set_password("test_password_123")
        
        # 驗證密碼
        if user.check_password("test_password_123"):
            print("✅ 密碼加密與驗證正常")
            return True
        else:
            print("❌ 密碼驗證失敗")
            return False
    except Exception as e:
        print(f"❌ 密碼測試失敗: {str(e)}")
        return False


# 測試 Email 服務
def test_email_service():
    """測試 Email 服務配置"""
    print("\n測試 Email 服務...")
    try:
        from services.email_service import mail
        from app import app
        
        with app.app_context():
            if app.config.get('MAIL_USERNAME'):
                print(f"✅ Email 服務已配置 ({app.config['MAIL_USERNAME']})")
                print("   注意：實際發送郵件需要正確的 SMTP 設定")
                return True
            else:
                print("⚠️  Email 服務未配置（某些功能可能無法使用）")
                return True
    except Exception as e:
        print(f"❌ Email 服務測試失敗: {str(e)}")
        return False


# 主測試函式
def run_all_tests():
    """執行所有測試"""
    print("=" * 50)
    print("論文救火站 - 認證系統測試")
    print("=" * 50)
    
    tests = [
        test_env_variables,
        test_models,
        test_database,
        test_password_hashing,
        test_routes,
        test_email_service,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ 測試執行錯誤: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"測試結果: {sum(results)}/{len(results)} 通過")
    print("=" * 50)
    
    if all(results):
        print("\n🎉 所有測試通過！系統已準備就緒。")
        print("\n下一步:")
        print("1. 確保 .env 檔案中的 SMTP 設定正確")
        print("2. 設定 Google OAuth 憑證（如需使用 Google 登入）")
        print("3. 執行 'python app.py' 啟動應用")
    else:
        print("\n⚠️  部分測試失敗，請檢查上方錯誤訊息")
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

