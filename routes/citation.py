from flask import Blueprint, request, jsonify
from services.crossref_service import (
    fetch_metadata_from_doi,
    suggest_doi_candidates,
    fetch_metadata_from_title,
    fetch_metadata_from_keywords,
)
from services.apa_formatter import format_apa_reference, generate_citation_key
from services.reference_parser import parse_reference
import re

bp = Blueprint('citation', __name__)


def detect_input_mode(text: str):
    """Detect user input mode: doi, reference, title, keyword, or unknown.

    Rules (inferred from design attachments):
    - DOI: contains doi.org, starts with 10., or matches DOI regex
    - Reference: contains a 4-digit year in parentheses and author-like part before it
    - Title: wrapped in quotes ("..." or '...')
    - Keyword: multi-word input without quotes (fallback)
    - If DOI appears anywhere, prefer DOI mode (mixed inputs)
    """
    s = text.strip()
    if not s:
        return "unknown"

    # DOI detection: common patterns
    doi_regex = re.compile(r"\b10\.\d{4,9}/\S+\b", re.I)
    if "doi.org" in s.lower() or s.lower().startswith("doi:") or doi_regex.search(s) or s.lower().startswith("10."):
        return "doi"

    # Title detection: quoted
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return "title"

    # Reference detection: year in parentheses and at least one comma before it (author list)
    if re.search(r"\(\s*\d{4}\s*\)", s) and ("," in s.split("(", 1)[0] if "(" in s else s):
        return "reference"

    # Keyword vs title heuristic: if multiple words and not too short -> keyword
    words = s.split()
    if len(words) >= 1:
        return "keyword"

    return "unknown"


def select_best_candidate(metas):
    """Choose the best candidate from keyword search results.

    Heuristics:
    - Prefer titles that don't start with 'Table'/'Figure' and have a proper year and/or authors.
    - Prefer DOIs that don't include fragments like '/table-' or '/fig-'.
    - Fall back to first candidate if none match.
    """
    if not metas:
        return None

    def title_is_figure_or_table(title):
        if not title:
            return False
        t = title.strip().lower()
        return t.startswith('table') or t.startswith('figure') or 'table' in t.split(':',1)[0] or 'figure' in t.split(':',1)[0]

    def doi_is_fragment(doi):
        if not doi:
            return False
        d = doi.lower()
        return '/fig' in d or '/table' in d or '/supp' in d or '/append' in d

    # 1) prefer non-table/figure titles with authors and year
    for m in metas:
        if m.get('title') and not title_is_figure_or_table(m.get('title')) and m.get('authors') and m.get('year') and m.get('year') != 'n.d.' and not doi_is_fragment(m.get('doi')):
            return m

    # 2) prefer non-table/figure titles with year
    for m in metas:
        if m.get('title') and not title_is_figure_or_table(m.get('title')) and m.get('year') and m.get('year') != 'n.d.':
            return m

    # 3) prefer non-table/figure titles without fragment DOIs
    for m in metas:
        if m.get('title') and not title_is_figure_or_table(m.get('title')) and not doi_is_fragment(m.get('doi')):
            return m

    # 4) prefer any item with authors
    for m in metas:
        if m.get('authors'):
            return m

    # fallback to first
    return metas[0]


def _normalize_text(s: str) -> str:
    import re
    if not s:
        return ""
    return re.sub(r"[^0-9a-z]", "", s.lower())


def _tokens(s: str):
    return [t for t in re.findall(r"[0-9a-z]+", (s or "").lower())]


def _compare_meta(a: dict, b: dict) -> bool:
    """Return True if metadata a and b appear to refer to the same work.

    Heuristics: normalized title equality or high token overlap, or same year
    and share first author's family name.
    """
    # titles
    ta = (a.get('title') or '')
    tb = (b.get('title') or '')
    na = _normalize_text(ta)
    nb = _normalize_text(tb)
    if na and nb and na == nb:
        return True

    # token overlap
    sa = set(_tokens(ta))
    sb = set(_tokens(tb))
    if sa and sb:
        inter = sa.intersection(sb)
        union = sa.union(sb)
        if len(inter) / max(1, len(union)) >= 0.6:
            return True

    # year + first author family match
    ya = str(a.get('year') or '')
    yb = str(b.get('year') or '')
    if ya and yb and ya == yb:
        # compare first author family name if available
        fa = ''
        fb = ''
        if a.get('authors'):
            fa = a.get('authors')[0].split(',')[0].strip().lower()
        if b.get('authors'):
            fb = b.get('authors')[0].split(',')[0].strip().lower()
        if fa and fb and fa == fb:
            return True

    return False


