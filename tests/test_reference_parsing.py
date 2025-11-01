import re
from typing import List, Dict

def parse_reference_section(references_text: str) -> List[Dict[str, str]]:
    """測試版本：解析參考文獻"""
    if not references_text.strip():
        return []
    
    lines = references_text.split('\n')
    merged_references = []
    current_ref = ""
    
    print("=" * 80)
    print("開始解析參考文獻...")
    print("=" * 80)
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        print(f"\n第 {idx} 行: '{line}'")
        
        # 判斷是否是新的參考文獻開始
        is_new_reference_start = (
            re.match(r'^[A-Z][a-zA-Z\-\']+,\s+[A-Z]', line) or
            re.match(r'^[A-Z][a-zA-Z\-\']+\s+\(', line) or
            re.match(r'^[A-Z][a-zA-Z\-\']+,\s+&', line)
        )
        
        has_year = current_ref and (
            re.search(r'\(\d{4}\)', current_ref) or
            re.search(r',\s*\d{4}\.', current_ref) or
            re.search(r'\s+\d{4}\.', current_ref)
        )
        
        print(f"  is_new_reference_start: {is_new_reference_start}")
        print(f"  has_year in current_ref: {has_year}")
        print(f"  current_ref 長度: {len(current_ref)}")
        
        if is_new_reference_start and has_year:
            print(f"  → 保存上一個參考文獻，開始新的")
            merged_references.append(current_ref.strip())
            print(f"     已保存: '{current_ref[:60]}...'")
            current_ref = line
        else:
            print(f"  → 合併到當前參考文獻")
            if current_ref:
                current_ref += " " + line
            else:
                current_ref = line
    
    # 最後一個
    if current_ref and (
        re.search(r'\(\d{4}\)', current_ref) or
        re.search(r',\s*\d{4}\.', current_ref) or
        re.search(r'\s+\d{4}\.', current_ref)
    ):
        merged_references.append(current_ref.strip())
        print(f"\n最後一個參考文獻已保存")
    
    print("\n" + "=" * 80)
    print(f"共合併了 {len(merged_references)} 個參考文獻")
    print("=" * 80)
    
    # 解析年份
    references = []
    for i, line in enumerate(merged_references):
        print(f"\n參考文獻 {i+1}:")
        print(f"  內容: {line[:100]}...")
        
        year = None
        year_match = re.search(r'\((\d{4})\)', line)
        if year_match:
            year = year_match.group(1)
            print(f"  找到括號年份: {year}")
        else:
            year_match = re.search(r'[,\s](\d{4})\.', line)
            if year_match:
                year = year_match.group(1)
                print(f"  找到其他格式年份: {year}")
        
        if year:
            # 簡單提取第一作者
            first_author_match = re.match(r'^([A-Z][a-zA-Z\-\']+)', line)
            first_author = first_author_match.group(1) if first_author_match else "Unknown"
            
            references.append({
                'id': i + 1,
                'first_author': first_author,
                'year': year,
                'text': line[:100] + '...' if len(line) > 100 else line
            })
            print(f"  ✓ 第一作者: {first_author}, 年份: {year}")
        else:
            print(f"  ✗ 未找到年份，跳過")
    
    return references


# 測試用例：模擬跨頁的參考文獻
test_text = """
De Menezes, K. J., Peixoto, C., Nardi, A. E., Carta, M. G., Machado, S., & Veras, A.
B. (2016). Dehydroepiandrosterone, Its Sulfate and Cognitive Functions. Clinical Practice and Epidemiology in Mental Health: CP and EMH, 12, 24–37.

Delorme, A., & Makeig, S. (2004).
EEGLAB: An open source toolbox for analysis of single-trial EEG dynamics. Neuroscience Methods, 134(1), 9-21.

Ebbeling, C. B., Ward, A., Puleo, E. M., Widrick, J., & Rippe, J. M. (1991).
Development of a single-stage submaximal treadmill walking test. Medicine and Science in Sports and Exercise, 23(8), 966-973.
"""

print("\n\n測試跨頁參考文獻解析")
print("=" * 80)
references = parse_reference_section(test_text)

print("\n\n最終結果：")
print("=" * 80)
for ref in references:
    print(f"{ref['id']}. {ref['first_author']} ({ref['year']})")

