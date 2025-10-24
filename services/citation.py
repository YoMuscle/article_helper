@bp.route('/api/suggest_doi', methods=['GET'])
def suggest_doi():
    prefix = request.args.get('prefix', '').strip()
    if not prefix:
        return jsonify([])

    results = suggest_doi_candidates(prefix)
    return jsonify(results)