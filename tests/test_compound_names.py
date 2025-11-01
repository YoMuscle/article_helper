import re

# 測試複合姓氏的匹配
author_pattern_old = r'([A-Z][a-zA-Z\-\']+),\s*([A-Z][\.\-\s]*[A-Z]*[\.\s]*[A-Z]*\.?)'
author_pattern_new = r'([A-Z][a-zA-Z\-\'\s]+?),\s*([A-Z][\.\-\s]*[A-Z]*[\.\s]*[A-Z]*\.?)'

test_cases = [
    "De Menezes, K. J., Peixoto, C., Nardi, A. E.",
    "Delorme, A., & Makeig, S.",
    "Ebbeling, C. B., Ward, A., Puleo, E. M.",
    "Van der Berg, A. B., Smith, C. D.",
    "Chang, Y.-K., Labban, J. D.",
]

print("=" * 80)
print("測試複合姓氏匹配")
print("=" * 80)

for test in test_cases:
    print(f"\n測試字串: '{test}'")
    
    # 舊模式
    old_matches = re.findall(author_pattern_old, test)
    print(f"  舊模式結果: {old_matches}")
    
    # 新模式
    new_matches = re.findall(author_pattern_new, test)
    print(f"  新模式結果: {new_matches}")
    
    if new_matches:
        print(f"  第一作者: '{new_matches[0][0].strip()}'")

