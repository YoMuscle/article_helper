# 變更日誌 - Feature: User Authentication

## 版本 2.0.0 - 使用者認證系統 (feature/user-authentication 分支)

### 🎉 新增功能

#### 使用者認證
- ✅ Email + 密碼註冊與登入系統
- ✅ Google OAuth 2.0 整合（快速登入）
- ✅ Email 驗證機制（註冊後需驗證才能使用進階功能）
- ✅ 密碼重設功能（忘記密碼）
- ✅ 個人資料管理（修改使用者名稱、密碼）
- ✅ 重新發送驗證郵件功能

#### 文件管理
- ✅ 文件上傳需要登入且驗證
- ✅ 使用者文件隔離（每個使用者只能看到自己的文件）
- ✅ 文件歷史記錄查看
- ✅ 儲存分析結果到資料庫
- ✅ 文件刪除功能
- ✅ 我的文件列表頁面

#### 安全性增強
- ✅ 密碼使用 bcrypt 加密
- ✅ Session 管理使用 Flask-Login
- ✅ Token 安全生成（Email 驗證、密碼重設）
- ✅ 權限控制裝飾器（@login_required, @verified_required）

#### 前端界面
- ✅ 響應式導航列（顯示登入狀態）
- ✅ 登入頁面（支援 Email/密碼 + Google 登入）
- ✅ 註冊頁面（支援 Email/密碼 + Google 登入）
- ✅ 個人資料頁面（修改名稱、密碼）
- ✅ 我的文件列表頁面（查看歷史記錄）
- ✅ 忘記密碼頁面
- ✅ 重設密碼頁面
- ✅ Email 驗證結果頁面
- ✅ 未驗證提示（可重新發送驗證郵件）

### 📁 新增檔案

#### 後端
- `models/__init__.py` - 模型套件初始化
- `models/user.py` - 使用者模型
- `models/document.py` - 文件模型
- `models/email_verification.py` - Email 驗證模型
- `models/password_reset.py` - 密碼重設模型
- `routes/auth.py` - 認證相關路由
- `services/email_service.py` - 郵件服務
- `utils/__init__.py` - 工具套件初始化
- `utils/decorators.py` - 權限控制裝飾器

#### 前端
- `templates/login.html` - 登入頁面
- `templates/register.html` - 註冊頁面
- `templates/profile.html` - 個人資料頁面
- `templates/my_documents.html` - 我的文件列表
- `templates/forgot_password.html` - 忘記密碼頁面
- `templates/reset_password.html` - 重設密碼頁面
- `templates/verify_result.html` - Email 驗證結果

#### 配置與文檔
- `env.example` - 環境變數範例
- `.gitignore` - Git 忽略檔案
- `README.md` - 專案說明
- `SETUP_GUIDE.md` - 詳細設置指南
- `QUICKSTART.md` - 快速開始指南
- `CHANGELOG.md` - 變更日誌
- `test_auth_system.py` - 系統測試腳本
- `uploads/.gitkeep` - 確保 uploads 目錄被追蹤

### 🔧 修改檔案

#### `app.py`
- 整合 Flask-Login、Flask-SQLAlchemy、Flask-Mail
- 添加環境變數載入（python-dotenv）
- 初始化資料庫和 OAuth
- 添加使用者載入器
- 修改 `/api/analyze_document` 路由（需登入+驗證）
- 新增文件管理 API：
  - `GET /api/documents` - 取得使用者文件列表
  - `GET /api/documents/<id>` - 取得特定文件
  - `DELETE /api/documents/<id>` - 刪除文件
- 新增頁面路由（登入、註冊、個人資料等）

#### `requirements.txt`
- 新增 Flask-Login==0.6.3
- 新增 Flask-SQLAlchemy==3.1.1
- 新增 Flask-Mail==0.10.0
- 新增 Authlib==1.3.0
- 新增 bcrypt==4.2.0
- 新增 python-dotenv==1.0.1

#### `templates/index.html`
- 添加導航列（顯示登入狀態、使用者選單）
- 添加未驗證提示橫幅
- 添加登入狀態檢查功能
- 修改文檔分析功能（需檢查登入+驗證）
- 添加從我的文件頁面返回查看文件的功能
- 整合登出功能

#### `.gitignore`
- 更新忽略規則（Python、Flask、資料庫、環境變數等）

### 🗄️ 資料庫架構

#### users 表
```sql
- id (INTEGER, 主鍵)
- email (VARCHAR(120), 唯一, 索引)
- password_hash (VARCHAR(255))
- username (VARCHAR(100))
- is_verified (BOOLEAN, 預設 False)
- google_id (VARCHAR(100), 唯一, 索引)
- created_at (DATETIME)
- updated_at (DATETIME)
```

