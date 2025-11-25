# PaddleOCR 服务使用指南

本目录包含小说阅读助手的 OCR（光学字符识别）服务，用于识别图片中的文字内容。

## 📋 目录结构

```
paddleocr/
├── app.py                  # OCR 服务主程序
├── requirements.txt        # OCR 相关依赖
├── start_service.bat       # Windows 启动脚本
├── start_service.sh        # Linux/Mac 启动脚本
├── test_service.py         # 服务测试脚本
├── README.md              # 项目说明
└── USAGE.md               # 本使用指南
```

## 🚀 快速开始

### 1. 安装依赖

在项目根目录运行完整安装模式：

```bash
# Windows PowerShell
python install.py --full

# Linux/Mac
python3 install.py --full
```

或者在 paddleocr 目录下单独安装：

```bash
cd paddleocr
pip install -r requirements.txt
```

### 2. 启动 OCR 服务

**Windows 用户：**
```bash
# 方法1：直接运行批处理文件
start_service.bat

# 方法2：使用 Python
python app.py
```

**Linux/Mac 用户：**
```bash
# 方法1：使用启动脚本
chmod +x start_service.sh
./start_service.sh

# 方法2：使用 Python
python3 app.py
```

服务启动后会在 `http://localhost:5000` 上运行。

### 3. 测试服务

在另一个终端窗口运行测试脚本：

```bash
python test_service.py
```

## 📡 API 接口

### 1. 服务状态检查

**端点：** `GET /status`

**示例：**
```bash
curl http://localhost:5000/status
```

**响应：**
```json
{
  "status": "running",
  "service": "PaddleOCR API"
}
```

### 2. 本地文件 OCR 识别

**端点：** `GET /ocr/local`

**参数：**
- `path`: 本地图片文件的绝对路径

**示例：**
```bash
curl "http://localhost:5000/ocr/local?path=E:/test/image.png"
```

**响应：**
```json
{
  "status": "success",
  "results": [
    {
      "text": "识别到的文字",
      "confidence": 0.95,
      "position": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
}
```

### 3. 上传文件 OCR 识别

**端点：** `POST /ocr`

**参数：**
- `file`: 上传的图片文件

**Python 示例：**
```python
import requests

url = "http://localhost:5000/ocr"
files = {'file': open('test.png', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### 4. URL 图片 OCR 识别

**端点：** `GET /ocr`

**参数：**
- `url`: 图片的 URL 地址

**示例：**
```bash
curl "http://localhost:5000/ocr?url=https://example.com/image.png"
```

## 🔧 配置说明

### 端口配置

默认端口为 `5000`。如需修改，请编辑 `app.py` 文件最后一行：

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### OCR 引擎配置

在 `app.py` 的 `get_ocr()` 函数中可以修改 PaddleOCR 的配置：

```python
ocr = PaddleOCR(
    use_angle_cls=True,  # 是否使用角度分类
    lang='ch',           # 语言：'ch'中文, 'en'英文
    use_gpu=False        # 是否使用 GPU
)
```

## 🐛 常见问题

### 1. 服务无法启动

**问题：** 提示端口已被占用

**解决：** 
- 检查是否已有 OCR 服务在运行
- 修改 `app.py` 中的端口号
- 或者关闭占用 5000 端口的其他程序

### 2. 依赖安装失败

**问题：** PaddlePaddle 或 PaddleOCR 安装失败

**解决：**
```bash
# 清华镜像源安装
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. OCR 识别速度慢

**问题：** 图片识别耗时较长

**解决：**
- 如果有 NVIDIA GPU，安装 GPU 版本的 PaddlePaddle
- 减小输入图片的尺寸
- 在 `app.py` 中设置 `use_gpu=True`（需要 GPU 支持）

### 4. 识别准确率低

**问题：** 文字识别不准确

**解决：**
- 确保图片清晰度足够
- 图片中文字大小适中
- 避免图片倾斜或变形
- 可以尝试预处理图片（增强对比度等）

## 📝 开发说明

### 添加新的 API 端点

在 `app.py` 中添加新的路由：

```python
@app.route('/your_endpoint', methods=['GET', 'POST'])
def your_function():
    # 你的处理逻辑
    return jsonify({'status': 'success'})
```

### 集成到其他项目

在其他 Python 项目中使用此 OCR 服务：

```python
import requests

def ocr_image(image_path):
    """调用 OCR 服务识别图片"""
    url = "http://localhost:5000/ocr/local"
    params = {"path": image_path}
    response = requests.get(url, params=params)
    return response.json()

# 使用
result = ocr_image("path/to/your/image.png")
print(result)
```

## 📞 技术支持

如遇到问题，请：
1. 检查本文档的常见问题部分
2. 运行 `test_service.py` 进行诊断
3. 查看终端中的错误日志
4. 参考 PaddleOCR 官方文档：https://github.com/PaddlePaddle/PaddleOCR

## 🔄 更新日志

### v1.0.0 (2024-12-25)
- ✨ 初始版本发布
- 🚀 支持本地文件、URL 和上传文件三种识别方式
- 📝 提供完整的 API 文档
- 🧪 包含测试脚本