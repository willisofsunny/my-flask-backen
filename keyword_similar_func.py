import pandas as pd
import re
from collections import OrderedDict
from difflib import SequenceMatcher
from typing import Optional
import os

def clean_company(raw: str) -> str:
    company = raw.split("_", 1)[0]
    company = re.sub(r"\s+", "", company)
    return company

def is_similar(a: str, b: str, threshold: float = 0.9) -> bool:
    if a == b:
        return True
    if a.startswith(b) or b.startswith(a):
        return True
    return SequenceMatcher(None, a, b).ratio() >= threshold

def merge_companies(df: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
    merged = OrderedDict()
    for raw_name, cnt in zip(df["company"], df["count"]):
        name = clean_company(str(raw_name))
        placed = False
        for canon in list(merged.keys()):
            if is_similar(name, canon, threshold):
                new_canon = canon if len(canon) <= len(name) else name
                if new_canon != canon:
                    merged[new_canon] = merged.pop(canon)
                merged[new_canon] += int(cnt)
                placed = True
                break
        if not placed:
            merged[name] = int(cnt)
    return pd.DataFrame({"company": list(merged.keys()), "count": list(merged.values())})

def keyword_similar_merge(file_path: str, output_path: Optional[str]=None, threshold: float=0.9) -> pd.DataFrame:
    """
    file_path: Excel/CSV 檔案路徑，自動判斷格式
    output_path: 結果CSV路徑（可選）
    threshold: 相似度閾值
    return: 合併結果DataFrame
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.xls', '.xlsx'):
        df = pd.read_excel(file_path, usecols=["company", "count"])
    elif ext == '.csv':
        df = pd.read_csv(file_path, usecols=["company", "count"])
    else:
        raise ValueError(f"不支援的檔案格式：{ext}")
    result = merge_companies(df, threshold)
    if output_path:
        result.to_csv(output_path, index=False, encoding="utf-8-sig")
    return result 