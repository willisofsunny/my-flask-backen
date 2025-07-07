import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib.font_manager as fm
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, Image as PILImage
from typing import Optional, Tuple
import time, random

def create_cloud_mask(w, h):
    img = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = w//2, h//2
    r = min(w, h) // 4
    for dx in (-r, 0, r):
        draw.ellipse([cx+dx-r, cy-r, cx+dx+r, cy+r], fill=255)
    r2 = int(r * 0.7)
    for dx, dy in [(-int(r*0.6), -int(r*0.8)), (int(r*0.6), -int(r*0.8))]:
        draw.ellipse([cx+dx-r2, cy+dy-r2, cx+dx+r2, cy+dy+r2], fill=255)
    mask = img.filter(ImageFilter.GaussianBlur(radius=r * 0.2))
    arr = np.array(mask)
    return arr > 128

VIVID_COLORS = [
    '#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC'
]
def vivid_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    if font_size >= 150:
        return random.choice(VIVID_COLORS[:3])
    elif font_size >= 100:
        return random.choice(VIVID_COLORS[3:6])
    elif font_size >= 50:
        return random.choice(VIVID_COLORS[6:8])
    else:
        return random.choice(VIVID_COLORS[8:])

def create_background(w, h):
    y, x = np.indices((h, w))
    dx = x - w/2; dy = y - h/2
    dist = np.sqrt(dx*dx + dy*dy)
    maxd = np.sqrt((w/2)**2 + (h/2)**2)
    grad = 1 - dist/maxd
    r = (250 + grad * 5).clip(0,255).astype(np.uint8)
    g = (250 + grad * 5).clip(0,255).astype(np.uint8)
    b = (255 - grad * 10).clip(0,255).astype(np.uint8)
    a = np.full((h, w), 255, dtype=np.uint8)
    return np.dstack([r, g, b, a])

font_list = [
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    'C:\\Windows\\Fonts\\msjh.ttc'
]
def get_font_path():
    for f in font_list:
        if os.path.exists(f):
            return f
    return fm.findfont(fm.FontProperties(family=['Arial Unicode MS']))

def workcloud(file_path: str, out_dir: Optional[str]=None) -> Tuple[str, str]:
    """
    file_path: Excel/CSV 檔案路徑，自動判斷格式
    out_dir: 輸出目錄
    return: (詞雲圖片路徑, 圓餅圖圖片路徑)
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.xls', '.xlsx'):
        df = pd.read_excel(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"不支援的檔案格式：{ext}")
    df.columns = df.columns.str.lower()
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0)
    df = df.groupby('company', as_index=False)['count'].sum()
    if not out_dir:
        out_dir = os.path.join(os.path.dirname(file_path), f'output_{time.strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(out_dir, exist_ok=True)
    mask = create_cloud_mask(1200, 800)
    bg = create_background(1200, 800)
    font_path = get_font_path()
    wc = WordCloud(
        font_path=font_path,
        width=1200, height=800,
        background_color=None, mode='RGBA',
        mask=mask,
        contour_width=0,
        min_font_size=12, max_font_size=180,
        color_func=vivid_color_func,
        prefer_horizontal=0.8,
        relative_scaling=0.5
    )
    word_cloud = wc.generate_from_frequencies(dict(zip(df['company'], df['count'])))
    word_cloud_image = word_cloud.to_image()
    background = PILImage.fromarray(bg)
    result = PILImage.alpha_composite(background.convert('RGBA'), word_cloud_image)
    wc_path = os.path.join(out_dir, 'wordcloud.png')
    result.save(wc_path, format='PNG')
    # Pie chart
    top10 = df.nlargest(10, 'count')
    others = df.iloc[10:]['count'].sum()
    pie_df = pd.concat([top10, pd.DataFrame([{'company':'其他','count':others}])], ignore_index=True)
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS','sans-serif']
    fig, (ax0, ax1) = plt.subplots(1,2, figsize=(14,7), dpi=120, gridspec_kw={'width_ratios':[2,1]})
    colors = plt.cm.tab20(range(len(pie_df)))
    ax0.pie(pie_df['count'], labels=pie_df['company'], autopct='%1.1f%%', startangle=135, colors=colors)
    ax0.set_title('公司數量分布')
    ax1.axis('off')
    tbl = ax1.table(cellText=pie_df.values, colLabels=pie_df.columns, loc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for cell in tbl._cells.values(): cell.set_text_props(ha='center', va='center')
    ax1.set_title('公司明細')
    pie_path = os.path.join(out_dir, 'company_pie.png')
    plt.tight_layout(); fig.savefig(pie_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return wc_path, pie_path 