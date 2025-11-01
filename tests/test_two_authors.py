"""
測試兩位作者的參考文獻解析
"""
from ..services.document_analyzer import DocumentAnalyzer
import re

def test_two_author_parsing():
    """測試兩位作者的參考文獻是否能正確解析"""
    
    # 模擬參考文獻文字
    test_references = """
References

Aly, M., & Kojima, H. (2020). Acute moderate-intensity exercise generally enhances neural resources related to perceptual and cognitive processes: A randomized controlled ERP study. Mental Health and Physical Activity, 19, 100363.

Smith, J., & Johnson, A. (2019). Test article. Journal Name, 10, 123-456.

Anderson, K., Brown, L., & Davis, M. (2021). Another test. Science, 15, 789-800.
"""
    
    analyzer = DocumentAnalyzer()
    
    # 分離主文和參考文獻區
    main_text, references_section = analyzer._separate_text_and_references(test_references)
    
    # 解析參考文獻
    reference_items = analyzer._parse_reference_section(references_section)
    
    print("=" * 80)
    print("參考文獻解析測試")
    print("=" * 80)
    
    for i, ref in enumerate(reference_items):
        print(f"\n【參考文獻 {i+1}】")
        print(f"原文: {ref['text'][:80]}...")
        print(f"作者數量: {len(ref['authors'])}")
        print(f"作者列表: {ref['authors']}")
        print(f"年份: {ref['year']}")
        
        # 生成引用格式
        from ..services.apa_formatter import generate_citation_key
        citation_keys = generate_citation_key({
            'authors': ref['authors'],
            'year': ref['year']
        })
        print(f"Parenthetical: {citation_keys['parenthetical']}")
        print(f"Narrative: {citation_keys['narrative']}")
    
    # 特別檢查 Aly & Kojima
    print("\n" + "=" * 80)
    print("重點檢查: Aly & Kojima (2020)")
    print("=" * 80)
    
    aly_kojima = next((ref for ref in reference_items if 'Aly' in ref['text']), None)
    
    if aly_kojima:
        if len(aly_kojima['authors']) == 2:
            print("✅ 正確：偵測到 2 位作者")
            print(f"   作者 1: {aly_kojima['authors'][0]}")
            print(f"   作者 2: {aly_kojima['authors'][1]}")
            
            from ..services.apa_formatter import generate_citation_key
            citation_keys = generate_citation_key({
                'authors': aly_kojima['authors'],
                'year': aly_kojima['year']
            })
            print(f"   Parenthetical: {citation_keys['parenthetical']}")
            print(f"   Narrative: {citation_keys['narrative']}")
        else:
            print(f"❌ 錯誤：只偵測到 {len(aly_kojima['authors'])} 位作者")
            print(f"   作者列表: {aly_kojima['authors']}")
    else:
        print("❌ 錯誤：找不到 Aly & Kojima 的參考文獻")

if __name__ == "__main__":
    test_two_author_parsing()

