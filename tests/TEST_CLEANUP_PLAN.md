# APA Checker 測試整理建議

## 📊 當前狀況

目前有 **18 個測試文件**，但並非全部都是必要的 regression tests。

---

## ✅ 核心 Regression Tests（建議保留 - 8個）

這些是**真正必要**的測試，應該永久保留並定期運行：

### 1. test_full_matching.py ⭐⭐⭐⭐⭐
**目的**: 端到端完整測試  
**覆蓋**: 引用檢測、參考文獻解析、匹配邏輯  
**狀態**: 必須保留

### 2. test_semicolon_formats.py ⭐⭐⭐⭐⭐
**目的**: 分號分隔引用的格式檢查  
**覆蓋**: 7種分號格式變化、空格錯誤檢測  
**狀態**: 必須保留（剛修復的功能）

### 3. test_three_authors_wrong_citation.py ⭐⭐⭐⭐⭐
**目的**: 檢查作者數量規則  
**覆蓋**: 3位以上作者必須用 et al.、錯誤檢測  
**狀態**: 必須保留（剛修復的功能）

### 4. test_compound_names.py ⭐⭐⭐⭐
**目的**: 複合姓氏解析  
**覆蓋**: De Menezes, Van der Berg, Lopez-Calderon  
**狀態**: 必須保留

### 5. test_reference_parsing.py ⭐⭐⭐⭐
**目的**: 跨頁參考文獻解析  
**覆蓋**: 多行參考文獻合併  
**狀態**: 必須保留

### 6. test_kojima_suggestion.py ⭐⭐⭐⭐
**目的**: 錯誤引用的建議功能  
**覆蓋**: 不完整引用的建議機制  
**狀態**: 必須保留

### 7. test_two_authors.py ⭐⭐⭐
**目的**: 兩位作者的引用格式  
**覆蓋**: parenthetical 和 narrative 格式  
**狀態**: 必須保留

### 8. test_fuzzy_matching.py ⭐⭐⭐
**目的**: 模糊匹配邏輯  
**覆蓋**: 作者/年份提取、各種格式  
**狀態**: 必須保留

---

## ❌ 調試測試（建議刪除 - 5個）

這些是**臨時創建**的調試測試，功能已被核心測試覆蓋：

1. **test_debug_format_error.py** - 臨時調試 Klimesch 格式錯誤
2. **test_extract_lopez.py** - 臨時測試 Lopez-Calderon 提取
3. **test_lopez_matching.py** - 臨時測試 Lopez-Calderon 匹配
4. **test_parse_lopez_ref.py** - 臨時測試參考文獻解析
5. **test_regex_pattern.py** - 臨時測試 regex patterns

**建議**: 直接刪除這 5 個文件

---

## ⚠️ 重複測試（建議刪除或合併 - 5個）

這些測試與核心測試有功能重複：

1. **test_lopez_calderon.py** - 功能已被 `test_compound_names.py` 覆蓋
2. **test_extraction.py** - 與 `test_fuzzy_matching.py` 部分重複
3. **test_two_author_extraction.py** - 與 `test_two_authors.py` 重複
4. **test_matching.py** - 基本測試，可合併到 `test_full_matching.py`
5. **test_citation_detection.py** - 太簡單，可合併到 `test_full_matching.py`

**建議**: 刪除這 5 個文件

---

## 📋 精簡後的測試結構

```
tests/
├── run_all_tests.py          # 測試運行器
├── README.md                  # 測試說明文檔
│
├── test_full_matching.py      # ✅ 核心測試 1
├── test_semicolon_formats.py  # ✅ 核心測試 2
├── test_three_authors_wrong_citation.py  # ✅ 核心測試 3
├── test_compound_names.py     # ✅ 核心測試 4
├── test_reference_parsing.py  # ✅ 核心測試 5
├── test_kojima_suggestion.py  # ✅ 核心測試 6
├── test_two_authors.py        # ✅ 核心測試 7
└── test_fuzzy_matching.py     # ✅ 核心測試 8
```

**總計**: 8 個核心測試 + 1 個運行器 + 1 個說明文檔 = 10 個文件

---

## 🎯 刪除清單

可以安全刪除的 10 個文件：

```bash
# 調試測試（5個）
tests/test_debug_format_error.py
tests/test_extract_lopez.py
tests/test_lopez_matching.py
tests/test_parse_lopez_ref.py
tests/test_regex_pattern.py

# 重複測試（5個）
tests/test_lopez_calderon.py
tests/test_extraction.py
tests/test_two_author_extraction.py
tests/test_matching.py
tests/test_citation_detection.py
```

---

## 📊 測試覆蓋率

精簡後的 8 個核心測試覆蓋了：

✅ 端到端完整流程  
✅ 引用檢測（parenthetical & narrative）  
✅ 參考文獻解析（跨頁、複合姓氏）  
✅ 引用匹配（精確 & 模糊）  
✅ 格式錯誤檢測（et al., &/and, 分號等）  
✅ 作者數量規則（2位、3位以上）  
✅ 錯誤建議功能  
✅ 分號分隔引用處理  

**估計覆蓋率**: 約 90% 的核心功能

---

## 💡 下一步行動

### 選項 1: 立即清理（推薦）
```bash
# 刪除 10 個不必要的測試文件
rm tests/test_debug_format_error.py
rm tests/test_extract_lopez.py
rm tests/test_lopez_matching.py
rm tests/test_parse_lopez_ref.py
rm tests/test_regex_pattern.py
rm tests/test_lopez_calderon.py
rm tests/test_extraction.py
rm tests/test_two_author_extraction.py
rm tests/test_matching.py
rm tests/test_citation_detection.py

# 運行核心測試確認
.\.apa\Scripts\python.exe tests\run_all_tests.py
```

### 選項 2: 保守方式
先將這些文件移到 `tests/archive/` 目錄，觀察一段時間後再刪除。

---

## 🔄 維護策略

1. **只保留 8 個核心測試** - 易於維護，執行快速
2. **每次改動後運行測試** - 確保沒有破壞現有功能
3. **發現新 bug 時添加測試** - 防止回歸
4. **定期審查測試** - 刪除過時或重複的測試

---

## ⏱️ 執行時間

- **18 個測試**: 約 5-8 秒
- **8 個核心測試**: 約 2-3 秒

精簡後測試執行更快，維護更容易！
