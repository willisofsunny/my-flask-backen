import pandas as pd
import re
from difflib import SequenceMatcher
from collections import Counter
from typing import List, Dict, Optional, Tuple
import os

def normalize_text(text: str) -> str:
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    return text

def advanced_similarity(text1: str, text2: str) -> float:
    norm_text1 = normalize_text(text1)
    norm_text2 = normalize_text(text2)
    if not norm_text1 or not norm_text2:
        return 0.0
    seq_ratio = SequenceMatcher(None, norm_text1, norm_text2).ratio()
    return seq_ratio

def is_fuzzy_match(text1: str, text2: str, threshold: float) -> Tuple[bool, float]:
    similarity = advanced_similarity(text1, text2)
    return similarity >= threshold, similarity

def load_df_auto(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.xls', '.xlsx'):
        return pd.read_excel(file_path)
    elif ext == '.csv':
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"不支援的檔案格式：{ext}")

def table_matcher(
    main_df: pd.DataFrame,
    tag_df: pd.DataFrame,
    main_field1: str,
    main_field2: str,
    tag_field1: str,
    tag_field2: str,
    tag_name_field: str,
    tag_value_field: str,
    similarity_threshold: float = 0.8,
    max_matches: int = 5,
    min_similarity: float = 0.3
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    result_df = main_df.copy()
    result_df['匹配標籤總數值'] = 0
    result_df['匹配的標籤'] = ''
    result_df['匹配相似度'] = ''
    result_df['匹配詳情'] = ''
    matched_tags = set()
    for idx, main_row in result_df.iterrows():
        main_val1 = str(main_row[main_field1]).strip()
        main_val2 = str(main_row[main_field2]).strip()
        matching_records = []
        for tag_idx, tag_row in tag_df.iterrows():
            if tag_idx in matched_tags:
                continue
            tag_val1 = str(tag_row[tag_field1]).strip()
            tag_val2 = str(tag_row[tag_field2]).strip()
            best_similarity = 0.0
            best_combo = ""
            match_results = []
            combinations = [
                (main_val1, tag_val1, f"{main_field1}↔{tag_field1}"),
                (main_val1, tag_val2, f"{main_field1}↔{tag_field2}"),
                (main_val2, tag_val1, f"{main_field2}↔{tag_field1}"),
                (main_val2, tag_val2, f"{main_field2}↔{tag_field2}")
            ]
            for main_val, tag_val, combo_desc in combinations:
                if main_val and tag_val:
                    is_match, similarity = is_fuzzy_match(main_val, tag_val, similarity_threshold)
                    if is_match:
                        match_results.append((combo_desc, similarity))
            if match_results:
                best_match = max(match_results, key=lambda x: x[1])
                best_combo = best_match[0]
                best_similarity = best_match[1]
                if best_similarity >= min_similarity:
                    matching_records.append({
                        'index': tag_idx,
                        'row': tag_row,
                        'similarity': best_similarity,
                        'combination': best_combo
                    })
        if matching_records:
            matching_records.sort(key=lambda x: x['similarity'], reverse=True)
            limited_records = matching_records[:max_matches]
            newly_matched_tags = [record['index'] for record in limited_records]
            matched_tags.update(newly_matched_tags)
            total_value = sum(record['row'][tag_value_field] for record in limited_records)
            result_df.at[idx, '匹配標籤總數值'] = total_value
            tag_names = [str(record['row'][tag_name_field]) for record in limited_records]
            similarities = [f"{record['similarity']:.2f}" for record in limited_records]
            combinations = [record['combination'] for record in limited_records if record['combination']]
            result_df.at[idx, '匹配的標籤'] = ', '.join(tag_names)
            result_df.at[idx, '匹配相似度'] = ', '.join(similarities)
            result_df.at[idx, '匹配詳情'] = ', '.join(combinations[:3])
    unmatched_df = tag_df.drop(index=list(matched_tags)).copy()
    return result_df, unmatched_df 