import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from collections import Counter
import os

class TagCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("標籤統計器")
        self.root.geometry("800x600")
        # ... existing code ...
        # (完整複製 tagcount.py 內容，移除 if __name__ == "__main__" 區塊，並保留 main() 函數)

def main():
    root = tk.Tk()
    app = TagCounterApp(root)
    root.mainloop() 