import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.document_analyzer import DocumentAnalyzer

def test_real_document_simulation():
    test_doc = """
Introduction
Recent studies (Aly & Kojima, 2020) found results.

References
Aly, M., & Kojima, H. (2020). Test paper. Journal, 10, 1-10.
"""
    analyzer = DocumentAnalyzer()
    main_text, refs = analyzer._separate_text_and_references(test_doc)
    ref_items = analyzer._parse_reference_section(refs)
    ref_dict = analyzer._generate_citation_formats(ref_items)
    citations = analyzer._find_citations_in_text(main_text)
    missing = analyzer._check_missing_references(citations, ref_dict)
    
    print("References:", len(ref_items))
    print("Citations:", len(citations))
    print("Missing:", len(missing))
    return len(missing) == 0

if __name__ == "__main__":
    success = test_real_document_simulation()
    print("Test passed!" if success else "Test failed!")


