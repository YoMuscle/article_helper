import requests
import re
import time

# --------------------------------------------------------
# 1️⃣ 根據 DOI 抓完整 metadata → 用於 /api/generate_citation
# --------------------------------------------------------
def fetch_metadata_from_doi(doi):
    """使用 DOI 取得 CrossRef metadata"""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=8)
        if response.status_code != 200:
            raise ValueError("DOI 不存在於 CrossRef 資料庫。")

        data = response.json().get("message", {})
        authors = [
            f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
            for a in data.get("author", [])
        ]

        return {
            "title": data.get("title", [""])[0],
            "authors": authors,
            "year": str(data.get("issued", {}).get("date-parts", [[None]])[0][0]),
            "journal": data.get("container-title", [""])[0],
            "doi": doi,
            "publisher": data.get("publisher", "N/A"),
        }

    except requests.exceptions.ConnectionError:
        raise ConnectionError("無法連線 CrossRef。")
    except requests.exceptions.Timeout:
        raise ConnectionError("CrossRef 回應逾時。")


# --------------------------------------------------------
# 2️⃣ 根據 DOI 或關鍵字搜尋建議 → 用於 /api/suggest_doi
# --------------------------------------------------------
def suggest_doi_candidates(prefix, limit=5):

    """自動補全建議：支援完整 DOI、部分 DOI、或關鍵字搜尋"""
    prefix = prefix.strip()
    prefix = re.sub(r"^https?://(dx\.)?doi\.org/", "", prefix, flags=re.I)
    prefix = re.sub(r"^doi://", "", prefix, flags=re.I)

    try:
        # ✅ Step 1. 嘗試精準查詢
        if prefix.startswith("10.") and "/" in prefix:
            precise_url = f"https://api.crossref.org/works/{prefix}"
            r = safe_request(precise_url)
            if r:
                msg = r.json().get("message", {})
                return [{
                    "doi": msg.get("DOI", ""),
                    "title": msg.get("title", [""])[0],
                    "year": msg.get("issued", {}).get("date-parts", [[None]])[0][0],
                    "authors": ", ".join([a.get("family", "") for a in msg.get("author", [])[:2]])
                }]

        # ✅ Step 2. fallback 模糊搜尋
        url = "https://api.crossref.org/works"
        params = {
            "rows": limit,
            "query.bibliographic": prefix
        }

        res = safe_request(url, params=params)
        if not res:
            raise ConnectionError("CrossRef 伺服器未回應")

        items = res.json().get("message", {}).get("items", [])
        results = []
        for i in items:
            doi = i.get("DOI", "")
            title = i.get("title", ["N/A"])[0]
            year = i.get("issued", {}).get("date-parts", [[None]])[0][0]
            authors = ", ".join([a.get("family", "") for a in i.get("author", [])[:2]])
            if prefix.lower() in doi.lower() or prefix.lower() in title.lower():
                results.append({
                    "doi": doi,
                    "title": title,
                    "year": year,
                    "authors": authors
                })

        # ✅ 若模糊查完全沒結果，嘗試再用一般 query 搜一次
        if not results:
            params = {"rows": limit, "query": prefix}
            res = safe_request(url, params=params)
            if res:
                items = res.json().get("message", {}).get("items", [])
                for i in items:
                    doi = i.get("DOI", "")
                    title = i.get("title", ["N/A"])[0]
                    year = i.get("issued", {}).get("date-parts", [[None]])[0][0]
                    authors = ", ".join([a.get("family", "") for a in i.get("author", [])[:2]])
                    results.append({
                        "doi": doi,
                        "title": title,
                        "year": year,
                        "authors": authors
                    })

        return results

    except requests.exceptions.RequestException:
        raise ConnectionError("無法連線 CrossRef。")

    
# ✅ 帶重試與延遲的安全請求
def safe_request(url, params=None, retries=2, delay=2, timeout=15):
    """帶自動重試的 requests.get，避免 CrossRef timeout"""
    for attempt in range(retries):
        try:
            res = requests.get(url, params=params, timeout=timeout)
            if res.status_code == 200:
                return res
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                print(f"[Retry {attempt+1}] CrossRef timeout，等待 {delay} 秒後重試...")
                time.sleep(delay)
                continue
        except requests.exceptions.RequestException as e:
            print(f"[Error] CrossRef 連線失敗: {e}")
            break
    return None    