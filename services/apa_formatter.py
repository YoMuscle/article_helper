def format_apa_reference(meta):
    """根據 metadata 生成 APA 格式的 reference"""
    authors_list = meta.get("authors", []) or []
    # normalize authors: ensure it's a list of non-empty strings
    authors_list = [a for a in authors_list if isinstance(a, str) and a.strip()]
    year = meta.get("year") or "n.d."
    title = meta.get("title", "")
    journal = meta.get("journal", "")
    doi = meta.get("doi", "")

    if authors_list:
        authors = ", ".join(authors_list)
        byline = f"{authors} ({year})."
    else:
        # no authors available — show year-first byline
        byline = f"({year})."

    if doi:
        if journal:
            return f"{byline} {title}. *{journal}*. https://doi.org/{doi}"
        else:
            return f"{byline} {title}. https://doi.org/{doi}"
    else:
        if journal:
            return f"{byline} {title}. *{journal}*."
        else:
            return f"{byline} {title}."

def generate_citation_key(meta):
    """生成 Parenthetical / Narrative citation key"""
    authors = meta.get("authors", [])
    year = meta.get("year", "n.d.")
    if not authors:
        return {"parenthetical": f"(Unknown, {year})", "narrative": f"Unknown ({year})"}

    first_author = authors[0].split(",")[0]

    if len(authors) == 1:
        return {
            "parenthetical": f"({first_author}, {year})",
            "narrative": f"{first_author} ({year})"
        }
    elif len(authors) == 2:
        last_author = authors[1].split(",")[0]
        return {
            "parenthetical": f"({first_author} & {last_author}, {year})",
            "narrative": f"{first_author} and {last_author} ({year})"
        }
    else:
        return {
            "parenthetical": f"({first_author} et al., {year})",
            "narrative": f"{first_author} et al. ({year})"
        }
