import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
測試 Kojima 單獨引用的情況（應該建議使用 Aly & Kojima）
"""
from services.document_analyzer import DocumentAnalyzer

def test_kojima_suggestion():
    """測試當只引用 Kojima 時，是否會建議完整的 Aly & Kojima"""
    
    # 模擬完整文檔
    test_doc = """
Introduction

Recent studies (Kojima, 2020) have shown that exercise is beneficial.

References

Aly, M., & Kojima, H. (2020). Acute moderate-intensity exercise generally enhances neural resources related to perceptual and cognitive processes: A randomized controlled ERP study. Mental Health and Physical Activity, 19, 100363.
"""
    
    analyzer = DocumentAnalyzer()
    
    # 分離主文和參考文獻
    main_text, references_section = analyzer._separate_text_and_references(test_doc)
    
    # 解析參考文獻
    reference_items = analyzer._parse_reference_section(references_section)
    
    # 生成引用格式
    reference_dict = analyzer._generate_citation_formats(reference_items)
    
    # 找出文中的引用
    found_citations = analyzer._find_citations_in_text(main_text)
    
    # 檢查缺失的參考文獻
    missing_references = analyzer._check_missing_references(found_citations, reference_dict)
    
    print("=" * 80)
    print("測試 Kojima 單獨引用的建議功能")
    print("=" * 80)
    
    print("\n【參考文獻列表】")
    for ref_id, ref_data in reference_dict.items():
        print(f"  - {ref_data['parenthetical']}")
        print(f"    作者: {ref_data['item']['authors']}")
    
    print("\n【文中的引用】")
    for citation in found_citations:
        print(f"  - {citation['text']}")
    
    print("\n【缺失的參考文獻檢查】")
    if missing_references:
        for item in missing_references:
            print(f"\n❌ 引用: {item['citation']}")
            print(f"   章節: {item['section']}")
            if item.get('suggestion'):
                print(f"   💡 建議: {item['suggestion']}")
            else:
                print(f"   ⚠️ 沒有找到建議")
    else:
        print("✅ 所有引用都有對應的參考文獻")
    
    print("\n" + "=" * 80)
    print("結論")
    print("=" * 80)
    
    # 驗證是否有建議
    if missing_references and missing_references[0].get('suggestion'):
        suggestion = missing_references[0]['suggestion']
        if 'Aly & Kojima' in suggestion:
            print("✅ 測試成功！系統正確建議使用 'Aly & Kojima, 2020'")
            return True
        else:
            print(f"❌ 測試失敗：建議內容不正確 - {suggestion}")
            return False
    else:
        print("❌ 測試失敗：沒有生成建議")
        return False

if __name__ == "__main__":
    success = test_kojima_suggestion()
    exit(0 if success else 1)

