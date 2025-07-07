import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import math
from datetime import datetime
import os

# 原有的計算邏輯

def calculate_hours(start_time, end_time):
    """計算時間差，以0.5小時為最小單位，跨日按天數計算"""
    if start_time is None or end_time is None:
        return None
    try:
        days_diff = (end_time.date() - start_time.date()).days
        if days_diff == 0:
            time_diff = end_time - start_time
            hours = time_diff.total_seconds() / 3600
            if hours < 0:
                hours = 0.0
        else:
            hours = days_diff * 6.0
        rounded_hours = math.ceil(hours * 2) / 2
        return rounded_hours
    except Exception as e:
        return None

class TimeBatchCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批次工時計算工具")
        self.root.geometry("800x600")
        self.df = None
        self.file_path = None
        self.start_col = None
        self.end_col = None
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        # 檔案選擇
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Button(file_frame, text="選擇 Excel/CSV 檔案", command=self.load_file).pack(side=tk.LEFT)
        self.file_label = ttk.Label(file_frame, text="尚未選擇檔案")
        self.file_label.pack(side=tk.LEFT, padx=10)
        # 欄位選擇
        col_frame = ttk.Frame(frame)
        col_frame.pack(fill=tk.X, pady=5)
        ttk.Label(col_frame, text="開始時間欄位:").pack(side=tk.LEFT)
        self.start_col_var = tk.StringVar()
        self.start_col_combo = ttk.Combobox(col_frame, textvariable=self.start_col_var, state="disabled")
        self.start_col_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(col_frame, text="結束時間欄位:").pack(side=tk.LEFT)
        self.end_col_var = tk.StringVar()
        self.end_col_combo = ttk.Combobox(col_frame, textvariable=self.end_col_var, state="disabled")
        self.end_col_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(col_frame, text="批次計算工時", command=self.batch_calculate).pack(side=tk.LEFT, padx=10)
        # 預覽區
        preview_frame = ttk.LabelFrame(frame, text="結果預覽", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree = ttk.Treeview(preview_frame, show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        # 匯出按鈕
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill=tk.X, pady=5)
        ttk.Button(export_frame, text="匯出結果", command=self.export_results).pack(side=tk.LEFT)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="選擇 Excel/CSV 檔案",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            columns = list(self.df.columns)
            self.start_col_combo['values'] = columns
            self.end_col_combo['values'] = columns
            self.start_col_combo.config(state="readonly")
            self.end_col_combo.config(state="readonly")
            self.start_col_var.set('')
            self.end_col_var.set('')
            self.preview_data(self.df)
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案失敗: {e}")
            self.df = None
            self.file_label.config(text="讀取失敗")

    def batch_calculate(self):
        if self.df is None:
            messagebox.showwarning("警告", "請先選擇檔案")
            return
        start_col = self.start_col_var.get()
        end_col = self.end_col_var.get()
        if not start_col or not end_col:
            messagebox.showwarning("警告", "請選擇開始與結束時間欄位")
            return
        result_df = self.df.copy()
        def parse_time(val):
            try:
                return pd.to_datetime(val)
            except Exception:
                return None
        result_df['計算工時'] = [
            calculate_hours(parse_time(row[start_col]), parse_time(row[end_col]))
            for _, row in result_df.iterrows()
        ]
        self.preview_data(result_df)
        self.df = result_df

    def preview_data(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        for _, row in df.head(100).iterrows():
            self.tree.insert('', 'end', values=[row[col] for col in df.columns])
        if len(df) > 100:
            self.tree.insert('', 'end', values=["...", "（僅顯示前100行）", *(["..."]*(len(df.columns)-2))])

    def export_results(self):
        if self.df is None:
            messagebox.showwarning("警告", "沒有可匯出的結果")
            return
        file_path = filedialog.asksaveasfilename(
            title="保存結果",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:
                    self.df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", f"結果已保存到：{file_path}")
            except Exception as e:
                messagebox.showerror("錯誤", f"保存失敗：{e}")

def main():
    root = tk.Tk()
    app = TimeBatchCalculatorApp(root)
    root.mainloop() 