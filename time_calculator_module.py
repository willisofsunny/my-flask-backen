import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from datetime import datetime, time
import os
import pytz

class TimeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("時間計算器")
        self.root.geometry("600x500")
        # ... existing code ...
        # (完整複製 time_calculator.py 內容，移除 if __name__ == "__main__" 區塊，並保留 main() 函數)

def main():
    root = tk.Tk()
    app = TimeCalculator(root)
    root.mainloop() 