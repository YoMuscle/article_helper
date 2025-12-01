# 開發模式說明

## 什麼是開發模式？

開發模式（`DEV_MODE=True`）是為了方便開發和測試而設計的模式，可以跳過 email 驗證流程。

## 如何啟用？

在 `.env` 檔案中設定：

```env
DEV_MODE=True
```

## 開發模式的效果

### 1. 自動驗證新使用者

當 `DEV_MODE=True` 時：
- ✅ 使用者註冊後 `is_verified` 自動設為 `True`
- ✅ 無需點擊 email 驗證連結
- ✅ 註冊後立即可以使用所有功能（包括文檔檢查）
- ✅ 不需要設定 SMTP 郵件服務

### 2. 註冊流程變化

**開發模式 (DEV_MODE=True)**
```
註冊 → 自動驗證 → 立即可用 ✅
```

**正式模式 (DEV_MODE=False 或未設定)**
```
註冊 → 發送驗證郵件 → 點擊連結 → 驗證完成 → 可用
```

## 使用場景

### 適合使用開發模式：
- ✅ 本地開發測試
- ✅ 功能開發階段
- ✅ 沒有設定 SMTP 郵件服務
- ✅ 快速測試註冊登入流程
- ✅ 展示 Demo

### 不適合使用開發模式：
- ❌ 生產環境部署
- ❌ 對外公開的服務
- ❌ 需要驗證真實 email 的場景
- ❌ 正式測試 email 發送功能

## 配置範例

### 開發環境 `.env`
```env
SECRET_KEY=dev-secret-key-123456
DATABASE_URL=sqlite:///apa_checker.db
DEV_MODE=True
APP_URL=http://localhost:5000
```

最少只需要這些即可運行！

### 生產環境 `.env`
```env
SECRET_KEY=strong-random-production-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DEV_MODE=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
APP_URL=https://your-domain.com
```

## 安全提醒

⚠️ **重要：生產環境必須關閉開發模式**

生產環境部署時：
1. 將 `DEV_MODE` 設為 `False` 或完全移除
2. 設定正確的 SMTP 郵件服務
3. 確保所有新使用者都需要驗證 email

## 測試開發模式

啟用開發模式後測試：

```bash
# 1. 設定 DEV_MODE=True 在 .env
echo "DEV_MODE=True" >> .env

# 2. 啟動應用
python app.py

# 3. 註冊新帳號
# 訪問 http://localhost:5000/register
# 註冊後應該看到 "註冊成功！（開發模式：已自動驗證）"

# 4. 立即登入使用
# 無需檢查 email，直接登入即可使用所有功能
```

## 程式碼說明

開發模式在 `routes/auth.py` 的註冊函式中實現：

```python
# 開發模式：自動驗證使用者
dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
if dev_mode:
    user.is_verified = True
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "註冊成功！（開發模式：已自動驗證）",
        "user": user.to_dict()
    }), 201
```

## 常見問題

### Q: 我已經註冊了帳號但未驗證，現在啟用開發模式會自動驗證嗎？
A: 不會。開發模式只對「新註冊」的使用者生效。已存在的未驗證帳號需要手動在資料庫中設定：

```python
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(email='your-email@example.com').first()
    user.is_verified = True
    db.session.commit()
```

### Q: 開發模式下還需要設定 MAIL_SERVER 嗎？
A: 不需要。開發模式下不會發送 email，所以不需要設定郵件服務。

### Q: 如何確認開發模式已啟用？
A: 註冊新帳號時，成功訊息會顯示「（開發模式：已自動驗證）」。

### Q: 生產環境忘記關閉開發模式會怎樣？
A: ⚠️ 非常危險！所有新註冊的使用者都會自動驗證，無法確認 email 真實性，可能被濫用。務必在生產環境關閉。

## 檢查清單

部署到生產環境前：
- [ ] 確認 `.env` 中 `DEV_MODE=False` 或已移除
- [ ] 設定正確的 SMTP 郵件服務
- [ ] 測試 email 驗證流程正常
- [ ] 測試密碼重設郵件正常
- [ ] 檢查 `SECRET_KEY` 是否為強隨機字串
- [ ] 確認使用正式資料庫（非 SQLite）
- [ ] 啟用 HTTPS

## 總結

開發模式是個便利的工具，讓您在開發階段無需設定複雜的 email 服務即可測試完整功能。但請記得在生產環境中務必關閉！

