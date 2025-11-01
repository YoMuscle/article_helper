"""
測試 Lopez-Calderon 的作者提取
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer()

# 測試提取
citation = "(Lopez-Calderon & Luck, 2014)"
result = analyzer._extract_author_year_from_citation(citation)

print(f"引用: {citation}")
print(f"提取的作者: '{result['author']}'")
print(f"提取的年份: '{result['year']}'")
