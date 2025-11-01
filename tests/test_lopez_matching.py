"""
測試 Lopez-Calderon 的完整匹配流程
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer()

# 模擬引用
citation = "(Lopez-Calderon & Luck, 2014)"
citation_info = analyzer._extract_author_year_from_citation(citation)
citation_author = citation_info.get('author', '').lower().strip()
citation_year = citation_info.get('year', '').strip()

print(f"引用: {citation}")
print(f"提取的作者（小寫）: '{citation_author}'")
print(f"提取的年份: '{citation_year}'")

# 模擬參考文獻
ref_text = "Lopez-Calderon, J., & Luck, S. J. (2014). ERPLAB: an open-source toolbox."
parsed_refs = analyzer._parse_reference_section(ref_text)

if parsed_refs:
    ref = parsed_refs[0]
    ref_authors = ref.get('authors', [])
    ref_year = ref.get('year', '').strip()
    
    if ref_authors:
        first_ref_author = ref_authors[0].split(",")[0].lower().strip()
        
        print(f"\n參考文獻:")
        print(f"  第一作者（小寫）: '{first_ref_author}'")
        print(f"  年份: '{ref_year}'")
        
        # 比對
        print(f"\n匹配檢查:")
        print(f"  作者匹配: {citation_author} == {first_ref_author} ? {citation_author == first_ref_author}")
        print(f"  年份匹配: {citation_year} == {ref_year} ? {citation_year == ref_year}")
        
        if citation_author == first_ref_author and citation_year == ref_year:
            print(f"\n✅ 匹配成功！")
        else:
            print(f"\n❌ 匹配失敗！")
