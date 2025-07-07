from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    # 僅本地開發測試時啟動 Flask 內建伺服器
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) 