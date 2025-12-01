# 快速開始指南

## 5 分鐘快速啟動

### 1. 安裝依賴 (1 分鐘)

```bash
pip install -r requirements.txt
```

### 2. 建立環境變數檔案 (2 分鐘)

複製範例檔案：
```bash
cp env.example .env
```

編輯 `.env`，最少需要設定：
```env
SECRET_KEY=your-random-secret-key-here-change-this
DEV_MODE=True
```

> **提示**: 使用以下命令生成安全的 SECRET_KEY：
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

**開發模式說明：**
- `DEV_MODE=True`: 新註冊使用者自動驗證，無需設定 email
- 如需測試 email 功能，請設定 MAIL_SERVER 等相關變數

### 3. 測試系統 (1 分鐘)

```bash
python test_auth_system.py
```

如果看到 "所有測試通過！"，就可以繼續了。

### 4. 啟動應用 (1 分鐘)

```bash
python app.py
```

訪問 http://localhost:5000

## 首次使用

1. **註冊帳號**
   - 前往 http://localhost:5000/register
   - 填寫 Email、使用者名稱、密碼
   - 點擊「註冊」

2. **驗證 Email**
   - **開發模式 (DEV_MODE=True)**: 自動驗證，直接進入下一步
   - **正式模式**: 檢查 Email 收件匣，點擊驗證連結

3. **開始使用**
   - 使用「產生 Citation」功能（無需登入）
   - 上傳 Word 文檔進行 APA 格式檢查（需登入+驗證）
   - 在「我的文件」查看歷史記錄

## Gmail SMTP 快速設定

如果使用 Gmail 發送驗證郵件：

1. 前往 https://myaccount.google.com/security
2. 啟用「兩步驟驗證」
3. 搜尋「應用程式密碼」
4. 選擇「郵件」和「其他（自訂名稱）」
5. 生成密碼並複製到 `.env` 的 `MAIL_PASSWORD`

## Google OAuth 設定（可選）

如果想使用 Google 登入：

1. 前往 https://console.cloud.google.com/
2. 建立專案
3. 啟用「Google+ API」
4. 建立「OAuth 2.0 用戶端 ID」
5. 設定重新導向 URI：`http://localhost:5000/api/auth/google/callback`
6. 將 Client ID 和 Secret 填入 `.env`

## 常見問題

### Q: 無法發送郵件？
A: 檢查：
- Gmail 是否啟用兩步驟驗證
- 是否使用「應用程式密碼」（不是帳戶密碼）
- SMTP 設定是否正確

### Q: Google 登入失敗？
A: 檢查：
- 重新導向 URI 是否設定正確
- Client ID 和 Secret 是否正確
- 是否啟用了 Google+ API

### Q: 資料庫錯誤？
A: 嘗試：
```bash
# 刪除舊資料庫重新建立
rm apa_checker.db
python app.py
```

### Q: 測試時看到警告？
A: 如果看到「Email 服務未配置」，這表示您需要在 `.env` 中設定 Email 相關變數。但這不影響基本功能測試。

## 進階設定

詳細的設定說明請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 需要協助？

如果遇到問題：
1. 檢查 `.env` 檔案是否正確設定
2. 執行 `python test_auth_system.py` 診斷問題
3. 查看控制台的錯誤訊息
4. 參考 SETUP_GUIDE.md 的疑難排解章節

## 開發模式 vs 生產模式

目前是開發模式，適合測試和開發。

如要部署到生產環境：
- 將 DEBUG 設為 False
- 使用 PostgreSQL 或 MySQL 替代 SQLite
- 設定 HTTPS
- 使用強隨機的 SECRET_KEY
- 設定正確的 APP_URL

詳見 SETUP_GUIDE.md 的部署章節。

