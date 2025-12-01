
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, current_user
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

# 載入環境變數
load_dotenv()

# 匯入模型和服務
from models import db, User, Document, VisitorCount
from services.document_analyzer import DocumentAnalyzer
from services.email_service import init_mail
from routes.auth import init_oauth
from utils.decorators import login_required, verified_required

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app, supports_credentials=True)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# 資料庫配置（支援多種環境變數名稱）
database_url = (
    os.getenv('DATABASE_URL') or 
    os.getenv('POSTGRES_URI') or 
    os.getenv('POSTGRESQL_URI') or 
    'sqlite:///apa_checker.db'
)
# 處理 PostgreSQL URL 格式
if database_url.startswith('postgres://'):
    # 使用 psycopg3 驅動（postgresql+psycopg://）
    database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://') and '+' not in database_url.split('://')[0]:
    # 將 postgresql:// 改為 postgresql+psycopg://
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"[INIT] Database: {database_url[:50]}...")

# Email 配置
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

# 初始化擴展
db.init_app(app)
init_mail(app)
oauth = init_oauth(app)

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 建立資料庫表
with app.app_context():
    db.create_all()
    
    # 從環境變數自動升級 Premium 用戶
    premium_emails = os.getenv('PREMIUM_EMAILS', '')
    if premium_emails:
        for email in premium_emails.split(','):
            email = email.strip().lower()
            if email:
                user = User.query.filter_by(email=email).first()
                if user and not user.is_premium:
                    user.is_premium = True
                    user.is_verified = True  # 也自動驗證
                    db.session.commit()
                    print(f"[INIT] Upgraded {email} to premium")

# 註冊 blueprints
from routes.citation import bp as citation_bp
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
app.register_blueprint(citation_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# 文件上傳設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'doc', 'docx'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/analyze_document', methods=['POST'])
def analyze_document():
    """分析文件（可選登入：登入則保存記錄，未登入則僅返回結果）"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "沒有上傳文件"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "沒有選擇文件"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加時間戳避免文件名衝突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 根據是否登入決定文件名
            if current_user.is_authenticated:
                unique_filename = f"{current_user.id}_{timestamp}_{filename}"
            else:
                unique_filename = f"guest_{timestamp}_{filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            try:
                analyzer = DocumentAnalyzer()
                result = analyzer.analyze_document(file_path)
                
                # 使用者成功分析文件，增加使用次數
                VisitorCount.increment()
                
                # 如果使用者已登入且驗證，儲存文件記錄
                if current_user.is_authenticated and current_user.is_verified:
                    document = Document(
                        user_id=current_user.id,
                        filename=filename,
                        analysis_result=result
                    )
                    db.session.add(document)
                    db.session.commit()
                    result['document_id'] = document.id
                    result['saved'] = True
                else:
                    result['saved'] = False
                    if not current_user.is_authenticated:
                        result['message'] = '登入以保存分析記錄'
                    elif not current_user.is_verified:
                        result['message'] = '請先驗證 email 以保存記錄'
                
                # 刪除臨時文件
                os.remove(file_path)
                
                return jsonify(result)
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({"error": str(e)}), 500
        return jsonify({"error": "不支持的文件格式，請上傳 .doc 或 .docx 文件"}), 400
    except Exception as e:
        return jsonify({"error": f"處理請求時發生錯誤: {str(e)}"}), 500

@app.route('/api/documents', methods=['GET'])
@login_required
def get_user_documents():
    """取得當前使用者的所有文件"""
    try:
        documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_time.desc()).all()
        return jsonify({
            "documents": [doc.to_dict() for doc in documents]
        }), 200
    except Exception as e:
        return jsonify({"error": f"取得文件列表失敗: {str(e)}"}), 500

@app.route('/api/documents/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    """取得特定文件（只能取得自己的）"""
    try:
        document = Document.query.filter_by(id=document_id, user_id=current_user.id).first()
        if not document:
            return jsonify({"error": "文件不存在或無權限存取"}), 404
        return jsonify({"document": document.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": f"取得文件失敗: {str(e)}"}), 500

@app.route('/api/documents/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """刪除文件（只能刪除自己的）"""
    try:
        document = Document.query.filter_by(id=document_id, user_id=current_user.id).first()
        if not document:
            return jsonify({"error": "文件不存在或無權限刪除"}), 404
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({"message": "文件已刪除"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"刪除文件失敗: {str(e)}"}), 500

@app.route('/')
def index():
    # 只取得目前計數，不增加（計數在使用功能時才增加）
    visitor_count = VisitorCount.get_count()
    return render_template('index.html', visitor_count=visitor_count)

@app.route('/api/visitor-count', methods=['GET'])
def get_visitor_count():
    """取得目前使用次數（計數只在使用 Citation 產生或文檔分析功能時增加）"""
    count = VisitorCount.get_count()
    return jsonify({"count": count})

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/my-documents')
def my_documents_page():
    return render_template('my_documents.html')

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>')
def reset_password_page(token):
    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    # 從環境變數讀取配置，適用於雲端部署
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
