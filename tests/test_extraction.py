import re

def extract_author_year_from_citation(citation_text: str):
    """測試版本：提取作者和年份"""
    clean_text = citation_text.strip()
    
    # 尋找年份
    year_match = re.search(r'(\d{4})', clean_text)
    year = year_match.group(1) if year_match else ""
    
    # 提取作者部分
    author = ""
    if year:
        # 對於括號內引用
        if clean_text.startswith('(') and clean_text.endswith(')'):
            inner = clean_text[1:-1]  # 移除括號
            year_pos = inner.find(year)
            if year_pos > 0:
                author_part = inner[:year_pos].strip()
            else:
                author_part = ""
        else:
            # 對於敘述型引用
            paren_pos = clean_text.find('(')
            if paren_pos > 0:
                author_part = clean_text[:paren_pos].strip()
            else:
                author_part = ""
        
        print(f"  原始 author_part: '{author_part}'")
        
        # 清理作者部分並提取第一個作者
        if author_part:
            # 移除尾部的標點和連接詞
            author_part = author_part.rstrip(',;.& ')
            print(f"  rstrip 後: '{author_part}'")
            
            # 處理 "et al." 情況 - 移除 "et al."
            author_part = re.sub(r'\s+et\s+al\.?$', '', author_part, flags=re.IGNORECASE).strip()
            print(f"  移除 et al 後: '{author_part}'")
            
            # 處理多作者情況：取第一個作者（在 & 或 , 或 and 之前）
            if '&' in author_part:
                author_part = author_part.split('&')[0].strip()
                print(f"  處理 & 後: '{author_part}'")
            elif ' and ' in author_part.lower():
                author_part = re.split(r'\s+and\s+', author_part, flags=re.IGNORECASE)[0].strip()
                print(f"  處理 and 後: '{author_part}'")
            
            # 如果還有逗號，可能是 "Last, First" 格式或多作者
            if ',' in author_part:
                parts = author_part.split(',')
                print(f"  split(',') 後: {parts}")
                if len(parts) >= 2 and re.match(r'^\s*[A-Z]\.?\s*$', parts[1]):
                    author_part = parts[0].strip()
                    print(f"  是 Last, F. 格式，取第一部分: '{author_part}'")
                else:
                    author_part = parts[0].strip()
                    print(f"  多作者或其他，取第一個: '{author_part}'")
            
            # 提取第一個有效的作者姓氏
            author_match = re.search(r'^([A-Z][a-zA-Z\-\']+)', author_part.strip())
            if author_match:
                author = author_match.group(1).rstrip('.,')
                print(f"  最終提取的 author: '{author}'")
    
    return {'author': author, 'year': year}

# 測試用例
test_cases = [
    "(Cai, et al., 2025)",
    "(Hillman, 2007)",
    "(Kojima, 2020)",
    "(Kao et al., 2020)",
    "(Baler & Volkow, 2006)",
]

print("=" * 60)
for test in test_cases:
    print(f"\n測試: {test}")
    result = extract_author_year_from_citation(test)
    print(f"結果: author='{result['author']}', year='{result['year']}'")
    print("-" * 60)

