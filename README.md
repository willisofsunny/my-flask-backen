# 數據處理工具箱 Data Toolbox

本工具集成常用數據處理腳本，無需安裝Python環境，直接在網頁上操作。

## 目前功能
- **關鍵字計數**：統計指定欄位中多個關鍵字的出現次數。
- **相似公司名稱合併**：自動合併相似公司名稱並加總數量。

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 啟動方式

```bash
streamlit run app.py
```

啟動後，瀏覽器會自動打開本地網頁（預設 http://localhost:8501 ）。

## 使用說明
1. 在左側選擇要使用的工具。
2. 按照頁面指示，上傳檔案、設置參數。
3. 點擊「執行」按鈕，稍候即可在下方看到結果，並可下載CSV。

## 常見問題
- 若遇到無法上傳大檔案，請調整 Streamlit 設定（`~/.streamlit/config.toml`）。
- 若遇到 Excel 讀取錯誤，請確認檔案格式正確。

---
如需擴充更多數據處理腳本，請聯絡維護者。

# trigger redeploy 