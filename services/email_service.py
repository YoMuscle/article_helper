from flask import current_app, render_template, request
from flask_mail import Mail, Message
import os

mail = Mail()


def init_mail(app):
    """初始化郵件服務"""
    mail.init_app(app)


def get_app_url():
    """
    取得應用程式 URL，優先順序：
    1. APP_URL 環境變數
    2. 從當前請求自動偵測
    3. 預設 localhost
    """
    app_url = os.getenv('APP_URL')
    if app_url:
        return app_url.rstrip('/')
    
    # 嘗試從請求中獲取
    try:
        # request.host_url 包含 scheme 和 host，例如 "https://example.com/"
        return request.host_url.rstrip('/')
    except RuntimeError:
        # 不在 request context 中
        return 'http://localhost:5000'


def send_verification_email(user_email, username, verification_token):
    """發送 Email 驗證郵件"""
    app_url = get_app_url()
    verification_url = f"{app_url}/verify-email/{verification_token}"
    
    subject = "論文救火站 - 請驗證您的 Email"
    
    # HTML 版本
    html_body = f"""
    <html>
    <body style="font-family: 'Microsoft JhengHei', sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 30px; border-radius: 10px;">
            <h2 style="color: #007BFF;">歡迎來到論文救火站！</h2>
            <p>親愛的 {username}，</p>
            <p>感謝您註冊論文救火站。請點擊下方按鈕來驗證您的 email 地址：</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #007BFF; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    驗證 Email
                </a>
            </div>
            <p>或複製以下連結到瀏覽器：</p>
            <p style="word-break: break-all; color: #666;">{verification_url}</p>
            <p style="margin-top: 30px; color: #999; font-size: 14px;">
                此驗證連結將在 24 小時後過期。<br>
                如果您沒有註冊論文救火站，請忽略此郵件。
            </p>
        </div>
    </body>
    </html>
    """
    
    # 純文字版本
    text_body = f"""
    歡迎來到論文救火站！
    
    親愛的 {username}，
    
    感謝您註冊論文救火站。請點擊以下連結來驗證您的 email 地址：
    
    {verification_url}
    
    此驗證連結將在 24 小時後過期。
    如果您沒有註冊論文救火站，請忽略此郵件。
    """
    
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"發送驗證郵件失敗: {str(e)}")
        return False


def send_password_reset_email(user_email, username, reset_token):
    """發送密碼重設郵件"""
    app_url = get_app_url()
    reset_url = f"{app_url}/reset-password/{reset_token}"
    
    subject = "論文救火站 - 重設密碼"
    
    # HTML 版本
    html_body = f"""
    <html>
    <body style="font-family: 'Microsoft JhengHei', sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 30px; border-radius: 10px;">
            <h2 style="color: #007BFF;">重設您的密碼</h2>
            <p>親愛的 {username}，</p>
            <p>我們收到了重設您密碼的請求。請點擊下方按鈕來設定新密碼：</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #007BFF; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    重設密碼
                </a>
            </div>
            <p>或複製以下連結到瀏覽器：</p>
            <p style="word-break: break-all; color: #666;">{reset_url}</p>
            <p style="margin-top: 30px; color: #999; font-size: 14px;">
                此重設連結將在 1 小時後過期。<br>
                如果您沒有請求重設密碼，請忽略此郵件，您的密碼將保持不變。
            </p>
        </div>
    </body>
    </html>
    """
    
    # 純文字版本
    text_body = f"""
    重設您的密碼
    
    親愛的 {username}，
    
    我們收到了重設您密碼的請求。請點擊以下連結來設定新密碼：
    
    {reset_url}
    
    此重設連結將在 1 小時後過期。
    如果您沒有請求重設密碼，請忽略此郵件，您的密碼將保持不變。
    """
    
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"發送密碼重設郵件失敗: {str(e)}")
        return False


def send_welcome_email(user_email, username):
    """發送歡迎郵件（給 Google OAuth 使用者）"""
    app_url = get_app_url()
    subject = "歡迎來到論文救火站！"
    
    # HTML 版本
    html_body = f"""
    <html>
    <body style="font-family: 'Microsoft JhengHei', sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 30px; border-radius: 10px;">
            <h2 style="color: #007BFF;">歡迎來到論文救火站！</h2>
            <p>親愛的 {username}，</p>
            <p>感謝您使用 Google 帳號註冊論文救火站。您的帳號已經準備就緒！</p>
            <p>您現在可以使用以下功能：</p>
            <ul>
                <li>上傳並分析 Word 文檔的 APA 引用格式</li>
                <li>查看您的文檔歷史記錄</li>
                <li>產生標準的 APA Citation</li>
            </ul>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{app_url}" 
                   style="background-color: #007BFF; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    開始使用
                </a>
            </div>
            <p style="margin-top: 30px; color: #999; font-size: 14px;">
                祝您論文寫作順利！
            </p>
        </div>
    </body>
    </html>
    """
    
    # 純文字版本
    text_body = f"""
    歡迎來到論文救火站！
    
    親愛的 {username}，
    
    感謝您使用 Google 帳號註冊論文救火站。您的帳號已經準備就緒！
    
    祝您論文寫作順利！
    """
    
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"發送歡迎郵件失敗: {str(e)}")
        return False

