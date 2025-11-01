import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
測試模糊比對改進 - 確保即使格式錯誤的引用也能正確匹配到參考文獻
"""
from services.document_analyzer import DocumentAnalyzer

def test_extract_author_year():
    """測試作者和年份提取功能"""
    analyzer = DocumentAnalyzer()
    
    test_cases = [
        # (輸入, 期望的作者, 期望的年份)
        ("(Kojima, 2020)", "Kojima", "2020"),
        ("(Erickson et al., 2019)", "Erickson", "2019"),
        ("(Gonzalez et al., 2019)", "Gonzalez", "2019"),
        ("(Chu et al., 2023)", "Chu", "2023"),
        ("Hillman (2007)", "Hillman", "2007"),
        ("(De Menezes et al., 2016)", "De", "2016"),
        ("(Volkov, 2006)", "Volkov", "2006"),
        ("(American College of Sports Medicine, 2014)", "American", "2014"),
        ("(Jacobsen et al., 2021)", "Jacobsen", "2021"),
        ("(Medicine, 2014)", "Medicine", "2014"),
        ("(Kao et al., 2017)", "Kao", "2017"),
        # 缺少左括號的情況
        ("Wang et al., 2024)", "Wang", "2024"),
        # 多個年份的情況（會被拆分）
        ("(Wang et al., 2015, 2016)", "Wang", "2015"),  # 應該提取第一個年份
    ]
    
    print("=" * 80)
    print("測試作者和年份提取功能")
    print("=" * 80)
    
    success_count = 0
    for citation_text, expected_author, expected_year in test_cases:
        result = analyzer._extract_author_year_from_citation(citation_text)
        extracted_author = result.get('author', '')
        extracted_year = result.get('year', '')
        
        is_correct = (extracted_author == expected_author and extracted_year == expected_year)
        status = "✅" if is_correct else "❌"
        
        print(f"\n{status} 引用: {citation_text}")
        print(f"   期望: 作者='{expected_author}', 年份='{expected_year}'")
        print(f"   結果: 作者='{extracted_author}', 年份='{extracted_year}'")
        
        if is_correct:
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"測試結果: {success_count}/{len(test_cases)} 通過")
    print("=" * 80)

if __name__ == "__main__":
    test_extract_author_year()

