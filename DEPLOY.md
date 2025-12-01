# 雲端部署指南

## 快速部署到 Zeabur（推薦）

1. **準備工作**
   - 將專案 push 到 GitHub
   - 註冊 [Zeabur](https://zeabur.com) 帳號

2. **部署步驟**
   - 登入 Zeabur Dashboard
   - 點擊「建立專案」
   - 點擊「新增服務」→「部署您的原始碼」
   - 連結 GitHub，選擇此 repo
   - Zeabur 會自動偵測 Python/Flask 並部署

3. **設定環境變數**（在 Zeabur Dashboard → 服務 → 變數）
   ```
   SECRET_KEY=<隨機產生的密鑰>
   DEV_MODE=False
   FLASK_DEBUG=False
   
   # Email 設定（發送驗證信用）
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   
   # APP_URL 是可選的！程式會自動偵測網域
   # 如果要手動設定：APP_URL=https://你的服務名.zeabur.app
   ```

4. **綁定網域**
   - 在服務設定中點擊「網域」
   - 可使用 Zeabur 提供的 `*.zeabur.app` 子網域
   - 或綁定自己的自訂網域

> ⚠️ **重要**：`PORT` 環境變數由 Zeabur 自動設定，不需要手動設定！

---

## 部署到 Render.com

1. **準備工作**
   - 將專案 push 到 GitHub
   - 註冊 [Render.com](https://render.com) 帳號

2. **部署步驟**
   - 在 Render Dashboard 點擊 "New" → "Web Service"
   - 連接你的 GitHub repo
   - 設定：
     - Name: `apa-checker`
     - Runtime: `Python`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`

3. **設定環境變數**（在 Render Dashboard → Environment）
   ```
   SECRET_KEY=<隨機產生的密鑰>
   APP_URL=https://your-app-name.onrender.com
   DEV_MODE=False
   FLASK_DEBUG=False
   
   # Email 設定（發送驗證信用）
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

---

## 部署到 Heroku

1. **安裝 Heroku CLI**
   ```bash
   # Windows (用 chocolatey)
   choco install heroku-cli
   
   # 或下載安裝檔
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **部署**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

3. **設定環境變數**
   ```bash
   heroku config:set SECRET_KEY=<your-secret>
   heroku config:set APP_URL=https://your-app-name.herokuapp.com
   heroku config:set DEV_MODE=False
   heroku config:set FLASK_DEBUG=False
   heroku config:set MAIL_SERVER=smtp.gmail.com
   heroku config:set MAIL_PORT=587
   heroku config:set MAIL_USE_TLS=True
   heroku config:set MAIL_USERNAME=your-email@gmail.com
   heroku config:set MAIL_PASSWORD=your-app-password
   ```

---

## 重要環境變數說明

| 變數 | 說明 | 本地值 | 雲端值 |
|------|------|--------|--------|
| `APP_URL` | 應用的完整 URL | `http://localhost:5000` | `https://your-app.onrender.com` |
| `PORT` | 伺服器 port | `5000` | 雲端平台自動設定 |
| `HOST` | 伺服器 host | `127.0.0.1` | `0.0.0.0` |
| `DEV_MODE` | 開發模式 | `True` | `False` |
| `FLASK_DEBUG` | Debug 模式 | `True` | `False` |
| `SECRET_KEY` | 加密密鑰 | 開發用 | **必須更換** |

---

## 資料庫注意事項

目前使用 SQLite（`sqlite:///apa_checker.db`），適合：
- 本地開發
- 小型應用

如需更穩定的雲端資料庫，可改用 PostgreSQL：
1. 在 Render 建立 PostgreSQL 資料庫
2. 設定 `DATABASE_URL` 為提供的連接字串

---

## 產生安全的 SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

