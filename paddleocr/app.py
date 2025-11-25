from flask import Flask, request, jsonify
import os
import tempfile
import urllib.request
import cv2
import numpy as np

app = Flask(__name__)

# 延迟初始化PaddleOCR以避免启动时的依赖问题
ocr = None

def get_ocr():
    """延迟初始化PaddleOCR"""
    global ocr
    if ocr is None:
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
        except Exception as e:
            raise Exception(f"PaddleOCR初始化失败: {str(e)}")
    return ocr

@app.route('/ocr', methods=['GET', 'POST'])
def ocr_service():
    """
    OCR服务主接口
    GET: 通过URL参数获取图片并识别
    POST: 通过上传文件识别
    """
    try:
        if request.method == 'GET':
            # 通过URL获取图片
            image_url = request.args.get('url')
            if not image_url:
                return jsonify({'error': '请提供图片URL参数'}), 400
            
            # 下载图片
            temp_file, temp_path = tempfile.mkstemp(suffix='.jpg')
            try:
                urllib.request.urlretrieve(image_url, temp_path)
                image = cv2.imread(temp_path)
            finally:
                os.close(temp_file)
                os.unlink(temp_path)
                
        elif request.method == 'POST':
            # 通过文件上传获取图片
            if 'file' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '没有选择文件'}), 400
                
            # 读取上传的图片
            img_bytes = file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # OCR处理
        ocr_instance = get_ocr()
        result = ocr_instance.ocr(image, cls=True)
        
        # 处理结果
        ocr_results = []
        for idx, line in enumerate(result):
            for box in line:
                position = box[0]
                text = box[1][0]
                confidence = float(box[1][1])
                ocr_results.append({
                    'text': text,
                    'confidence': confidence,
                    'position': position
                })
        
        return jsonify({
            'status': 'success',
            'results': ocr_results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ocr/local', methods=['GET'])
def ocr_local_file():
    """通过本地文件路径进行OCR识别"""
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'error': '请提供本地图片路径参数'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'文件不存在: {file_path}'}), 404
            
        # OCR处理
        ocr_instance = get_ocr()
        result = ocr_instance.ocr(file_path, cls=True)
        
        # 处理结果
        ocr_results = []
        for idx, line in enumerate(result):
            for box in line:
                position = box[0]
                text = box[1][0]
                confidence = float(box[1][1])
                ocr_results.append({
                    'text': text,
                    'confidence': confidence,
                    'position': position
                })
        
        return jsonify({
            'status': 'success',
            'results': ocr_results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """服务状态检查"""
    return jsonify({
        'status': 'running',
        'service': 'PaddleOCR API'
    })

if __name__ == '__main__':
    print("PaddleOCR服务启动中...")
    print("访问 http://localhost:5000/status 检查服务状态")
    app.run(host='0.0.0.0', port=5000, debug=True)