#### documents 表
```sql
- id (INTEGER, 主鍵)
- user_id (INTEGER, 外鍵 → users.id, 索引)
- filename (VARCHAR(255))
- upload_time (DATETIME)
- analysis_result (JSON)
```

#### email_verifications 表
```sql
- id (INTEGER, 主鍵)
- user_id (INTEGER, 外鍵 → users.id, 索引)
- token (VARCHAR(100), 唯一, 索引)
- expires_at (DATETIME)
- created_at (DATETIME)
```

#### password_resets 表
```sql
- id (INTEGER, 主鍵)
- user_id (INTEGER, 外鍵 → users.id, 索引)
- token (VARCHAR(100), 唯一, 索引)
- expires_at (DATETIME)
- used (BOOLEAN, 預設 False)
- created_at (DATETIME)
```

### 🔐 API 端點

#### 認證 API
- `POST /api/auth/register` - 註冊
- `POST /api/auth/login` - 登入
- `POST /api/auth/logout` - 登出
- `GET /api/auth/user` - 取得當前使用者資訊
- `PUT /api/auth/profile` - 更新個人資料
- `POST /api/auth/change-password` - 修改密碼
- `POST /api/auth/resend-verification` - 重新發送驗證郵件
- `GET /verify-email/<token>` - Email 驗證
- `POST /api/auth/forgot-password` - 請求密碼重設
- `POST /api/auth/reset-password/<token>` - 重設密碼
- `GET /api/auth/google` - Google OAuth 登入
- `GET /api/auth/google/callback` - Google OAuth 回調

#### 文件管理 API
- `POST /api/analyze_document` - 分析文件（需登入+驗證）
- `GET /api/documents` - 取得使用者文件列表（需登入）
- `GET /api/documents/<id>` - 取得特定文件（需登入）
- `DELETE /api/documents/<id>` - 刪除文件（需登入）

#### 引用生成 API（保持不變）
- `POST /api/generate_citation` - 產生 Citation
- `GET /api/suggest_doi` - DOI 建議

### 📊 統計

- **新增檔案**: 24 個
- **修改檔案**: 4 個
- **新增程式碼行數**: 約 2500+ 行
- **新增 API 端點**: 15 個
- **新增資料表**: 4 個
- **新增前端頁面**: 7 個

### ⚙️ 技術棧更新

#### 新增依賴
- **Flask-Login**: 使用者 Session 管理
- **Flask-SQLAlchemy**: ORM 資料庫操作
- **Flask-Mail**: SMTP 郵件發送
- **Authlib**: OAuth 2.0 整合
- **bcrypt**: 密碼加密
- **python-dotenv**: 環境變數管理

### 🔄 向後相容性

- ✅ **完全相容**: 原始的「產生 Citation」功能完全保留
- ✅ **無需登入**: 免費功能（Citation 生成）仍可無登入使用
- ✅ **資料分離**: 新功能在獨立分支，main 分支保持不變

### 📝 待辦事項與未來規劃

- [ ] 添加使用者頭像上傳功能
- [ ] 實作 API 速率限制
- [ ] 添加使用者活動日誌
- [ ] 支援更多 OAuth 提供者（Facebook、Microsoft）
- [ ] 實作兩步驟驗證（2FA）
- [ ] 添加使用者偏好設定
- [ ] 文件分享功能
- [ ] 協作功能
- [ ] 導出報告為 PDF

### ⚠️ 已知限制

1. **Email 發送**: 需要正確設定 SMTP（Gmail 需要應用程式密碼）
2. **Google OAuth**: 需要在 Google Cloud Console 設定憑證
3. **SQLite**: 開發環境使用，生產環境建議使用 PostgreSQL
4. **檔案儲存**: 目前儲存在本地，未來可考慮雲端儲存

### 🧪 測試

- ✅ 系統測試腳本：`python test_auth_system.py`
- ✅ 模型測試：通過
- ✅ 路由測試：通過
- ✅ 密碼加密測試：通過
- ✅ 資料庫連接測試：通過

### 📚 文檔

- ✅ README.md - 專案總覽
- ✅ SETUP_GUIDE.md - 詳細設置指南
- ✅ QUICKSTART.md - 5分鐘快速開始
- ✅ CHANGELOG.md - 變更日誌

---

## 如何使用此版本

### 快速開始
```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數
cp env.example .env
# 編輯 .env 填入您的設定

# 3. 測試系統
python test_auth_system.py

# 4. 啟動應用
python app.py
```

詳細說明請參考 [QUICKSTART.md](QUICKSTART.md)

---

**分支**: `feature/user-authentication`  
**基於**: `main` 分支  
**狀態**: ✅ 已完成，可供測試使用

