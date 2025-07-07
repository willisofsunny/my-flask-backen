from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/table_matcher', methods=['POST'])
def table_matcher():
    main_file = request.files.get('main_file')
    tag_file = request.files.get('tag_file')
    if not main_file or not tag_file:
        return jsonify({'error': '缺少檔案'}), 400
    try:
        main_df = pd.read_excel(main_file)
        tag_df = pd.read_excel(tag_file)
        result = {
            'msg': '比對成功',
            'main_rows': len(main_df),
            'tag_rows': len(tag_df)
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # 僅本地開發測試時啟動 Flask 內建伺服器
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) 