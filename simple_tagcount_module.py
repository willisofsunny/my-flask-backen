#!/usr/bin/env python3
"""
簡單的標籤統計腳本
使用方式: python simple_tagcount.py
"""

import pandas as pd
import re
from collections import Counter
import os

def extract_tags(text):
    if pd.isna(text) or not isinstance(text, str):
        return []
    pattern = r'\[([^\]]+)\]'
    tags = re.findall(pattern, text)
    return tags

def load_data(filename):
    try:
        if filename.endswith(('.xlsx', '.xls')):
            return pd.read_excel(filename)
        elif filename.endswith('.csv'):
            for encoding in ['utf-8', 'gbk', 'big5']:
                try:
                    return pd.read_csv(filename, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            raise Exception("無法讀取CSV文件，請檢查編碼格式")
        else:
            raise Exception("不支援的文件格式")
    except Exception as e:
        print(f"讀取文件失敗：{e}")
        return None

def main():
    print("=== 標籤統計工具 ===")
    filename = input("請輸入文件路徑 (或按Enter使用sample_data.csv): ").strip()
    if not filename:
        filename = "sample_data.csv"
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return
    print(f"正在加載文件: {filename}")
    df = load_data(filename)
    if df is None:
        return
    print(f"成功加載 {len(df)} 行數據")
    print(f"可用欄位: {list(df.columns)}")
    while True:
        column = input("請選擇要統計的欄位名稱: ").strip()
        if column in df.columns:
            break
        else:
            print(f"欄位 '{column}' 不存在，請重新選擇")
    print(f"正在統計欄位 '{column}' 中的標籤...")
    all_tags = []
    for text in df[column]:
        tags = extract_tags(text)
        all_tags.extend(tags)
    if not all_tags:
        print("沒有找到任何標籤")
        return
    tag_counts = Counter(all_tags)
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    print(f"\n=== 標籤統計結果 ===")
    print(f"共找到 {len(tag_counts)} 個不同的標籤")
    print(f"標籤總數: {sum(tag_counts.values())}")
    print("\n標籤排名:")
    print("-" * 40)
    print(f"{'標籤':<20} {'數量':<10}")
    print("-" * 40)
    for tag, count in sorted_tags:
        print(f"{tag:<20} {count:<10}")
    save = input("\n是否保存結果到文件? (y/n): ").strip().lower()
    if save in ['y', 'yes']:
        output_file = input("輸入輸出文件名 (預設: tag_results.csv): ").strip()
        if not output_file:
            output_file = "tag_results.csv"
        try:
            result_df = pd.DataFrame(sorted_tags, columns=['標籤', '數量'])
            if output_file.endswith('.xlsx'):
                result_df.to_excel(output_file, index=False)
            else:
                result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"結果已保存到: {output_file}")
        except Exception as e:
            print(f"保存失敗: {e}")

# 保留 main() 作為入口，不自動執行 