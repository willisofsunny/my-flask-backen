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

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# 關鍵字計數
@app.route('/api/keyword_count', methods=['POST'])
def api_keyword_count():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            column_name = request.form.get('column_name')
            keywords = set(request.form.get('keywords', '').split(','))
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                result_df = keyword_count(tmp.name, column_name, keywords)
            return jsonify(result_df.to_dict(orient='records'))
        else:
            data = request.get_json()
            file_path = data.get('file_path')
            column_name = data.get('column_name')
            keywords = set(data.get('keywords', []))
            result_df = keyword_count(file_path, column_name, keywords)
            return jsonify(result_df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 相似公司名稱合併
@app.route('/api/keyword_similar_merge', methods=['POST'])
def api_keyword_similar_merge():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            threshold = float(request.form.get('threshold', 0.9))
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                result_df = keyword_similar_merge(tmp.name, threshold=threshold)
            return jsonify(result_df.to_dict(orient='records'))
        else:
            data = request.get_json()
            file_path = data.get('file_path')
            threshold = float(data.get('threshold', 0.9))
            result_df = keyword_similar_merge(file_path, threshold=threshold)
            return jsonify(result_df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 公司名稱提取與詞雲
@app.route('/api/keyword_extraction', methods=['POST'])
def api_keyword_extraction():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                df, img_path = keyword_extraction(tmp.name)
            return jsonify({'data': df.to_dict(orient='records'), 'wordcloud_img': img_path})
        else:
            data = request.get_json()
            file_path = data.get('file_path')
            df, img_path = keyword_extraction(file_path)
            return jsonify({'data': df.to_dict(orient='records'), 'wordcloud_img': img_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 公司詞雲與圓餅圖
@app.route('/api/workcloud', methods=['POST'])
def api_workcloud():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                wc_path, pie_path = workcloud(tmp.name)
            return jsonify({'wordcloud_img': wc_path, 'pie_img': pie_path})
        else:
            data = request.get_json()
            file_path = data.get('file_path')
            wc_path, pie_path = workcloud(file_path)
            return jsonify({'wordcloud_img': wc_path, 'pie_img': pie_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 表格智能匹配
@app.route('/api/table_matcher', methods=['POST'])
def api_table_matcher():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            main_file = request.files['main_file']
            tag_file = request.files['tag_file']
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(main_file.filename)[1]) as tmp_main, \
                 tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(tag_file.filename)[1]) as tmp_tag:
                main_file.save(tmp_main.name)
                tag_file.save(tmp_tag.name)
                result = table_matcher(tmp_main.name, tmp_tag.name)
            return jsonify(result)
        else:
            data = request.get_json()
            result = table_matcher(**data)
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 標籤統計
@app.route('/api/extract_tags', methods=['POST'])
def api_extract_tags():
    try:
        data = request.get_json()
        text = data.get('text', '')
        tags = extract_tags(text)
        return jsonify({'tags': tags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 批次工時計算
@app.route('/api/calculate_hours', methods=['POST'])
def api_calculate_hours():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                result = calculate_hours(tmp.name)
            return jsonify(result)
        else:
            data = request.get_json()
            result = calculate_hours(**data)
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 時間格式轉換
@app.route('/api/timeformattransfer', methods=['POST'])
def api_timeformattransfer():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                from timeformattransfer_module import timeformattransfer
                result = timeformattransfer(tmp.name)
            return jsonify(result)
        else:
            data = request.get_json()
            from timeformattransfer_module import timeformattransfer
            result = timeformattransfer(**data)
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 進階工時計算
@app.route('/api/advanced_time_calculator', methods=['POST'])
def api_advanced_time_calculator():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file = request.files['file']
            filename = file.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                from test_calculation_module import advanced_time_calculator
                result = advanced_time_calculator(tmp.name)
            return jsonify(result)
        else:
            data = request.get_json()
            from test_calculation_module import advanced_time_calculator
            result = advanced_time_calculator(**data)
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 表格模糊匹配
@app.route('/api/fuzzy_match', methods=['POST'])
def api_fuzzy_match():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file_a = request.files['file_a']
            file_b = request.files['file_b']
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_a.filename)[1]) as tmp_a, \
                 tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_b.filename)[1]) as tmp_b:
                file_a.save(tmp_a.name)
                file_b.save(tmp_b.name)
                from table_matcher_func import fuzzy_match
                result = fuzzy_match(tmp_a.name, tmp_b.name)
            return jsonify(result)
        else:
            data = request.get_json()
            from table_matcher_func import fuzzy_match
            result = fuzzy_match(**data)
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 其他功能依此模式擴充

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) 