import pandas as pd
import re
import os
from typing import Set, Optional

def normalize_keyword(kw: str) -> str:
    kw = kw.strip('[](){}、+')
    return kw.replace(" ", "").upper()

def keyword_count(file_path: str, column_name: str, keywords: Set[str], output_path: Optional[str]=None) -> pd.DataFrame:
    """
    file_path: Excel/CSV 檔案路徑，自動判斷格式
    column_name: 欲搜尋的欄位
    keywords: 關鍵字集合
    output_path: 結果CSV路徑（可選）
    return: 統計結果DataFrame
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.xls', '.xlsx'):
        df = pd.read_excel(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"不支援的檔案格式：{ext}")
    
    text_series = df[column_name].astype(str).str.upper().str.replace(" ", "")
    counts = {kw: text_series.str.contains(kw, regex=False).sum() for kw in keywords}
    result_df = pd.DataFrame({
        'Keyword': list(counts.keys()),
        'Count': list(counts.values())
    }).sort_values('Count', ascending=False)
    if output_path:
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    return result_df 