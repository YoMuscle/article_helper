import re
from docx import Document
from typing import Dict, List, Tuple, Any
from .apa_formatter import generate_citation_key

class DocumentAnalyzer:
    def __init__(self):
        self.parenthetical_patterns = [
            r'\([A-Za-z][^)]*\d{4}[^)]*\)',  # (Author, 2023)
            r'\([A-Za-z][^)]*et al\.[^)]*\d{4}[^)]*\)',  # (Author et al., 2023)
            r'\([A-Za-z][^)]*&[^)]*\d{4}[^)]*\)',  # (Author & Author, 2023)
        ]
        # 添加：匹配缺少左括號的引用（格式錯誤但仍需識別）
        self.malformed_parenthetical_patterns = [
            r'(?<!\()[A-Z][a-z]+\s+et al\.,\s*\d{4}\)',  # Wang et al., 2024) - 缺左括號
            r'(?<!\()[A-Z][a-z]+(?:\s+&\s+[A-Z][a-z]+)?,\s*\d{4}\)',  # Wang & Smith, 2024) - 缺左括號
        ]
        self.narrative_patterns = [
            r'[A-Za-z]+\s+\(\d{4}\)',  # Author (2023)
            r'[A-Za-z]+\s+et al\.\s+\(\d{4}\)',  # Author et al. (2023)
            r'[A-Za-z]+\s+and\s+[A-Za-z]+\s+\(\d{4}\)',  # Author and Author (2023)
            r'[A-Za-z]+\s+&\s+[A-Za-z]+\s+\(\d{4}\)',  # Author & Author (2023)
        ]

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        try:
            doc_text = self._extract_text_from_docx(file_path)
            main_text, references_section = self._separate_text_and_references(doc_text)
            reference_items = self._parse_reference_section(references_section)
            reference_dict = self._generate_citation_formats(reference_items)
            found_citations = self._find_citations_in_text(main_text)
            format_errors = self._check_citation_formats(found_citations, reference_dict)
            missing_references = self._check_missing_references(found_citations, reference_dict)
            citation_status = self._mark_cited_references(found_citations, reference_dict)
            
            # 生成檢查摘要
            total_errors = len(format_errors)
            total_missing = len(missing_references)
            total_uncited = sum(1 for ref in citation_status if not ref['cited'])
            
            # 判斷整體狀態
            if total_errors == 0 and total_missing == 0 and total_uncited == 0:
                overall_status = 'excellent'
                status_message = '✅ 太棒了！沒有發現任何問題，可以準備投稿了！'
            elif total_errors + total_missing <= 5 and total_uncited <= 3:
                overall_status = 'good'
                status_message = '✅ 整體良好，只有少數問題需要修正。'
            elif total_errors + total_missing <= 10:
                overall_status = 'needs_revision'
                status_message = '⚠️ 發現一些問題，建議修正後再投稿。'
            else:
                overall_status = 'needs_major_revision'
                status_message = '❌ 發現較多問題，需要仔細檢查並修正。'
            
            return {
                'format_errors': format_errors,
                'missing_references': missing_references,
                'citation_status': citation_status,
                'total_references': len(reference_items),
                'total_citations': len(found_citations),
                'summary': {
                    'total_errors': total_errors,
                    'total_missing': total_missing,
                    'total_uncited': total_uncited,
                    'overall_status': overall_status,
                    'status_message': status_message
                }
            }
        except Exception as e:
            raise Exception(f"文檔分析失敗: {str(e)}")

    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            return '\n'.join(full_text)
        except Exception as e:
            raise Exception(f"無法讀取文檔: {str(e)}")

    def _separate_text_and_references(self, text: str) -> Tuple[str, str]:
        # 支援多語言的 References 標題
        patterns = [
            r'\n\s*References\s*\n',
            r'\n\s*Reference\s*\n',
            r'\n\s*參考文獻\s*\n',
            r'\n\s*REFERENCES\s*\n',
            r'\n\s*Bibliography\s*\n',  # 英文替代
            r'\n\s*Works Cited\s*\n',  # MLA 格式
            r'\n\s*Literatur\s*\n',    # 德文
            r'\n\s*Bibliographie\s*\n', # 法文
            r'\n\s*参考文献\s*\n',      # 簡體中文
        ]
        
        # 找到所有匹配，取最後一個（因為可能有多個標題）
        all_matches = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            all_matches.extend(matches)
        
        if all_matches:
            # 按位置排序，取最後一個
            all_matches.sort(key=lambda m: m.start())
            match = all_matches[-1]
            
            split_point = match.end()
            main_text = text[:match.start()]
            references_section = text[split_point:]
            
            return main_text, references_section
        
        # 未找到 References 標題，使用 80% 分割
        split_point = int(len(text) * 0.8)
        return text[:split_point], text[split_point:]

    def _parse_reference_section(self, references_text: str) -> List[Dict[str, str]]:
        """
        解析參考文獻部分，提取每個條目，並嘗試抓出所有作者與年份
        """
        if not references_text.strip():
            return []
        
        # 改進：將多行的參考文獻合併成單行
        # 參考文獻可能跨越多行，需要先合併
        lines = references_text.split('\n')
        merged_references = []
        current_ref = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳過常見的標題行
            if re.match(r'^(References|Reference|參考文獻|参考文献|REFERENCES|Bibliography|Works Cited|Literatur|Bibliographie)$', line, re.IGNORECASE):
                continue
            
            # 判斷是否是新的參考文獻開始
            # 通常以大寫字母開頭，且符合 "姓, 名縮寫" 或 "姓 (" 的模式
            # 如果當前參考文獻已經有內容且包含年份，且新行看起來是新參考文獻的開頭
            is_new_reference_start = (
                re.match(r'^[A-Z][a-zA-Z\-\']+,\s+[A-Z]', line) or  # 匹配 "Last, F."
                re.match(r'^[A-Z][a-zA-Z\-\']+\s+\(', line) or      # 匹配 "Last ("
                re.match(r'^[A-Z][a-zA-Z\-\']+,\s+&', line)         # 匹配 "Last, &"
            )
            
            # 檢查當前參考文獻是否包含年份（支援多種格式）
            has_year = current_ref and (
                re.search(r'\(\d{4}\)', current_ref) or  # 括號格式: (2020)
                re.search(r',\s*\d{4}\.', current_ref) or  # 逗號+年份+句點: , 1998.
                re.search(r'\s+\d{4}\.', current_ref)      # 空格+年份+句點: 1998.
            )
            
            if is_new_reference_start and has_year:
                # 上一個參考文獻結束，保存它
                merged_references.append(current_ref.strip())
                current_ref = line
            else:
                # 繼續合併到當前參考文獻
                if current_ref:
                    current_ref += " " + line
                else:
                    current_ref = line
        
        # 別忘了最後一個（支援多種年份格式）
        if current_ref and (
            re.search(r'\(\d{4}\)', current_ref) or
            re.search(r',\s*\d{4}\.', current_ref) or
            re.search(r'\s+\d{4}\.', current_ref)
        ):
            merged_references.append(current_ref.strip())
        
        # 解析每個合併後的參考文獻
        references = []
        for i, line in enumerate(merged_references):
            # 改良的作者和年份解析
            # 支援多種年份格式：(2020)、, 1998.、1998.
            year = None
            year_match = re.search(r'\((\d{4})\)', line)  # 優先匹配括號格式
            if year_match:
                year = year_match.group(1)
                authors_end_pos = year_match.start()
            else:
                # 嘗試匹配其他格式：逗號+年份+句點 或 空格+年份+句點
                year_match = re.search(r'[,\s](\d{4})\.', line)
                if year_match:
                    year = year_match.group(1)
                    authors_end_pos = year_match.start()
                else:
                    continue  # 沒找到年份，跳過這個條目
            
            # 獲取年份前的部分作為作者區域
            authors_part = line[:authors_end_pos].strip()
            
            # 解析作者 - 使用更強大的方法
            authors = []
            
            # 方法：尋找 "姓, 名縮寫" 的模式
            # 支援各種格式：Last, F. M. / Last, F.-M. / Last, Y.-K. 等
            # 也支援複合姓氏：De Menezes, K. J. / Van der Berg, A. B.
            # 匹配模式：從開頭到第一個逗號（姓氏），然後是名字縮寫
            author_pattern = r'([A-Z][a-zA-Z\-\'\s]+?),\s*([A-Z][\.\-\s]*[A-Z]*[\.\s]*[A-Z]*\.?)'
            
            matches = re.findall(author_pattern, authors_part)
            
            if matches:
                # 找到完整的 "姓, 名" 格式
                for last_name, initials in matches:
                    # 清理姓氏（去除尾部空格）
                    last_name = last_name.strip()
                    # 清理名字縮寫
                    clean_initials = initials.strip().rstrip('.')
                    if not clean_initials.endswith('.'):
                        clean_initials += '.'
                    authors.append(f"{last_name}, {clean_initials}")
            else:
                # 備用方法：只提取姓氏
                # 先移除 "et al." 以避免干擾
                clean_authors_part = re.sub(r'\bet\s+al\.?', '', authors_part, flags=re.IGNORECASE)
                
                # 用 & 和 , 分割
                parts = re.split(r'[&,]', clean_authors_part)
                
                for part in parts:
                    part = part.strip()
                    # 找到姓氏（可能是複合姓氏，匹配到逗號、& 或結尾）
                    # 支援 "De Menezes" 等複合姓氏
                    match = re.match(r'^([A-Z][a-zA-Z\-\'\s]+?)(?:\s+[A-Z]\.|\s*$)', part)
                    if match:
                        last_name = match.group(1).strip().rstrip('.,')
                        if f"{last_name}," not in [a.split(',')[0] + ',' for a in authors]:
                            authors.append(f"{last_name},")
            
            if authors and year:
                references.append({
                    'id': i + 1,
                    'text': line,
                    'authors': authors,  # 保留所有作者，不限制數量
                    'year': year,
                })
        return references

    def _generate_citation_formats(self, reference_items: list) -> dict:
        """為每個參考文獻產生 Parenthetical/Narrative 格式（用現有 generate_citation_key）"""
        reference_dict = {}
        for item in reference_items:
            meta = {
                "authors": item.get("authors", []),
                "year": item.get("year", "")
            }
            citation_keys = generate_citation_key(meta)
            reference_dict[item['id']] = {
                'item': item,
                'parenthetical': citation_keys['parenthetical'],
                'narrative': citation_keys['narrative'],
                'cited': False
            }
        return reference_dict

    def _find_citations_in_text(self, text: str) -> List[Dict[str, str]]:
        """改良版：能識別括號內多個引用的情況，並記錄所在章節"""
        citations = []
        
        # 檢測章節標題
        def get_section(position: int) -> str:
            """根據位置判斷所在章節"""
            text_before = text[:position]
            
            # 常見的章節標題模式（支援編號和無編號）
            section_patterns = [
                (r'\n\s*\d*\.?\s*Abstract\s*\n', 'Abstract'),
                (r'\n\s*\d*\.?\s*Introduction\s*\n', 'Introduction'),
                (r'\n\s*\d*\.?\s*Method[s]?\s*\n', 'Methods'),
                (r'\n\s*\d*\.?\s*Material[s]?\s+and\s+Method[s]?\s*\n', 'Methods'),
                (r'\n\s*\d*\.?\s*Result[s]?\s*\n', 'Results'),
                (r'\n\s*\d*\.?\s*Finding[s]?\s*\n', 'Results'),  # 替代用詞
                (r'\n\s*\d*\.?\s*Discussion\s*\n', 'Discussion'),
                (r'\n\s*\d*\.?\s*Conclusion[s]?\s*\n', 'Conclusion'),
                (r'\n\s*\d*\.?\s*Reference[s]?\s*\n', 'References'),
                (r'\n\s*\d*\.?\s*Background\s*\n', 'Background'),  # 常見章節
                (r'\n\s*\d*\.?\s*Experiment[s]?\s*\n', 'Experiments'),
            ]
            
            # 找到最近的章節標題
            current_section = 'Document Start'
            last_match_pos = -1
            
            for pattern, section_name in section_patterns:
                matches = list(re.finditer(pattern, text_before, re.IGNORECASE))
                if matches:
                    last_match = matches[-1]  # 取最後一個匹配
                    if last_match.start() > last_match_pos:
                        last_match_pos = last_match.start()
                        current_section = section_name
            
            return current_section
        
        # 先找所有括號內引用
        processed_ranges = []  # 記錄已處理的位置範圍，避免重複處理
        
        for pattern in self.parenthetical_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # 檢查這個 match 是否已經被處理過
                match_start = match.start()
                match_end = match.end()
                is_already_processed = False
                for proc_start, proc_end in processed_ranges:
                    # 如果有重疊，跳過
                    if not (match_end <= proc_start or match_start >= proc_end):
                        is_already_processed = True
                        break
                
                if is_already_processed:
                    continue
                
                # 標記這個範圍為已處理
                processed_ranges.append((match_start, match_end))
                
                citation_text = match.group()
                section = get_section(match.start())
                
                # 檢查是否包含分號（表示多個引用）
                if ';' in citation_text:
                    # 先檢查分號前後的空格格式
                    semicolon_errors = []
                    if re.search(r'\s;', citation_text):
                        semicolon_errors.append('APA 7 格式中，分號前不應該有空格')
                    if re.search(r';[^\s)]', citation_text):  # 注意：分號後可以是空格或右括號
                        semicolon_errors.append('APA 7 格式中，分號後應該有空格，例如：(Author A, 2015; Author B, 2016)')
                    
                    # 分割多個引用
                    inner = citation_text[1:-1]  # 移除括號
                    parts = inner.split(';')
                    for i, part in enumerate(parts):
                        part = part.strip()
                        if part and re.search(r'\d{4}', part):
                            # 為每個部分計算不同的位置偏移，避免去重時被誤刪
                            # 使用微小的位置偏移（0.1, 0.2, ...）來區分同一括號內的多個引用
                            position_offset = match.start() + (i * 0.1)
                            citation_dict = {
                                'text': f"({part})",
                                'original_text': part,
                                'type': 'parenthetical',
                                'position': position_offset,  # 使用偏移後的位置
                                'end_position': match.end(),
                                'section': section,
                                'has_parentheses': True,
                                'from_multi_citation': True,  # 標記來自多重引用
                                'original_multi_citation': citation_text  # 保存原始多重引用文本
                            }
                            # 如果有分號格式錯誤，只在第一個引用上標記（避免重複）
                            if i == 0 and semicolon_errors:
                                citation_dict['semicolon_format_errors'] = semicolon_errors
                            citations.append(citation_dict)
                else:
                    # 檢查是否是同一作者多個年份（格式錯誤但仍需拆分來匹配）
                    # 例如：(Wang et al., 2015, 2016)
                    inner = citation_text[1:-1]  # 移除括號
                    multi_year_match = re.search(r'([A-Z][a-z]+(?:\s+et al\.|(?:\s+&\s+[A-Z][a-z]+))?),\s*(\d{4}),\s*(\d{4})', inner)
                    if multi_year_match:
                        author_part = multi_year_match.group(1)
                        year1 = multi_year_match.group(2)
                        year2 = multi_year_match.group(3)
                        # 拆分成兩個引用來匹配
                        citations.append({
                            'text': f"({author_part}, {year1})",
                            'original_text': citation_text,  # 保留原始錯誤格式
                            'type': 'parenthetical',
                            'position': match.start(),
                            'end_position': match.end(),
                            'section': section,
                            'has_parentheses': True
                        })
                        citations.append({
                            'text': f"({author_part}, {year2})",
                            'original_text': citation_text,  # 保留原始錯誤格式
                            'type': 'parenthetical',
                            'position': match.start(),
                            'end_position': match.end(),
                            'section': section,
                            'has_parentheses': True
                        })
                    else:
                        # 正常的單一引用
                        citations.append({
                            'text': citation_text,
                            'original_text': citation_text,
                            'type': 'parenthetical',
                            'position': match.start(),
                            'end_position': match.end(),
                            'section': section,
                            'has_parentheses': True
                        })
        
        # 找缺少左括號的引用（格式錯誤但仍需識別）
        for pattern in self.malformed_parenthetical_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # 檢查是否已經被 parenthetical patterns 處理過
                match_start = match.start()
                match_end = match.end()
                is_already_processed = False
                for proc_start, proc_end in processed_ranges:
                    # 如果有重疊，跳過（因為已經被正常的 parenthetical pattern 處理了）
                    if not (match_end <= proc_start or match_start >= proc_end):
                        is_already_processed = True
                        break
                
                if is_already_processed:
                    continue
                
                citation_text = match.group()
                section = get_section(match.start())
                
                # 添加左括號來標準化
                normalized_text = f"({citation_text}"
                
                citations.append({
                    'text': normalized_text,  # 標準化後的文字
                    'original_text': citation_text,  # 原始文字（缺左括號）
                    'type': 'parenthetical',
                    'position': match.start(),
                    'end_position': match.end(),
                    'section': section,
                    'has_parentheses': False,  # 標記為缺括號
                    'malformed': True  # 標記為格式錯誤
                })
        
        # 找敘述型引用
        for pattern in self.narrative_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                section = get_section(match.start())
                citation_text = match.group()
                citations.append({
                    'text': citation_text,
                    'original_text': citation_text,
                    'type': 'narrative',
                    'position': match.start(),
                    'end_position': match.end(),  # 添加結束位置
                    'section': section,
                    'has_parentheses': True
                })
        
        # 智能去重：處理重疊的引用（保留較長的）
        citations = sorted(citations, key=lambda x: (x['position'], -len(x['text'])))  # 先按位置，再按長度倒序
        
        unique_citations = []
        for i, citation in enumerate(citations):
            # 如果是來自多重引用（分號分隔），不需要去重檢查
            if citation.get('from_multi_citation', False):
                unique_citations.append(citation)
                continue
            
            # 檢查是否與已選擇的引用重疊
            is_overlapping = False
            for selected in unique_citations:
                # 跳過多重引用的比對
                if selected.get('from_multi_citation', False):
                    continue
                
                # 檢查位置範圍是否重疊
                selected_start = selected['position']
                selected_end = selected.get('end_position', selected_start + len(selected['text']))
                current_start = citation['position']
                current_end = citation.get('end_position', current_start + len(citation['text']))
                
                # 如果重疊（有交集）
                if not (current_end <= selected_start or current_start >= selected_end):
                    # 保留較長的引用
                    if len(citation['text']) > len(selected['text']):
                        # 新的更長，移除舊的
                        unique_citations.remove(selected)
                        break  # 跳出內層循環，添加新的
                    else:
                        # 舊的更長或相等，跳過新的
                        is_overlapping = True
                        break
            
            if not is_overlapping:
                unique_citations.append(citation)
        
        # 最後按位置排序
        unique_citations = sorted(unique_citations, key=lambda x: x['position'])
        return unique_citations

    def _check_citation_formats(self, citations: List[Dict[str, str]], reference_dict: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        format_errors = []
        for citation in citations:
            citation_text = citation['text']
            citation_type = citation['type']
            original_text = citation.get('original_text', citation_text)
            error_messages = []  # 改為列表，可以累積多個錯誤
            
            # 檢查作者數量是否與參考文獻匹配
            # 提取引用中的作者和年份
            citation_info = self._extract_author_year_from_citation(citation_text)
            citation_author = citation_info.get('author', '').lower().strip()
            citation_year = citation_info.get('year', '').strip()
            
            if citation_author and citation_year:
                # 尋找匹配的參考文獻
                for ref_id, ref_data in reference_dict.items():
                    ref_authors = ref_data['item'].get('authors', [])
                    ref_year = ref_data['item'].get('year', '').strip()
                    
                    if not ref_authors or not ref_year:
                        continue
                    
                    # 提取第一作者的 last name
                    first_ref_author = ref_authors[0].split(",")[0].lower().strip()
                    
                    # 如果第一作者和年份匹配
                    if citation_author == first_ref_author and citation_year == ref_year:
                        # 檢查作者數量是否正確
                        num_ref_authors = len(ref_authors)
                        
                        # 檢查引用中是否使用了 et al.
                        has_et_al = 'et al.' in citation_text
                        
                        # 檢查引用中是否有兩位作者（使用 & 或 and）
                        has_two_authors = bool(re.search(r'&|and', citation_text, re.IGNORECASE))
                        
                        # APA 7 規則：3 位或以上作者必須使用 et al.
                        if num_ref_authors >= 3:
                            if not has_et_al:
                                # 檢查是否錯誤地列出了兩位作者
                                if has_two_authors:
                                    error_messages.append(f'APA 7 格式中，3 位或以上作者應使用 "et al."，建議改為: {ref_data["parenthetical"]}')
                                else:
                                    error_messages.append(f'APA 7 格式中，3 位或以上作者應使用 "et al."，建議改為: {ref_data["parenthetical"]}')
                        # APA 7 規則：2 位作者必須列出兩位
                        elif num_ref_authors == 2:
                            if has_et_al:
                                error_messages.append(f'APA 7 格式中，2 位作者應列出兩位作者名，建議改為: {ref_data["parenthetical"]}')
                        
                        break  # 找到匹配的參考文獻，停止搜索
            
            # 檢查括號完整性
            if citation.get('malformed', False):
                error_messages.append('缺少左括號 "("')
            
            # 檢查分號格式錯誤（來自多重引用拆分時的檢查）
            if 'semicolon_format_errors' in citation:
                error_messages.extend(citation['semicolon_format_errors'])
                # 使用原始多重引用文本作為錯誤報告的引用
                citation_text = citation.get('original_multi_citation', citation_text)
            
            # 檢查 et al. 前面是否有多餘的逗號（APA 7 不應該有）
            if ', et al.' in citation_text:
                error_messages.append('APA 7 格式中 "et al." 前面不應該有逗號')
            
            # 檢查 et al 後面是否缺少句點
            if re.search(r'\bet al[,\s]', citation_text) and 'et al.' not in citation_text:
                error_messages.append('APA 7 格式中應為 "et al."（需要句點）')
            
            # 檢查 et al. 後面是否缺少逗號和空格（在 parenthetical 中）
            if citation_type == 'parenthetical':
                # 檢查 et al. 後面缺少逗號
                if re.search(r'et al\.\s*\d{4}', citation_text):
                    error_messages.append('APA 7 格式中 "et al." 後面應該有逗號，例如：(Author et al., 2020)')
                # 檢查 et al., 後面缺少空格
                elif re.search(r'et al\.,\d{4}', citation_text):
                    error_messages.append('APA 7 格式中 "et al.," 後面應該有空格，例如：(Author et al., 2020)')
            
            # 檢查同一作者多個年份是否用逗號而非分號分隔
            # 例如：(Wang et al., 2015, 2016) 是錯誤的
            # 應該是：(Wang et al., 2015; Wang et al., 2016)
            if citation_type == 'parenthetical':
                # 匹配模式：作者名 et al., 年份, 年份
                multiple_years_pattern = r'([A-Z][a-z]+(?:\s+et al\.|(?:\s+&\s+[A-Z][a-z]+))?),\s*(\d{4}),\s*(\d{4})'
                match = re.search(multiple_years_pattern, citation_text)
                if match:
                    author = match.group(1)
                    year1 = match.group(2)
                    year2 = match.group(3)
                    error_messages.append(f'APA 7 格式中，同一作者的多個年份應用分號分隔並重複作者名，例如：({author}, {year1}; {author}, {year2})')
            
            # 檢查 parenthetical citation 中是否使用了 "and" 而非 "&"
            if citation_type == 'parenthetical' and re.search(r'\band\b', citation_text, re.IGNORECASE):
                error_messages.append('APA 7 格式中，括號內引用應使用 "&" 而非 "and"')
            
            # 檢查 narrative citation 中是否使用了 "&" 而非 "and"
            if citation_type == 'narrative' and '&' in citation_text:
                # 排除括號內的 &（因為年份在括號內是正常的）
                text_before_paren = citation_text.split('(')[0] if '(' in citation_text else citation_text
                if '&' in text_before_paren:
                    error_messages.append('APA 7 格式中，敘述型引用應使用 "and" 而非 "&"')
            
            # 基本格式檢查
            is_valid_format = False
            if citation_type == 'parenthetical':
                if re.match(r'\([A-Za-z][^)]*\d{4}[^)]*\)', citation_text):
                    is_valid_format = True
                else:
                    # 檢查是否缺少括號
                    if not citation_text.startswith('('):
                        error_messages.append('Parenthetical citation 應該有括號')
                        
            elif citation_type == 'narrative':
                if re.match(r'[A-Za-z]+.*\(\d{4}\)', citation_text):
                    is_valid_format = True
            
            # 如果有任何錯誤訊息，加入錯誤列表
            if error_messages:
                format_errors.append({
                    'citation': citation_text,
                    'type': citation_type,
                    'section': citation.get('section', 'Unknown'),
                    'error': ' / '.join(error_messages)  # 用 / 連接多個錯誤
                })
            elif not is_valid_format:
                format_errors.append({
                    'citation': citation_text,
                    'type': citation_type,
                    'section': citation.get('section', 'Unknown'),
                    'error': 'Format does not follow APA 7 guidelines'
                })
        return format_errors

    def _check_missing_references(self, citations: List[Dict[str, str]], reference_dict: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """改良版：使用模糊比對（第一作者 last name + 年份）來減少誤報"""
        missing_references = []
        
        for citation in citations:
            citation_text = citation['text']
            original_text = citation.get('original_text', citation_text)
            
            # 從 citation 中提取第一作者和年份
            citation_info = self._extract_author_year_from_citation(citation_text)
            citation_author = citation_info.get('author', '').lower().strip()
            citation_year = citation_info.get('year', '').strip()
            
            if not citation_author or not citation_year:
                # 無法提取作者或年份，但仍然嘗試精確比對
                # 不要直接跳過，嘗試精確匹配
                found_match = False
                for ref_id, ref_data in reference_dict.items():
                    if self._exact_citation_match(citation_text, original_text, ref_data):
                        found_match = True
                        break
                
                if not found_match:
                    missing_references.append({
                        'citation': citation_text,
                        'type': citation['type'],
                        'section': citation.get('section', 'Unknown')
                    })
                continue
            
            # 在 reference_dict 中尋找匹配的項目
            matching_refs = []
            for ref_id, ref_data in reference_dict.items():
                ref_authors = ref_data['item'].get('authors', [])
                ref_year = ref_data['item'].get('year', '').strip()
                
                if not ref_authors or not ref_year:
                    continue
                
                # 提取第一作者的 last name
                first_ref_author = ref_authors[0].split(",")[0].lower().strip()
                
                # 比對第一作者 + 年份
                if citation_author == first_ref_author and citation_year == ref_year:
                    matching_refs.append((ref_id, ref_data))
            
            # 判斷結果
            if len(matching_refs) == 0:
                # 完全沒找到 → 可能是缺少參考文獻，或是作者數量不匹配
                # 檢查是否有相同年份但不同作者的參考文獻（可能是只寫了部分作者）
                suggestion = None
                for ref_id, ref_data in reference_dict.items():
                    ref_authors = ref_data['item'].get('authors', [])
                    ref_year = ref_data['item'].get('year', '').strip()
                    
                    # 檢查年份是否匹配
                    if ref_year == citation_year:
                        # 檢查引用中的作者是否出現在參考文獻的作者列表中（任一位置）
                        for ref_author in ref_authors:
                            ref_author_last = ref_author.split(",")[0].lower().strip()
                            if citation_author == ref_author_last:
                                # 找到了！但不是第一作者
                                # 這可能表示引用格式錯誤（遺漏了其他作者）
                                suggestion = f"可能應該是: {ref_data['parenthetical']}"
                                break
                    if suggestion:
                        break
                
                missing_references.append({
                    'citation': citation_text,
                    'type': citation['type'],
                    'section': citation.get('section', 'Unknown'),
                    'suggestion': suggestion  # 添加建議
                })
            elif len(matching_refs) == 1:
                # 只找到一個 → 確定是這個 reference，不需要進一步比對
                pass
            else:
                # 找到多個（同一作者同一年有多篇）
                # 這時需要更精確的比對，使用原來的字串匹配邏輯
                found_exact_match = False
                
                def normalize_citation(text):
                    text = text.replace(', et al.', ' et al.')
                    text = text.replace(', et al,', ' et al,')
                    text = re.sub(r'et al\.?,?\s*', 'et al., ', text)
                    text = re.sub(r'\band\b', '&', text, flags=re.IGNORECASE)
                    text = re.sub(r',(\d)', r', \1', text)
                    return text
                
                normalized_citation = normalize_citation(citation_text)
                normalized_original = normalize_citation(original_text)
                
                for ref_id, ref_data in matching_refs:
                    parenthetical = normalize_citation(ref_data['parenthetical'])
                    narrative = normalize_citation(ref_data['narrative'])
                    
                    if parenthetical in normalized_citation or narrative in normalized_citation:
                        found_exact_match = True
                        break
                    
                    # 額外檢查：移除括號後比對
                    if ref_data['parenthetical'].startswith('(') and ref_data['parenthetical'].endswith(')'):
                        inner_citation = ref_data['parenthetical'][1:-1]
                        normalized_inner = normalize_citation(inner_citation)
                        if normalized_inner == normalized_original:
                            found_exact_match = True
                            break
                
                if not found_exact_match:
                    # 同一作者同一年有多篇，但無法精確匹配
                    missing_references.append({
                        'citation': citation_text,
                        'type': citation['type'],
                        'section': citation.get('section', 'Unknown')
                    })
        
        return missing_references

    def _exact_citation_match(self, citation_text: str, original_text: str, ref_data: Dict[str, Any]) -> bool:
        """精確匹配引用和參考文獻（用於無法提取作者年份的情況）"""
        def normalize_citation(text):
            text = text.replace(', et al.', ' et al.')
            text = text.replace(', et al,', ' et al,')
            text = re.sub(r'et al\.?,?\s*', 'et al., ', text)
            text = re.sub(r'\band\b', '&', text, flags=re.IGNORECASE)
            text = re.sub(r',(\d)', r', \1', text)
            text = text.lower().strip()
            return text
        
        normalized_citation = normalize_citation(citation_text)
        normalized_original = normalize_citation(original_text)
        parenthetical = normalize_citation(ref_data['parenthetical'])
        narrative = normalize_citation(ref_data['narrative'])
        
        # 檢查是否匹配
        if parenthetical in normalized_citation or narrative in normalized_citation:
            return True
        
        # 額外檢查：移除括號後比對
        if ref_data['parenthetical'].startswith('(') and ref_data['parenthetical'].endswith(')'):
            inner_citation = ref_data['parenthetical'][1:-1]
            normalized_inner = normalize_citation(inner_citation)
            if normalized_inner == normalized_original:
                return True
        
        return False


    def _mark_cited_references(self, citations: list, reference_dict: dict) -> list:
        """簡化版：使用第一作者 + 年份的模糊匹配來標記引用狀態"""
        
        # 重置所有引用狀態
        for ref in reference_dict.values():
            ref['cited'] = False
        
        # 對每個 reference，檢查其 citation key 是否出現在 citations 中
        for ref_id, ref_data in reference_dict.items():
            parenthetical = ref_data['parenthetical']
            narrative = ref_data['narrative']
            
            # 提取參考文獻的第一作者和年份
            ref_authors = ref_data['item'].get('authors', [])
            ref_year = ref_data['item'].get('year', '').strip()
            
            if not ref_authors or not ref_year:
                continue
            
            first_ref_author = ref_authors[0].split(",")[0].lower().strip()
            
            # 移除括號和標準化格式以便比對
            def normalize(text):
                text = text.replace('(', '').replace(')', '')
                text = ' '.join(text.split())  # 標準化空白
                text = text.lower()
                return text
            
            parenthetical_norm = normalize(parenthetical)
            narrative_norm = normalize(narrative)
            
            # 檢查是否有任何 citation 匹配
            for citation in citations:
                citation_norm = normalize(citation['text'])
                
                # 方法 1: 精確比對（忽略 & 和 and 的差異）
                def exact_matches(key_norm, cit_norm):
                    if key_norm == cit_norm:
                        return True
                    # 嘗試 & <-> and 轉換
                    key_with_and = key_norm.replace('&', 'and')
                    key_with_amp = key_norm.replace(' and ', ' & ')
                    if key_with_and == cit_norm or key_with_amp == cit_norm:
                        return True
                    return False
                
                # 方法 2: 模糊匹配（第一作者 + 年份）
                citation_info = self._extract_author_year_from_citation(citation['text'])
                citation_author = citation_info.get('author', '').lower().strip()
                citation_year = citation_info.get('year', '').strip()
                
                fuzzy_match = (citation_author == first_ref_author and citation_year == ref_year)
                
                if exact_matches(parenthetical_norm, citation_norm) or exact_matches(narrative_norm, citation_norm) or fuzzy_match:
                    ref_data['cited'] = True
                    break
        
        # 回傳狀態
        citation_status = []
        for ref in reference_dict.values():
            # 格式化作者顯示
            authors_display = ', '.join([a.split(',')[0] for a in ref['item'].get('authors', [])])
            
            citation_status.append({
                'reference': ref['item']['text'],
                'authors_display': authors_display,
                'year': ref['item'].get('year', ''),
                'parenthetical': ref['parenthetical'],
                'narrative': ref['narrative'],
                'cited': ref['cited']
            })
        return citation_status

    def _extract_author_year_from_citation(self, citation_text: str) -> Dict[str, str]:
        """改良版：更準確地從引用文字中提取作者和年份，支援各種格式變化"""
        # 移除多餘的空白
        clean_text = citation_text.strip()
        
        # 尋找年份
        year_match = re.search(r'(\d{4})', clean_text)
        year = year_match.group(1) if year_match else ""
        
        # 提取作者部分
        author = ""
        if year:
            # 對於括號內引用 (Author, 2024) 或 (Author et al., 2024)
            if clean_text.startswith('(') and clean_text.endswith(')'):
                inner = clean_text[1:-1]  # 移除括號
                # 找到年份前的部分
                year_pos = inner.find(year)
                if year_pos > 0:
                    author_part = inner[:year_pos].strip()
                else:
                    author_part = ""
            # 對於缺少左括號的引用 Author et al., 2024) 
            elif clean_text.endswith(')') and not clean_text.startswith('('):
                # 移除右括號
                inner = clean_text[:-1]
                # 找到年份前的部分
                year_pos = inner.find(year)
                if year_pos > 0:
                    author_part = inner[:year_pos].strip()
                else:
                    author_part = ""
            else:
                # 對於敘述型引用 Author (2024) 或 Author et al. (2024)
                paren_pos = clean_text.find('(')
                if paren_pos > 0:
                    author_part = clean_text[:paren_pos].strip()
                else:
                    # 最後的備用方案：年份前的所有內容
                    year_pos = clean_text.find(year)
                    if year_pos > 0:
                        author_part = clean_text[:year_pos].strip()
                    else:
                        author_part = ""
            
            # 清理作者部分並提取第一個作者
            if author_part:
                # 移除尾部的標點和連接詞
                author_part = author_part.rstrip(',;.& ')
                
                # 處理 "et al." 情況 - 移除 "et al."（包含有無逗號的情況）
                author_part = re.sub(r',?\s*et\s+al\.?$', '', author_part, flags=re.IGNORECASE).strip()
                
                # 處理多作者情況：取第一個作者（在 & 或 , 或 and 之前）
                # 先處理 & 和 and
                if '&' in author_part:
                    author_part = author_part.split('&')[0].strip()
                elif ' and ' in author_part.lower():
                    author_part = re.split(r'\s+and\s+', author_part, flags=re.IGNORECASE)[0].strip()
                
                # 如果還有逗號，可能是 "Last, First" 格式或多作者
                if ',' in author_part:
                    # 檢查是否是 "Last, F." 格式
                    parts = author_part.split(',')
                    if len(parts) >= 2 and re.match(r'^\s*[A-Z]\.?\s*$', parts[1]):
                        # 是 "Last, F." 格式，取第一部分
                        author_part = parts[0].strip()
                    else:
                        # 可能是多作者，取第一個
                        author_part = parts[0].strip()
                
                # 移除尾部的標點（再次清理）
                author_part = author_part.rstrip(',;.& ')
                
                # 提取第一個有效的作者姓氏（大寫字母開頭的單詞，支援連字號）
                author_match = re.search(r'^([A-Z][a-zA-Z\-\']+)', author_part.strip())
                if author_match:
                    author = author_match.group(1).rstrip('.,')
        
        return {'author': author, 'year': year}

    def _citation_matches_reference(self, citation_info: Dict[str, str], ref_data: Dict[str, Any]) -> bool:
        """改良版：與 generate_citation_key 邏輯一致的比對"""
        citation_author = citation_info.get('author', '').lower().strip()
        citation_year = citation_info.get('year', '').strip()
        
        ref_authors = ref_data['item'].get('authors', [])
        ref_year = ref_data['item'].get('year', '').strip()
        
        # 年份必須完全匹配
        if citation_year != ref_year:
            return False
        
        # 作者比對：使用與 generate_citation_key 相同的邏輯
        if citation_author and ref_authors:
            # 使用與 generate_citation_key 相同的方式提取第一作者姓氏
            first_ref_author = ref_authors[0].split(",")[0].lower().strip()
            
            # 比對第一作者的姓氏
            return citation_author == first_ref_author
        
        return False
