import requests

def fetch_metadata_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("DOI not found in CrossRef database")

    data = response.json().get("message", {})
    authors = []
    for a in data.get("author", []):
        name = f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
        authors.append(name)

    return {
        "title": data.get("title", [""])[0],
        "authors": authors,
        "year": str(data.get("issued", {}).get("date-parts", [[None]])[0][0]),
        "journal": data.get("container-title", [""])[0],
        "doi": doi
    }