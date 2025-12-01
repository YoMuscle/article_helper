# 論文救火站 - 使用者認證系統設置指南

此分支 (`feature/user-authentication`) 新增了完整的使用者認證與管理功能。

## 新增功能

### 1. 使用者認證
- ✅ Email + 密碼註冊與登入
- ✅ Google OAuth 2.0 登入
- ✅ Email 驗證（註冊後需驗證）
- ✅ 密碼重設功能
- ✅ 個人資料管理

### 2. 文件管理
- ✅ 文件上傳需要登入且驗證
- ✅ 每個使用者只能看到自己的文件
- ✅ 文件歷史記錄
- ✅ 文件刪除功能

### 3. 權限控制
- 免費功能：產生 Citation（無需登入）
- 需登入功能：文檔檢查、我的文件

## 設置步驟

### 1. 安裝套件

```bash
pip install -r requirements.txt
```

### 2. 設置環境變數

複製 `env.example` 為 `.env` 並填入實際的配置：

```bash
cp env.example .env
```

編輯 `.env` 檔案：

```env
# Flask 密鑰（使用 python -c "import secrets; print(secrets.token_hex(32))" 生成）
SECRET_KEY=your-secret-key-here

# 資料庫
DATABASE_URL=sqlite:///apa_checker.db

# Email (SMTP) 配置 - Gmail 範例
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Gmail 需使用應用程式密碼
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Google OAuth 配置
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# 應用網址
APP_URL=http://localhost:5000
```

### 3. 開發模式設定（可選）

如果您在開發階段不想設定 email 服務，可以啟用開發模式：

```env
DEV_MODE=True
```

**開發模式效果：**
- ✅ 新註冊使用者自動驗證，無需點擊 email 連結
- ✅ 可以立即使用所有功能（文檔檢查）
- ⚠️ 生產環境請務必設為 `False` 或移除此設定

### 4. Gmail SMTP 設置（如需 email 功能）

如果使用 Gmail 發送郵件：

1. 前往 Google 帳戶設定
2. 啟用「兩步驟驗證」
3. 生成「應用程式密碼」
4. 將應用程式密碼填入 `.env` 的 `MAIL_PASSWORD`

### 5. Google OAuth 設置（可選）

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google+ API
4. 建立 OAuth 2.0 憑證（應用程式類型：網頁應用程式）
5. 設定授權重新導向 URI：
   - `http://localhost:5000/api/auth/google/callback`（開發環境）
   - `https://your-domain.com/api/auth/google/callback`（正式環境）
6. 將 Client ID 和 Client Secret 填入 `.env`

### 6. 建立資料庫

應用程式第一次啟動時會自動建立資料庫表：

```bash
python app.py
```

### 7. 測試

訪問 `http://localhost:5000`：

- 測試註冊功能
- 檢查 email 收件匣的驗證郵件
- 測試 Google 登入
- 測試文件上傳

## 資料庫結構

### users 表
- `id`: 主鍵
- `email`: Email（唯一）
- `password_hash`: 密碼雜湊
- `username`: 使用者名稱
- `is_verified`: Email 驗證狀態
- `google_id`: Google OAuth ID
- `created_at`: 建立時間
- `updated_at`: 更新時間

### documents 表
- `id`: 主鍵
- `user_id`: 使用者 ID（外鍵）
- `filename`: 檔案名稱
- `upload_time`: 上傳時間
- `analysis_result`: 分析結果（JSON）

### email_verifications 表
- `id`: 主鍵
- `user_id`: 使用者 ID（外鍵）
- `token`: 驗證 token
- `expires_at`: 過期時間
- `created_at`: 建立時間

### password_resets 表
- `id`: 主鍵
- `user_id`: 使用者 ID（外鍵）
- `token`: 重設 token
- `expires_at`: 過期時間
- `used`: 是否已使用
- `created_at`: 建立時間

## API 端點

### 認證相關
- `POST /api/auth/register` - 註冊
- `POST /api/auth/login` - 登入
- `POST /api/auth/logout` - 登出
- `GET /api/auth/user` - 取得當前使用者
- `PUT /api/auth/profile` - 更新個人資料
- `POST /api/auth/change-password` - 修改密碼
- `POST /api/auth/resend-verification` - 重新發送驗證郵件
- `GET /verify-email/<token>` - Email 驗證
- `POST /api/auth/forgot-password` - 請求密碼重設
- `POST /api/auth/reset-password/<token>` - 重設密碼
- `GET /api/auth/google` - Google 登入
- `GET /api/auth/google/callback` - Google 回調

### 文件相關
- `POST /api/analyze_document` - 分析文件（需登入+驗證）
- `GET /api/documents` - 取得使用者文件列表（需登入）
- `GET /api/documents/<id>` - 取得特定文件（需登入）
- `DELETE /api/documents/<id>` - 刪除文件（需登入）

### 引用生成（免費功能）
- `POST /api/generate_citation` - 產生 Citation
- `GET /api/suggest_doi` - DOI 建議

## 前端頁面

- `/` - 首頁（產生 Citation + 文檔檢查）
- `/login` - 登入頁面
- `/register` - 註冊頁面
- `/profile` - 個人資料頁面
- `/my-documents` - 我的文件列表
- `/forgot-password` - 忘記密碼
- `/reset-password/<token>` - 重設密碼

## 安全性注意事項

1. **SECRET_KEY**: 務必使用強隨機字串，不要使用預設值
2. **密碼**: 使用 bcrypt 加密，不儲存明文
3. **Token**: 使用 `secrets.token_urlsafe()` 生成隨機 token
4. **HTTPS**: 正式環境必須使用 HTTPS
5. **CORS**: 根據需求調整 CORS 設定
6. **環境變數**: 不要將 `.env` 提交到版本控制

## 疑難排解

### 無法發送郵件
- 檢查 SMTP 設定是否正確
- Gmail 需使用「應用程式密碼」而非帳戶密碼
- 確認防火牆沒有封鎖 SMTP 連接埠

### Google 登入失敗
- 確認重新導向 URI 設定正確
- 檢查 Google Client ID 和 Secret 是否正確
- 確認 Google OAuth 同意畫面已設定

### 資料庫錯誤
- 刪除現有資料庫檔案重新建立
- 檢查資料庫檔案權限

## 部署到生產環境

1. 將 `DEBUG` 設為 `False`
2. 設定強隨機的 `SECRET_KEY`
3. 使用 PostgreSQL 或 MySQL 替代 SQLite
4. 設定正確的 `APP_URL`
5. 使用 HTTPS
6. 設定 Google OAuth 正式環境的重新導向 URI

## 原始功能

原始的免費功能（產生 Citation）保持不變，無需登入即可使用。

## 聯絡資訊

如有問題，請參考專案文件或聯繫開發團隊。

