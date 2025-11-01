import re

def extract_author_year_from_citation(citation_text: str):
    """從引用中提取作者和年份"""
    clean_text = citation_text.strip()
    
    # 尋找年份
    year_match = re.search(r'(\d{4})', clean_text)
    year = year_match.group(1) if year_match else ""
    
    # 提取作者部分
    author = ""
    if year:
        if clean_text.startswith('(') and clean_text.endswith(')'):
            inner = clean_text[1:-1]  # 移除括號
            year_pos = inner.find(year)
            if year_pos > 0:
                author_part = inner[:year_pos].strip()
            else:
                author_part = ""
        else:
            paren_pos = clean_text.find('(')
            if paren_pos > 0:
                author_part = clean_text[:paren_pos].strip()
            else:
                author_part = ""
        
        if author_part:
            # 移除尾部的標點和連接詞
            author_part = author_part.rstrip(',;.& ')
            
            # 處理 "et al." 情況
            author_part = re.sub(r'\s+et\s+al\.?$', '', author_part, flags=re.IGNORECASE).strip()
            
            # 處理多作者情況
            if '&' in author_part:
                author_part = author_part.split('&')[0].strip()
            elif ' and ' in author_part.lower():
                author_part = re.split(r'\s+and\s+', author_part, flags=re.IGNORECASE)[0].strip()
            
            # 如果還有逗號
            if ',' in author_part:
                parts = author_part.split(',')
                if len(parts) >= 2 and re.match(r'^\s*[A-Z]\.?\s*$', parts[1]):
                    author_part = parts[0].strip()
                else:
                    author_part = parts[0].strip()
            
            # 提取第一個有效的作者姓氏
            author_match = re.search(r'^([A-Z][a-zA-Z\-\']+)', author_part.strip())
            if author_match:
                author = author_match.group(1).rstrip('.,')
    
    return {'author': author, 'year': year}


# 測試案例
test_citations = [
    "(Delorme & Makeig, 2004)",
    "(Lopez-Calderon & Luck, 2014)",
]

# 模擬參考文獻
references = [
    {'first_author': 'Delorme', 'year': '2004'},
    {'first_author': 'Lopez', 'year': '2014'},  # 注意：只提取到 Lopez（不是 Lopez-Calderon）
]

print("=" * 80)
print("測試引用比對邏輯")
print("=" * 80)

for citation in test_citations:
    print(f"\n引用: {citation}")
    info = extract_author_year_from_citation(citation)
    print(f"  提取結果: author='{info['author']}', year='{info['year']}'")
    
    # 嘗試匹配參考文獻
    matched = False
    for ref in references:
        if info['author'].lower() == ref['first_author'].lower() and info['year'] == ref['year']:
            print(f"  ✓ 匹配到參考文獻: {ref['first_author']} ({ref['year']})")
            matched = True
            break
    
    if not matched:
        print(f"  ✗ 未找到匹配的參考文獻")

