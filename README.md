# 小说阅读神器 - Novel Reader Helper

## 简介

小说阅读神器是一款功能强大的在线小说阅读辅助工具，集成了智能浏览器、内容提取、OCR识别和AI总结等多项功能。帮助您更高效地阅读和理解网络小说内容。

该项目使用文心快码Comate辅助编程实现（其实大部分脏活累活都是Comate干的，我就是帮着把把关，指指点点，外加人工测试）

## 核心功能

### 1. 智能浏览器
- **多站点支持**：内置起点中文网、纵横中文网、17K小说网等主流小说网站快捷链接
- **完整浏览功能**：支持前进、后退、刷新、停止等标准浏览器操作
- **快捷导航**：工具栏一键访问常用小说网站
- **本地文件支持**：可打开本地HTML/MHTML格式的小说文件

### 2. 智能内容提取
- **一键提取**：自动识别并提取小说章节的标题和正文内容
- **多格式支持**：支持起点、纵横等主流小说网站的内容提取
- **精准识别**：智能过滤广告和无关内容，只保留正文
- **MHTML支持**：可以从保存的MHTML文件中提取内容

### 3. 图片文字识别（OCR）
- **批量识别**：自动下载页面中的图片并进行OCR识别
- **高精度识别**：集成PaddleOCR引擎，支持中文识别
- **图文结合**：将识别出的文字与网页文本内容合并展示

### 4. AI智能总结
- **快速预览**：自动生成章节内容摘要，快速了解故事梗概
- **内容分析**：统计文章长度、段落数量，分析内容特征
- **结果保存**：支持将总结结果复制到剪贴板或保存为文本文件
- **多格式展示**：清晰的格式化输出，包含开头和结尾预览

## 系统要求

- **操作系统**：Windows 10/11, macOS, Linux
- **Python版本**：Python 3.8 或更高版本
- **浏览器内核**：PyQt5 WebEngine (Chromium内核)

## 快速开始
先下载源代码

```bash
git clone https://gitcode.com/skywalk163/novel_reader_helper
cd novel_reader_helper
```

​
### 1. 安装依赖

您可以选择快速安装（不包含OCR功能）或完整安装：

```bash
# 快速安装 - 不包含OCR功能
python install.py --quick

# 完整安装 - 包含OCR功能
python install.py --full
```
python install.py --quick 可以简化为python install.py 

主要依赖包括：
- PyQt5 >= 5.15.0
- PyQtWebEngine >= 5.15.0
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- paddleocr >= 2.6.0 (仅完整安装时安装，用于OCR功能)

### 2. 启动浏览器

```bash
python browser.py
```

或使用启动脚本：

```bash
python start.py
```

### 3. 使用步骤

#### 浏览小说网站
1. 点击工具栏上的网站快捷按钮（起点、纵横等）
2. 或在地址栏输入网址，按回车键访问

#### 提取小说内容
1. 在浏览器中打开小说章节页面
2. 等待页面完全加载
3. 点击工具栏的"📄 提取内容"按钮
4. 系统会自动识别并提取章节标题和正文

#### AI总结功能
1. 先使用"📄 提取内容"功能提取小说内容
2. 点击工具栏的"📝 AI总结"按钮
3. 查看自动生成的内容摘要
4. 可以复制总结或保存到文件

#### OCR识别（可选）
1. 在包含图片的小说页面
2. 点击"🖼️ 识别图片"按钮
3. 系统会自动下载图片并识别文字
4. 识别结果会与提取的文本内容合并显示

## 项目结构

```
novel_reader_helper/
├── browser.py              # 主浏览器程序
├── web_extractor.py        # 网页内容提取器
├── mhtml_extractor.py      # MHTML文件解析器
├── config.py               # 配置文件
├── start.py                # 启动脚本
├── requirements.txt        # 依赖列表
├── README.md              # 项目说明
├── INSTALL_GUIDE.md       # 安装指南
├── USAGE.md               # 使用手册
└── test/                  # 测试文件目录
    ├── test_browser_extract.py
    ├── test_qidian_extract.py
    └── ...
```

## 配置说明

### OCR服务配置（可选）

OCR服务使用的是后台独立的PaddleOCR服务。如果需要使用OCR识别功能：

1. 确保您已执行完整安装（`python install.py --full`）
2. 打开新的终端窗口，启动OCR服务：

```bash
cd paddleocrapp
python app.py  # Windows系统
# 或
python3 app.py  # Linux/macOS系统
```

3. 保持OCR服务终端窗口运行（不要关闭）
4. OCR服务默认运行在 `http://127.0.0.1:5000`
5. 主程序将自动连接到此服务以进行图片识别

**提示**：如果您不需要OCR功能，可以跳过此步骤，直接使用快速安装选项，节省安装时间和磁盘空间。

## 注意事项

1. **网络连接**：首次运行需要网络连接以加载网页内容
2. **处理时间**：大图片OCR识别可能需要较长时间，请耐心等待
3. **网站兼容性**：不同网站的页面结构可能导致提取效果不同
4. **反爬机制**：部分网站可能有反爬虫措施，请合理使用
5. **权限要求**：确保程序有访问网络和文件系统的权限

## 常见问题

### Q1: 浏览器无法启动？
**A**: 请检查是否正确安装了PyQt5和PyQtWebEngine：
```bash
pip install PyQt5 PyQtWebEngine
```

### Q2: 内容提取失败？
**A**: 可能的原因：
- 页面未完全加载，请等待几秒后再试
- 网站结构发生变化，提取规则需要更新
- 网络连接问题，请检查网络状态

### Q3: OCR识别不可用？
**A**: OCR功能是可选的，需要：
1. 确保您选择了完整安装：`python install.py --full`
2. 在单独的终端窗口启动OCR服务：`python paddleocrapp/app.py`
3. 确保OCR服务正常运行在5000端口（可以在浏览器中访问 http://127.0.0.1:5000/status 检查）
4. 如果您选择了快速安装（`--quick`），将不会安装OCR相关依赖，OCR功能将无法使用

### Q4: AI总结效果不理想？
**A**: 当前版本使用基于规则的简单总结算法。未来版本将集成：
- 更先进的自然语言处理模型
- 支持自定义总结规则
- 多种总结风格选择

### Q5: 有些linux系统报错
报错信息：
libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
libGL error: failed to load driver: swrast

**A**: 这个错误是因为程序需要 OpenGL 渲染环境和图形显示支持，但在当前环境（可能是无界面的服务器或容器）中不可用。解决方法是创建一个使用系统python pyqt的虚拟环境，具体使用方法见[说明文件](VENV_README.md) ,并使用run_browser.sh启动阅读器。

## 开发计划

### 近期计划
- [ ] 优化内容提取算法，提高准确率
- [ ] 增加更多小说网站的支持
- [ ] 改进AI总结功能，集成更智能的模型
- [ ] 添加阅读历史记录功能

### 远期计划
- [ ] 支持批量下载和处理章节
- [ ] 添加书签和笔记功能
- [ ] 开发浏览器插件版本
- [ ] 支持自定义提取规则

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

## 许可证

本项目采用 MIT 许可证。

## 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 跨平台GUI框架
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的OCR工具
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML解析库
- [文心快码Comate](https://comate.baidu.com/zh) - 智能代码助手

---

**最后更新**: 2025-11-25  
**版本**: 2.0  
**作者**: Novel Reader Helper Team
