import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
測試兩位作者引用的作者年份提取
"""
from services.document_analyzer import DocumentAnalyzer

def test_two_author_extraction():
    """測試兩位作者引用是否能正確提取第一作者"""
    
    analyzer = DocumentAnalyzer()
    
    test_cases = [
        # (引用, 期望的第一作者, 期望的年份)
        ("(Aly & Kojima, 2020)", "Aly", "2020"),
        ("Aly and Kojima (2020)", "Aly", "2020"),
        ("(Smith & Johnson, 2019)", "Smith", "2019"),
        ("Smith and Johnson (2019)", "Smith", "2019"),
        ("(De Menezes & Silva, 2016)", "De", "2016"),
        ("Lopez-Calderon and Delorme (2014)", "Lopez-Calderon", "2014"),
    ]
    
    print("=" * 80)
    print("測試兩位作者引用的作者年份提取")
    print("=" * 80)
    
    all_success = True
    
    for citation, expected_author, expected_year in test_cases:
        result = analyzer._extract_author_year_from_citation(citation)
        extracted_author = result.get('author', '')
        extracted_year = result.get('year', '')
        
        is_correct = (extracted_author == expected_author and extracted_year == expected_year)
        status = "✅" if is_correct else "❌"
        
        print(f"\n{status} 引用: {citation}")
        print(f"   期望: 作者='{expected_author}', 年份='{expected_year}'")
        print(f"   結果: 作者='{extracted_author}', 年份='{extracted_year}'")
        
        if not is_correct:
            all_success = False
    
    print("\n" + "=" * 80)
    if all_success:
        print("✅ 所有測試通過")
    else:
        print("❌ 部分測試失敗")
    
    return all_success

if __name__ == "__main__":
    success = test_two_author_extraction()
    exit(0 if success else 1)

