def format_apa_reference(meta):
    """根據 metadata 生成 APA 格式的 reference"""
    authors = ", ".join(meta.get("authors", []))
    year = meta.get("year", "n.d.")
    title = meta.get("title", "")
    journal = meta.get("journal", "")
    doi = meta.get("doi", "")

    if doi:
        return f"{authors} ({year}). {title}. *{journal}*. https://doi.org/{doi}"
    else:
        return f"{authors} ({year}). {title}. *{journal}*."

def generate_citation_key(meta):
    """生成 Parenthetical / Narrative citation key"""
    authors = meta.get("authors", [])
    year = meta.get("year", "n.d.")
    if not authors:
        return {"parenthetical": "(Unknown, {year})", "narrative": f"Unknown ({year})"}

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
