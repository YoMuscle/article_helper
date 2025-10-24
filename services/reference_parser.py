import re

def parse_reference(text):
    """從APA格式的文字中抽取作者與年份"""
    year_match = re.search(r"\((\d{4})\)", text)
    year = year_match.group(1) if year_match else "n.d."

    authors_part = text.split("(")[0].strip()
    authors = re.split(r"[,;&]\s*|\sand\s", authors_part)
    authors = [a.strip() for a in authors if a.strip()]

    title_match = re.search(r"\)\.\s*(.*?)(?:\.\s*\*|$)", text)
    title = title_match.group(1).strip() if title_match else ""

    return {
        "authors": authors,
        "year": year,
        "title": title,
        "journal": "",
        "doi": ""
    }