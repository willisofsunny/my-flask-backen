from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import pandas as pd
import re
from keyword_count_func import keyword_count, normalize_keyword
from keyword_similar_func import keyword_similar_merge
from keyword_extraction_func import keyword_extraction
from workcloud_func import workcloud
from table_matcher_func import table_matcher
from simple_tagcount_module import extract_tags
from test_calculation_module import calculate_hours
# 其他模組依需求引入

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# 關鍵字計數
@app.route('/api/keyword_count', methods=['POST'])
def api_keyword_count():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # 支援未來檔案上傳擴充
        return jsonify({'error': '目前僅支援 JSON 輸入'}), 400
    data = request.get_json()
    text = data.get('text', '')
    keywords = data.get('keywords', [])
    result = keyword_count(text, keywords)
    return jsonify(result)

# 相似公司名稱合併
@app.route('/api/keyword_similar_merge', methods=['POST'])
def api_keyword_similar_merge():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files['file']
        threshold = float(request.form.get('threshold', 0.9))
        filename = file.filename
        df = pd.read_excel(file) if filename.endswith(('xlsx','xls')) else pd.read_csv(file)
        # 假設 keyword_similar_merge 支援 DataFrame 輸入
        result = keyword_similar_merge(df, threshold=threshold)
        return jsonify(result)
    else:
        data = request.get_json()
        result = keyword_similar_merge(**data)
        return jsonify(result)

# 公司名稱提取與詞雲
@app.route('/api/keyword_extraction', methods=['POST'])
def api_keyword_extraction():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files['file']
        filename = file.filename
        df = pd.read_excel(file) if filename.endswith(('xlsx','xls')) else pd.read_csv(file)
        # 假設 keyword_extraction 支援 DataFrame 輸入
        result = keyword_extraction(df)
        return jsonify(result)
    else:
        data = request.get_json()
        result = keyword_extraction(**data)
        return jsonify(result)

# 公司詞雲與圓餅圖
@app.route('/api/workcloud', methods=['POST'])
def api_workcloud():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files['file']
        filename = file.filename
        df = pd.read_excel(file) if filename.endswith(('xlsx','xls')) else pd.read_csv(file)
        result = workcloud(df)
        return jsonify(result)
    else:
        data = request.get_json()
        result = workcloud(**data)
        return jsonify(result)

# 表格智能匹配
@app.route('/api/table_matcher', methods=['POST'])
def api_table_matcher():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        main_file = request.files['main_file']
        tag_file = request.files['tag_file']
        main_df = pd.read_excel(main_file) if main_file.filename.endswith(('xlsx','xls')) else pd.read_csv(main_file)
        tag_df = pd.read_excel(tag_file) if tag_file.filename.endswith(('xlsx','xls')) else pd.read_csv(tag_file)
        result = table_matcher(main_df, tag_df)
        return jsonify(result)
    else:
        data = request.get_json()
        result = table_matcher(**data)
        return jsonify(result)

# 標籤統計
@app.route('/api/extract_tags', methods=['POST'])
def api_extract_tags():
    data = request.get_json()
    text = data.get('text', '')
    tags = extract_tags(text)
    return jsonify({'tags': tags})

# 批次工時計算
@app.route('/api/calculate_hours', methods=['POST'])
def api_calculate_hours():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files['file']
        filename = file.filename
        df = pd.read_excel(file) if filename.endswith(('xlsx','xls')) else pd.read_csv(file)
        result = calculate_hours(df)
        return jsonify(result)
    else:
        data = request.get_json()
        result = calculate_hours(**data)
        return jsonify(result)

# 時間格式轉換
@app.route('/api/timeformattransfer', methods=['POST'])
def api_timeformattransfer():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files['file']
        filename = file.filename
        df = pd.read_excel(file) if filename.endswith(('xlsx','xls')) else pd.read_csv(file)
        # 假設 timeformattransfer_module 有 timeformattransfer 函數
        from timeformattransfer_module import timeformattransfer
        result = timeformattransfer(df)
        return jsonify(result)
    else:
        data = request.get_json()
        from timeformattransfer_module import timeformattransfer
        result = timeformattransfer(**data)
        return jsonify(result)

# 進階工時計算
@app.route('/api/advanced_time_calculator', methods=['POST'])
def api_advanced_time_calculator():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files['file']
        filename = file.filename
        df = pd.read_excel(file) if filename.endswith(('xlsx','xls')) else pd.read_csv(file)
        # 假設 test_calculation_module 有 advanced_time_calculator 函數
        from test_calculation_module import advanced_time_calculator
        result = advanced_time_calculator(df)
        return jsonify(result)
    else:
        data = request.get_json()
        from test_calculation_module import advanced_time_calculator
        result = advanced_time_calculator(**data)
        return jsonify(result)

# 表格模糊匹配
@app.route('/api/fuzzy_match', methods=['POST'])
def api_fuzzy_match():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file_a = request.files['file_a']
        file_b = request.files['file_b']
        df_a = pd.read_excel(file_a) if file_a.filename.endswith(('xlsx','xls')) else pd.read_csv(file_a)
        df_b = pd.read_excel(file_b) if file_b.filename.endswith(('xlsx','xls')) else pd.read_csv(file_b)
        # 假設 table_matcher_func 有 fuzzy_match 函數
        from table_matcher_func import fuzzy_match
        result = fuzzy_match(df_a, df_b)
        return jsonify(result)
    else:
        data = request.get_json()
        from table_matcher_func import fuzzy_match
        result = fuzzy_match(**data)
        return jsonify(result)

# 其他功能依此模式擴充

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) 