from flask import Blueprint, request, jsonify
from services.crossref_service import fetch_metadata_from_doi
from services.apa_formatter import format_apa_reference, generate_citation_key
from services.reference_parser import parse_reference

bp = Blueprint('citation', __name__)

@bp.route('/api/generate_citation', methods=['POST'])
def generate_citation():
    data = request.get_json()
    user_input = data.get('input', '').strip()

    try:
        # 模式判斷
        if user_input.startswith("10.") or "doi.org" in user_input:
            mode = "doi"
            doi = user_input.replace("https://doi.org/", "").strip()
            meta = fetch_metadata_from_doi(doi)
        else:
            mode = "reference"
            meta = parse_reference(user_input)

        apa_ref = format_apa_reference(meta)
        citation = generate_citation_key(meta)

        return jsonify({
            "mode": mode,
            "status": "success",
            "reference": apa_ref,
            "citations": citation,
            "meta": meta
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500