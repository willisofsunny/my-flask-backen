import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from fuzzywuzzy import fuzz, process
import os

class FuzzyMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("表格模糊匹配工具")
        self.root.geometry("800x600")
        # ... existing code ...
        # (完整複製 comparefit.py 內容，移除 if __name__ == "__main__" 區塊，並保留 main() 函數)

def main():
    root = tk.Tk()
    app = FuzzyMatchApp(root)
    root.mainloop() 