# ============ 1️⃣ Citation 主要功能 ============
@bp.route('/api/generate_citation', methods=['POST'])
def generate_citation():
    data = request.get_json()
    user_input = data.get('input', '').strip()

    try:
        mode = detect_input_mode(user_input)

        # If mixed input contains DOI anywhere, prefer DOI
        # extract DOI-like substring if present
        doi_match = re.search(r"(10\.\d{4,9}/\S+)", user_input, re.I)
        if doi_match:
            mode = "doi"
            doi_val = doi_match.group(1).rstrip('.,;')
        else:
            doi_val = None

        if mode == "doi":
            # normalize DOI from urls like https://doi.org/...
            doi = doi_val or re.sub(r"^https?://(dx\.)?doi\.org/", "", user_input, flags=re.I).strip()
            meta = fetch_metadata_from_doi(doi)
            suggestion = "偵測為 DOI 模式，正在查詢 CrossRef..."

        elif mode == "reference":
            meta = parse_reference(user_input)
            suggestion = "偵測為 Reference 模式，將進行格式確認"

        elif mode == "title":
            # strip surrounding quotes
            title = user_input.strip('"').strip("'")
            meta = fetch_metadata_from_title(title)
            # Verify the found metadata actually matches the provided title.
            # If not, inform user no data found (user requested exact title search).
            if not _compare_meta({"title": title}, meta):
                return jsonify({"mode": "title", "status": "error", "message": "使用標題搜尋但找不到與該標題相符的期刊文章。"}), 404

            suggestion = "偵測為 Title 模式，系統將根據完整標題搜尋最相似論文"

        elif mode == "keyword":
            metas = fetch_metadata_from_keywords(user_input, limit=3)
            suggestion = "偵測為 關鍵字 模式，以下為最相關的前 3 筆結果"

            # Prefer a candidate that has both authors and a year. Fallback to
            # the first item if none meet criteria.
            top = None
            for m in metas:
                if m.get('authors') and m.get('year') and m.get('title'):
                    top = m
                    break
            if not top and metas:
                top = metas[0]

            meta = top or {}
            # If candidate has a DOI, verify the DOI's metadata matches the
            # candidate metadata. If mismatch, omit DOI from the response.
            if meta and meta.get('doi'):
                try:
                    doi_meta = fetch_metadata_from_doi(meta.get('doi'))
                    if not _compare_meta(meta, doi_meta):
                        # mismatch -> remove DOI to avoid giving incorrect DOI
                        meta = dict(meta)
                        meta['doi'] = ''
                        suggestion += " (注意：檢查到 DOI 的 metadata 與候選資料不一致，已省略 DOI。)"
                except Exception:
                    # If DOI lookup fails, omit DOI
                    meta = dict(meta)
                    meta['doi'] = ''
                    suggestion += " (注意：無法取得 DOI 的完整 metadata，已省略 DOI。)"

            apa_ref = format_apa_reference(meta) if meta else ""
            citation = generate_citation_key(meta) if meta else {"parenthetical": "", "narrative": ""}

            return jsonify({
                "mode": mode,
                "status": "success",
                "suggestion": suggestion,
                "reference": apa_ref,
                "citations": citation,
                "meta": meta,
                "results": metas,
            })

        else:
            return jsonify({"mode": "unknown", "status": "error", "message": "無法判斷輸入格式，請輸入 DOI、APA Reference、標題或關鍵字。"}), 400

        apa_ref = format_apa_reference(meta)
        citation = generate_citation_key(meta)

        return jsonify({
            "mode": mode,
            "status": "success",
            "suggestion": suggestion,
            "reference": apa_ref,
            "citations": citation,
            "meta": meta
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============ 2️⃣ CrossRef DOI Suggestion 功能 ============
@bp.route('/api/suggest_doi', methods=['GET'])
def suggest_doi():
    prefix = request.args.get('prefix', '').strip()
    if not prefix:
        return jsonify([])

    results = suggest_doi_candidates(prefix)
    return jsonify(results)