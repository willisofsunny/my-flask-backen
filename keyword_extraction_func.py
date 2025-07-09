import os
import re
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import Optional, Tuple

EXCLUSION_LIST = [
    "Apollo","FD","正式區","PT","PY","全模組","SSO","VN","越南新專區導入",
    "正式專區","Pilot","Linkup","表單","XE","Pilot/正式區","MAYO777","Facepass",
    "正式/pilot區","PILOT","客戶Pilot區+正式區","API","CN","APP","導入後台",
    "專區","導入精靈","ＸＥ","AAD憑證","Apollo 集團版","PT","STAYFUN","Apollo XE版",
    "Lasso","Apollo XE","AUTH","facepass","APollo","Auth","py","Apollo[PT","APOLLO",
    "Apollo CN","ISSUE","Asia","Issue","[FD","Apollo Pilot","LOGO","通訊資料",
    "Link up","PT PY資料拋出","新專區導入"
]
EXCLUSIONS = set(item.lower().strip() for item in EXCLUSION_LIST)

# 可選中文字體
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansCJKtc-Regular.otf')

def extract_company(subject):
    segments = re.findall(r'\[([^\]]+)\]', subject)
    filtered = [s for s in (seg.strip() for seg in segments) if s.lower() not in EXCLUSIONS]
    if len(filtered) >= 2:
        return filtered[-2]
    elif len(filtered) == 1:
        return filtered[0]
    else:
        return None

def keyword_extraction(file_path: str, output_dir: Optional[str]=None, font_path: Optional[str]=None) -> Tuple[pd.DataFrame, str]:
    """
    file_path: Excel/CSV 檔案路徑，自動判斷格式
    output_dir: 輸出目錄
    font_path: 詞雲字型路徑
    return: (公司統計DataFrame, 詞雲圖片路徑)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError('檔案不存在')
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.xls', '.xlsx'):
        df = pd.read_excel(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"不支援的檔案格式：{ext}")
    # 優化：自動偵測主旨欄位
    possible_cols = ['主旨', 'subject', '主題', 'title']
    col = next((c for c in possible_cols if c in df.columns), None)
    if not col:
        raise ValueError(f"找不到主旨欄位，請確認欄位名稱（支援：{', '.join(possible_cols)}）")
    df['company'] = df[col].astype(str).apply(extract_company)
    counts = Counter(df['company'].dropna())
    if not output_dir:
        output_dir = os.path.dirname(file_path)
    csv_path = os.path.join(output_dir, 'company_counts.csv')
    pd.DataFrame(counts.items(), columns=['company', 'count']).to_csv(csv_path, index=False, encoding='utf-8-sig')
    # 詞雲
    if not font_path:
        font_path = FONT_PATH
    try:
        wc = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate_from_frequencies(counts)
    except Exception as e:
        # fallback: 沒有字型就用預設英文字型
        wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(counts)
    img_path = os.path.join(output_dir, 'company_wordcloud.png')
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()
    return pd.DataFrame(counts.items(), columns=['company', 'count']), img_path 