import requests

def fetch_metadata_from_doi(doi):
    """使用 DOI 取得 CrossRef metadata"""
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("❌ 無法在 CrossRef 找到此 DOI。請確認格式是否正確。")
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

def suggest_doi_candidates(prefix, limit=5):
    """根據部分 DOI 前綴，自動補全建議"""
    url = "https://api.crossref.org/works"
    params = {"query": prefix, "rows": limit}
    try:
        res = requests.get(url, params=params)
        items = res.json().get("message", {}).get("items", [])
        return [
            {
                "doi": i.get("DOI", ""),
                "title": i.get("title", ["N/A"])[0],
                "year": i.get("issued", {}).get("date-parts", [[None]])[0][0],
                "authors": ", ".join(
                    [a.get("family", "") for a in i.get("author", [])[:2]]
                ),
            }
            for i in items
        ]
    except Exception:
        return []