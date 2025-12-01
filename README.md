# 論文救火站 - APA Citation Generator

論文救火站是一個協助學術寫作的工具，提供 APA 格式引用生成和文檔檢查功能。

## 功能特色

### 免費功能（無需登入）
- ✅ **自動 Citation 生成**
  - 支援 DOI、標題、關鍵字、Reference 多種輸入模式
  - 自動偵測輸入類型
  - 整合 CrossRef API 查詢學術文獻
  - 生成標準 APA 7 格式的 Reference 和 Citation

### 進階功能（需要註冊登入）
- ✅ **文檔 APA 格式檢查**
  - 上傳 Word 文檔（.doc/.docx）
  - 自動檢測引用格式錯誤
  - 識別缺少的參考文獻
  - 顯示未引用的參考文獻
  - 提供詳細的修正建議

- ✅ **使用者認證系統**
  - Email + 密碼註冊登入
  - Google OAuth 2.0 快速登入
  - Email 驗證機制
  - 密碼重設功能
  - 個人資料管理

- ✅ **文件管理**
  - 查看上傳歷史記錄
  - 文件分析結果保存
  - 使用者文件隔離（只能看到自己的文件）

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 配置環境變數

複製 `env.example` 為 `.env` 並填入您的配置：

```bash
cp env.example .env
```

詳細的設置說明請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

### 執行應用

```bash
python app.py
```

訪問 `http://localhost:5000` 開始使用


📁 專案結構
apa_checker/
├── models/              ✅ 資料庫模型
├── routes/              ✅ 路由（auth.py 新增）
├── services/            ✅ 服務層（email_service.py 新增）
├── utils/               ✅ 工具函式（decorators.py 新增）
├── templates/           ✅ 7 個新模板 + 更新 index.html
├── uploads/             ✅ 文件上傳目錄
├── env.example          ✅ 環境變數範例
├── test_auth_system.py  ✅ 測試腳本
├── README.md            ✅ 專案說明
├── SETUP_GUIDE.md       ✅ 設置指南
├── QUICKSTART.md        ✅ 快速開始
└── CHANGELOG.md         ✅ 變更日誌

## 專案結構

```
apa_checker/
├── app.py                      # Flask 應用主程式
├── requirements.txt            # Python 依賴套件
├── env.example                 # 環境變數範例
├── models/                     # 資料庫模型
│   ├── user.py                # 使用者模型
│   ├── document.py            # 文件模型
│   ├── email_verification.py # Email 驗證模型
│   └── password_reset.py     # 密碼重設模型
├── routes/                     # 路由
│   ├── auth.py                # 認證相關路由
│   └── citation.py            # 引用生成路由
├── services/                   # 服務層
│   ├── apa_formatter.py       # APA 格式化
│   ├── crossref_service.py    # CrossRef API 整合
│   ├── document_analyzer.py   # 文檔分析
│   ├── reference_parser.py    # 參考文獻解析
│   └── email_service.py       # 郵件服務
├── utils/                      # 工具函式
│   └── decorators.py          # 裝飾器（權限控制）
├── templates/                  # HTML 模板
│   ├── index.html             # 首頁
│   ├── login.html             # 登入頁面
│   ├── register.html          # 註冊頁面
│   ├── profile.html           # 個人資料頁面
│   ├── my_documents.html      # 我的文件列表
│   ├── forgot_password.html   # 忘記密碼
│   ├── reset_password.html    # 重設密碼
│   └── verify_result.html     # Email 驗證結果
├── static/                     # 靜態資源
│   └── style.css              # 樣式表
└── uploads/                    # 上傳文件暫存目錄
```

## 技術架構

### 後端
- **Flask**: Web 框架
- **Flask-Login**: 使用者認證
- **Flask-SQLAlchemy**: ORM 資料庫操作
- **Flask-Mail**: Email 發送
- **Authlib**: OAuth 2.0 整合
- **bcrypt**: 密碼加密

### 前端
- **Bootstrap 5**: UI 框架
- **Font Awesome**: 圖示
- **原生 JavaScript**: 互動功能

### 資料庫
- **SQLite**: 開發環境（可替換為 PostgreSQL/MySQL）

### 外部 API
- **CrossRef API**: 學術文獻查詢

## API 文檔

詳細的 API 端點說明請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 分支說明

- `main`: 原始版本（免費功能，無認證系統）
- `feature/user-authentication`: 新增使用者認證與文件管理功能

## 安全性

本專案實施以下安全措施：
- 密碼使用 bcrypt 加密
- Session 管理使用 Flask-Login
- Token 使用安全的隨機生成
- Email 驗證機制
- CSRF 保護
- SQL Injection 防護（使用 ORM）

## 開發計劃

- [ ] 支援更多文件格式（PDF）
- [ ] 引用風格擴展（MLA, Chicago）
- [ ] 協作功能
- [ ] API 限流
- [ ] 進階分析功能

## 授權

此專案為學術用途開發。

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 聯絡

如有任何問題或建議，請透過 Issue 系統聯繫。

