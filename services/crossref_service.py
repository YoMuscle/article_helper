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

        def is_fragment_title(t: str) -> bool:
            if not t:
                return False
            s = t.strip().lower()
            # starts with table/figure or similar fragmentary labels
            if re.match(r"^(table|figure)\b", s):
                return True
            # common pattern like 'Table 1:' or 'Figure 2:' earlier in title
            if re.search(r"\b(table|figure)\s*\d+\b", s):
                return True
            return False

        for i in items:
            doi = i.get("DOI", "")
            title = i.get("title", ["N/A"])[0]
            year = i.get("issued", {}).get("date-parts", [[None]])[0][0]
            authors = ", ".join([a.get("family", "") for a in i.get("author", [])[:2]])
            # skip fragmentary table/figure titles or DOIs that look like fragments
            if is_fragment_title(title) or (doi and re.search(r"/fig|/table|/supp|/append|/fig- |/table-", doi.lower())):
                continue
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
                    if is_fragment_title(title) or (doi and re.search(r"/fig|/table|/supp|/append|/fig- |/table-", doi.lower())):
                        continue
                    results.append({
                        "doi": doi,
                        "title": title,
                        "year": year,
                        "authors": authors
                    })

        # Verify collected DOIs actually resolve in CrossRef. Keep only verified
        # ones when possible to avoid suggesting fragment/preprint records that
        # don't resolve to a proper work entry.
        verified = []
        for r in results:
            doi_val = (r.get('doi') or '').strip()
            if not doi_val:
                continue
            try:
                check = safe_request(f"https://api.crossref.org/works/{doi_val}")
                if check:
                    # also ensure title of resolved DOI is not a table/figure fragment
                    msg = check.json().get('message', {})
                    cand_title = msg.get('title', [""])[0]
                    if not is_fragment_title(cand_title):
                        verified.append(r)
            except Exception:
                # skip problematic DOI
                continue

        # prefer verified if any, otherwise return original results (to avoid
        # empty suggestions when CrossRef lookup fails)
        return verified if verified else results

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


# --------------------------------------------------------
# 3️⃣ 根據 Title 或 Keywords 搜尋並回傳 metadata
# --------------------------------------------------------
def fetch_metadata_from_title(title, timeout=10):
    """Search CrossRef by title and pick the best-matching work.

    Uses `query.title` and inspects up to several candidates, preferring
    exact or close title matches and filtering out fragment-like DOIs
    (e.g. URLs that point to /fig- or /table- resources).
    """
    def normalize(t):
        return re.sub(r"[^0-9a-z]", "", (t or "").lower())

    def doi_is_fragment(doi):
        if not doi:
            return False
        d = doi.lower()
        return any(x in d for x in ['/fig', '/table', '/supp', '/append', '/fig-','/table-'])

    url = "https://api.crossref.org/works"

    # Helper: try to pick the best candidate from a list of CrossRef items
    def pick_best_from_items(items_list):
        if not items_list:
            return None
        norm_q = normalize(title)
        best_local = None

        def has_journal(i):
            return bool(i.get('container-title') and i.get('container-title')[0].strip())

        # 1) exact normalized match with journal and non-fragment DOI
        for i in items_list:
            cand_title = i.get('title', [""])[0]
            if normalize(cand_title) == norm_q and has_journal(i) and not doi_is_fragment(i.get('DOI', '')):
                return i

        # 2) candidate contains query and has journal
        for i in items_list:
            cand_title = i.get('title', [""])[0]
            if title.lower() in cand_title.lower() and has_journal(i) and not doi_is_fragment(i.get('DOI', '')):
                return i

        # 3) choose first with journal and non-fragment DOI
        for i in items_list:
            if has_journal(i) and not doi_is_fragment(i.get('DOI', '')):
                return i

        # 4) exact normalized match (any non-fragment)
        for i in items_list:
            cand_title = i.get('title', [""])[0]
            if normalize(cand_title) == norm_q and not doi_is_fragment(i.get('DOI', '')):
                return i

        # 5) candidate contains query (any non-fragment)
        for i in items_list:
            cand_title = i.get('title', [""])[0]
            if title.lower() in cand_title.lower() and not doi_is_fragment(i.get('DOI', '')):
                return i

        # 6) choose first non-fragment DOI
        for i in items_list:
            if not doi_is_fragment(i.get('DOI', '')):
                return i

        # no non-fragment candidate found
        return None

    # Phase 1: prefer journal-article filtered results
    params_filtered = {"rows": 5, "query.title": title, "filter": "type:journal-article"}
    res = safe_request(url, params=params_filtered, timeout=timeout)
    items = []
    if res:
        items = res.json().get("message", {}).get("items", [])

    best_item = pick_best_from_items(items)

    # Phase 2: fallback to unfiltered query when no suitable journal-article found
    if not best_item:
        params = {"rows": 5, "query.title": title}
        res2 = safe_request(url, params=params, timeout=timeout)
        if not res2:
            raise ConnectionError("CrossRef 未回應 (title search)。")

        items2 = res2.json().get("message", {}).get("items", [])
        if not items2:
            raise ValueError("找不到與標題相符的文章。")

        best_item = pick_best_from_items(items2)

        # if still none, fall back to the first available item
        if not best_item and items2:
            best_item = items2[0]

    i = best_item
    doi = i.get("DOI", "")
    authors = [f"{a.get('family','')}, {a.get('given','')}".strip(', ') for a in i.get("author", [])]
    year_val = i.get("issued", {}).get("date-parts", [[None]])[0][0]
    year = str(year_val) if year_val is not None else "n.d."

    return {
        "title": i.get("title", [""])[0],
        "authors": authors,
        "year": year,
        "journal": i.get("container-title", [""])[0],
        "doi": doi,
        "publisher": i.get("publisher", "N/A"),
    }


def fetch_metadata_from_keywords(keywords, limit=3, timeout=10):
    """Use CrossRef to search by keywords and return up to `limit` metadata dicts.

    Each item uses the same simplified metadata shape as other fetch functions.
    """
    url = "https://api.crossref.org/works"
    params = {"rows": limit, "query.bibliographic": keywords}
    res = safe_request(url, params=params, timeout=timeout)
    if not res:
        raise ConnectionError("CrossRef 未回應 (keyword search)。")

    items = res.json().get("message", {}).get("items", [])
    results = []

    def is_fragment_title(t: str) -> bool:
        if not t:
            return False
        s = t.strip().lower()
        if re.match(r"^(table|figure)\b", s):
            return True
        if re.search(r"\b(table|figure)\s*\d+\b", s):
            return True
        return False

    for i in items[:limit]:
        doi = i.get("DOI", "")
        # build clean authors list (family, given) and filter out empty names
        authors = []
        for a in i.get('author', [])[:3]:
            fam = a.get('family', '') or ''
            giv = a.get('given', '') or ''
            name = ", ".join([x for x in [fam, giv] if x]).strip(', ')
            if name:
                authors.append(name)

        year_val = i.get("issued", {}).get("date-parts", [[None]])[0][0]
        year = year_val if year_val is not None else "n.d."

        title = i.get("title", ["N/A"])[0]
        # skip fragmentary table/figure titles and DOIs that look like fragments
        if is_fragment_title(title) or (doi and re.search(r"/fig|/table|/supp|/append|/fig- |/table-", doi.lower())):
            continue

        results.append({
            "title": title,
            "authors": authors,
            "year": year,
            "journal": i.get("container-title", [""])[0],
            "doi": doi,
        })
    return results