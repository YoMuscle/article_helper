"""
測試 regex pattern 匹配
"""
import re

# 測試不同的引用格式
test_cases = [
    "(Klimesch, 1999)",  # 正確格式
    "(Klimesch 1999)",   # 缺少逗號
    "(Klimesch 1999; Klimesch and Sauseng, 2007; Cooke, 2015)",  # 複雜案例
]

patterns = [
    r'\([A-Za-z][^)]*\d{4}[^)]*\)',  # 基本 pattern
    r'\([A-Za-z][^)]*,\s*\d{4}[^)]*\)',  # 要求有逗號
]

for test in test_cases:
    print(f"\n測試: {test}")
    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, test)
        print(f"  Pattern {i}: {matches if matches else '無匹配'}")
