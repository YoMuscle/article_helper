"""
測試參考文獻中 Lopez-Calderon 的解析
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer()

# 測試參考文獻解析
ref_text = "Lopez-Calderon, J., & Luck, S. J. (2014). ERPLAB: an open-source toolbox for the analysis of event-related potentials."

# 使用內部的解析方法
parsed_refs = analyzer._parse_reference_section(ref_text)

print(f"參考文獻: {ref_text}")
print(f"\n解析結果:")
for ref in parsed_refs:
    print(f"  作者數量: {len(ref['authors'])}")
    print(f"  作者列表: {ref['authors']}")
    print(f"  年份: {ref['year']}")
    
    # 提取第一作者
    if ref['authors']:
        first_author = ref['authors'][0].split(",")[0].lower().strip()
        print(f"  第一作者（小寫）: '{first_author}'")
