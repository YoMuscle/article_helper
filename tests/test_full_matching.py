"""
測試完整的引用匹配 - 使用正確格式的 Aly & Kojima 和 Hillman
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.document_analyzer import DocumentAnalyzer

def test_full_matching():
    """測試正確格式的引用是否能匹配到參考文獻"""
    
    # 模擬完整文檔（使用正確格式）
    test_doc = """
Introduction

Recent studies (Aly & Kojima, 2020) have shown that exercise is beneficial.
Aly and Kojima (2020) also found similar results.
Previous research by Hillman (2007) supports this.
Another study Hillman (2007) confirmed the findings.

References

Aly, M., & Kojima, H. (2020). Acute moderate-intensity exercise generally enhances neural resources related to perceptual and cognitive processes: A randomized controlled ERP study. Mental Health and Physical Activity, 19, 100363.

Hillman, C. H. (2007). Be smart, exercise your heart: exercise effects on brain and cognition. Nature Reviews Neuroscience, 9(1), 58-65.
"""
    
    analyzer = DocumentAnalyzer()
    
    print("=" * 80)
    print("完整匹配測試")
    print("=" * 80)
    
    # 執行完整分析
    try:
        # 手動執行各步驟以便除錯
        main_text, references_section = analyzer._separate_text_and_references(test_doc)
        
        print("\n【步驟 1：分離文本】")
        print(f"主文長度: {len(main_text)} 字元")
        print(f"參考文獻區長度: {len(references_section)} 字元")
        print(f"\n參考文獻區內容:\n{references_section[:200]}...")
        
        # 解析參考文獻
        reference_items = analyzer._parse_reference_section(references_section)
        
        print("\n【步驟 2：解析參考文獻】")
        print(f"找到 {len(reference_items)} 個參考文獻")
        for ref in reference_items:
            print(f"\n  參考文獻 {ref['id']}:")
            print(f"    原文: {ref['text'][:80]}...")
            print(f"    作者: {ref['authors']}")
            print(f"    年份: {ref['year']}")
        
        # 生成引用格式
        reference_dict = analyzer._generate_citation_formats(reference_items)
        
        print("\n【步驟 3：生成引用格式】")
        for ref_id, ref_data in reference_dict.items():
            print(f"\n  參考文獻 {ref_id}:")
            print(f"    Parenthetical: {ref_data['parenthetical']}")
            print(f"    Narrative: {ref_data['narrative']}")
        
        # 找出文中的引用
        found_citations = analyzer._find_citations_in_text(main_text)
        
        print("\n【步驟 4：找出文中引用】")
        print(f"找到 {len(found_citations)} 個引用")
        for citation in found_citations:
            print(f"  - {citation['text']} (類型: {citation['type']}, 章節: {citation['section']})")
        
        # 檢查缺失的參考文獻
        missing_references = analyzer._check_missing_references(found_citations, reference_dict)
        
        print("\n【步驟 5：檢查缺失的參考文獻】")
        if missing_references:
            print(f"❌ 找到 {len(missing_references)} 個缺失的引用：")
            for item in missing_references:
                print(f"\n  引用: {item['citation']}")
                print(f"  章節: {item['section']}")
                if item.get('suggestion'):
                    print(f"  建議: {item['suggestion']}")
                    
                # 除錯：提取作者年份
                citation_info = analyzer._extract_author_year_from_citation(item['citation'])
                print(f"  [除錯] 提取的作者: '{citation_info.get('author')}', 年份: '{citation_info.get('year')}'")
        else:
            print("✅ 所有引用都有對應的參考文獻")
        
        # 檢查引用狀態
        citation_status = analyzer._mark_cited_references(found_citations, reference_dict)
        
        print("\n【步驟 6：標記已引用的參考文獻】")
        for status in citation_status:
            cited_mark = "✅" if status['cited'] else "❌"
            print(f"  {cited_mark} {status['parenthetical']}")
        
        print("\n" + "=" * 80)
        print("測試結果")
        print("=" * 80)
        
        # 驗證結果
        success = True
        
        # 檢查 Aly & Kojima
        aly_kojima_missing = any('Aly' in item['citation'] and 'Kojima' in item['citation'] 
                                  for item in missing_references)
        if aly_kojima_missing:
            print("❌ 失敗：(Aly & Kojima, 2020) 仍然被標記為缺失")
            success = False
        else:
            print("✅ 成功：(Aly & Kojima, 2020) 正確匹配")
        
        # 檢查 Hillman
        hillman_missing = any('Hillman' in item['citation'] for item in missing_references)
        if hillman_missing:
            print("❌ 失敗：Hillman (2007) 仍然被標記為缺失")
            success = False
        else:
            print("✅ 成功：Hillman (2007) 正確匹配")
        
        return success
        
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_matching()
    exit(0 if success else 1)


