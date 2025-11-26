#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器模块 - 基于PyQtWebEngine实现基本浏览器功能
"""

import sys
import os
import tempfile
import requests
import json
from urllib.parse import urlparse, urljoin

from web_extractor import WebExtractor
from mhtml_extractor import MHTMLExtractor
import mimetypes
import re

try:
    from PyQt5.QtCore import QUrl, pyqtSignal, QTimer, Qt
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                                QHBoxLayout, QWidget, QPushButton, QLineEdit, 
                                QProgressBar, QMessageBox, QToolBar, QAction,
                                QStatusBar, QLabel, QMenu, QSplitter)
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
    from PyQt5.QtGui import QIcon, QKeySequence
    PYQT_AVAILABLE = True
except ImportError as e:
    PYQT_AVAILABLE = False
    PYQT_ERROR = str(e)
    print(f"警告: PyQt5/PyQtWebEngine 未安装: {e}")
    
    # 创建模拟QMenu类避免导入错误
    class QMenu:
        def __init__(self, *args, **kwargs):
            pass
        def addAction(self, *args, **kwargs):
            return None
        def exec_(self, *args, **kwargs):
            return None
    
    # 创建模拟基类避免导入错误
    class QMainWindow:
        pass
    class QWebEngineView:
        pass
    class QWebEnginePage:
        pass
    class QUrl:
        pass
    class QMessageBox:
        Yes = None
        No = None
        @staticmethod
        def information(*args, **kwargs):
            pass
        @staticmethod
        def question(*args, **kwargs):
            return None
    # 创建模拟pyqtSignal，避免在没有PyQt5时的导入错误
    def pyqtSignal(*args, **kwargs):
        return None

class NovelBrowserPage(QWebEnginePage):
    """自定义网页页面类，用于处理弹窗、错误和导航请求"""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
    def javaScriptAlert(self, url, msg):
        """处理JavaScript alert"""
        QMessageBox.information(self.parent(), "网页提示", msg)
        
    def javaScriptConfirm(self, url, msg):
        """处理JavaScript confirm"""
        reply = QMessageBox.question(self.parent(), "网页确认", msg,
                                   QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """处理导航请求，确保链接点击能正常工作"""
        print(f"导航请求: {url.toString()}, 类型: {navigation_type}, 主框架: {is_main_frame}")
        return True
    
    def createWindow(self, window_type):
        """处理新窗口请求，在当前窗口打开"""
        print(f"创建窗口请求，类型: {window_type}")
        return self


class NovelBrowser(QMainWindow):
    """小说阅读器浏览器窗口"""
    
    # 定义信号
    page_loaded = pyqtSignal(str)  # 页面加载完成信号
    content_extracted = pyqtSignal(dict)  # 内容提取完成信号
    ai_summary_completed = pyqtSignal(str)  # AI总结完成信号
    closed = pyqtSignal()  # 窗口关闭信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not PYQT_AVAILABLE:
            raise ImportError(f"PyQt5/PyQtWebEngine 不可用: {PYQT_ERROR}")
            
        self.setWindowTitle("小说阅读器浏览器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 先初始化所有重要属性，避免setup_ui中出现属性未定义的情况
        self.web_view = None
        self.web_page = None
        self.address_bar = None
        self.address_widget = None
        self.progress_bar = None
        self.status_bar = None
        self.status_label = None
        self.operation_counter = None
        self.back_action = None
        self.forward_action = None
        self.refresh_action = None
        self.stop_action = None
        self.home_action = None
        self.extract_content_action = None
        self.ocr_images_action = None
        self.site_actions = []
        self.go_button = None
        self.navigation_timer = None
        
        # 设置默认主页
        self.default_urls = [
            "https://www.qidian.com",
            "https://www.zongheng.com", 
            "https://www.17k.com",
            "https://www.readnovel.com"
        ]
        
        # 初始化网页提取器
        self.web_extractor = WebExtractor()
        
        # 存储最后提取的内容，用于AI总结
        self.last_extracted_content = None
        
        # 初始化UI
        self.setup_ui()
        
        # 连接信号 - 放在setup_ui之后
        self.connect_signals()
        
        # 监听链接点击事件
        self.web_view.page().linkHovered.connect(self.link_hovered)
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局 - 垂直布局：顶部导航区域 + 浏览器视图
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 先创建网页视图（必须在create_address_bar之前）
        self.web_view = QWebEngineView()
        profile = QWebEngineProfile.defaultProfile()
        self.web_page = NovelBrowserPage(profile, self)
        self.web_view.setPage(self.web_page)
        
        # 创建导航动作
        self.create_navigation_actions()
        
        # 创建顶部区域（包含导航按钮和地址栏）
        self.create_address_bar()
        layout.addWidget(self.address_widget)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(2)
        layout.addWidget(self.progress_bar)
        
        # 创建分割器，使浏览器视图紧贴工具栏
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.web_view)
        layout.addWidget(splitter)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态栏标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 操作计数器
        self.operation_counter = QLabel("")
        self.status_bar.addPermanentWidget(self.operation_counter)
        
    def create_navigation_actions(self):
        """创建导航相关的动作"""
        # 后退按钮
        self.back_action = QAction("← 后退", self)
        self.back_action.setShortcut(QKeySequence("Alt+Left"))
        self.back_action.triggered.connect(self.go_back)
        
        # 前进按钮
        self.forward_action = QAction("前进 →", self)
        self.forward_action.setShortcut(QKeySequence("Alt+Right"))
        self.forward_action.triggered.connect(self.go_forward)
        
        # 刷新按钮
        self.refresh_action = QAction("🔄 刷新", self)
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.refresh_action.triggered.connect(self.web_view.reload)
        
        # 停止按钮
        self.stop_action = QAction("⏹ 停止", self)
        self.stop_action.setShortcut(QKeySequence("Esc"))
        self.stop_action.triggered.connect(self.web_view.stop)
        
        # 主页按钮
        self.home_action = QAction("🏠 主页", self)
        self.home_action.triggered.connect(self.go_home)
        
        # 添加"提取内容"按钮
        self.extract_content_action = QAction("📄 提取内容", self)
        self.extract_content_action.triggered.connect(self.extract_page_content)
        
        # 添加"识别图片"按钮
        self.ocr_images_action = QAction("🖼️ 识别图片", self)
        self.ocr_images_action.triggered.connect(self.extract_and_ocr_images)
        
        # 添加"打开文件"按钮
        self.open_file_action = QAction("📁 打开文件", self)
        self.open_file_action.triggered.connect(self.open_local_file)
        
        # 添加"AI总结"按钮
        self.ai_summary_action = QAction("📝 AI总结", self)
        self.ai_summary_action.triggered.connect(self.ai_summarize_content)
        
        # 创建工具栏并添加动作
        self.toolbar = self.addToolBar("Navigation")
        self.toolbar.addAction(self.back_action)
        self.toolbar.addAction(self.forward_action)
        self.toolbar.addAction(self.refresh_action)
        self.toolbar.addAction(self.stop_action)
        self.toolbar.addAction(self.home_action)
        self.toolbar.addAction(self.open_file_action)
        self.toolbar.addAction(self.extract_content_action)
        self.toolbar.addAction(self.ocr_images_action)
        self.toolbar.addAction(self.ai_summary_action)
        
        # 小说网站快捷按钮
        self.site_actions = []
        sites = [
            ("起点", "https://www.qidian.com"),
            ("纵横", "https://www.zongheng.com"),
            ("17K", "https://www.17k.com"),
            ("读书", "https://www.readnovel.com")
        ]
        
        for name, url in sites:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, u=url: self.load_url(u))
            self.site_actions.append(action)
            self.toolbar.addAction(action)
    def create_address_bar(self):
        """创建地址栏和导航区域"""
        # 创建顶部地址栏区域容器
        self.address_widget = QWidget()
        layout = QHBoxLayout(self.address_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 地址栏输入框 - 占据大部分空间
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("输入网址或搜索内容...")
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        layout.addWidget(self.address_bar, 1)  # 设置为拉伸因子1，占据剩余空间
        
        # 跳转按钮
        self.go_button = QPushButton("转到")
        self.go_button.setFixedSize(50, 30)
        self.go_button.clicked.connect(self.navigate_to_url)
        layout.addWidget(self.go_button)
    
    def create_sites_menu(self):
        """创建小说网站菜单"""
        sites_menu = QMenu(self)
        
        sites = [
            ("起点中文网", "https://www.qidian.com"),
            ("纵横中文网", "https://www.zongheng.com"),
            ("17K小说网", "https://www.17k.com"),
            ("起点读书", "https://www.readnovel.com")
        ]
        
        for name, url in sites:
            action = sites_menu.addAction(name)
            action.triggered.connect(lambda checked, u=url: self.load_url(u))
            
        return sites_menu
        
    def connect_signals(self):
        """连接信号槽"""
        try:
            # 页面加载相关
            self.web_view.loadStarted.connect(self.on_load_started)
            self.web_view.loadProgress.connect(self.on_load_progress)
            self.web_view.loadFinished.connect(self.on_load_finished)
            
            # URL变化
            self.web_view.urlChanged.connect(self.on_url_changed)
            
            # 标题变化
            self.web_view.titleChanged.connect(self.on_title_changed)
            
            # 使用定时器定期更新导航按钮状态
            self.navigation_timer = QTimer(self)
            self.navigation_timer.timeout.connect(self.update_navigation_buttons)
            self.navigation_timer.start(500)  # 每500毫秒更新一次
            
            print("浏览器信号连接成功")
        except Exception as e:
            print(f"连接浏览器信号时出错: {e}")

    def update_navigation_buttons(self):
        """更新导航按钮状态"""
        try:
            if hasattr(self, 'web_view') and self.web_view and self.web_view.page():
                history = self.web_view.page().history()
                if hasattr(self, 'back_action') and self.back_action:
                    self.back_action.setEnabled(history.canGoBack())
                if hasattr(self, 'forward_action') and self.forward_action:
                    self.forward_action.setEnabled(history.canGoForward())
        except Exception as e:
            # 如果更新导航按钮状态失败，静默处理，不影响主要功能
            pass
            
    def navigate_to_url(self):
        """导航到指定URL"""
        url_text = self.address_bar.text().strip()
        if not url_text:
            return
            
        # 如果不是完整URL，添加协议
        if not url_text.startswith(('http://', 'https://')):
            # 检查是否像是域名
            if '.' in url_text and ' ' not in url_text:
                url_text = 'https://' + url_text
            else:
                # 否则当作搜索内容
                search_url = f"https://www.baidu.com/s?wd={url_text}"
                url_text = search_url
        
        self.load_url(url_text)
        
    def load_url(self, url):
        """加载指定URL或本地文件"""
        try:
            if isinstance(url, str):
                qurl = QUrl.fromUserInput(url)
            else:
                qurl = url

            if qurl.isLocalFile():
                file_path = qurl.toLocalFile()
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type == 'message/rfc822' or file_path.lower().endswith('.mhtml'):
                    self.load_mhtml_file(file_path)
                else:
                    self.web_view.load(qurl)
            else:
                self.web_view.load(qurl)

            self.address_bar.setText(qurl.toString())

        except Exception as e:
            self.show_error(f"加载页面失败: {str(e)}")

    def open_local_file(self):
        """打开本地文件对话框"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "打开文件",
                "",
                "网页文件 (*.html *.htm *.mhtml *.mht *.png *.jpg *.jpeg *.gif *.bmp);;所有文件 (*)"
            )
            if file_path:
                self.load_url(QUrl.fromLocalFile(file_path))
        except Exception as e:
            self.show_error(f"打开文件失败: {str(e)}")

    def load_mhtml_file(self, file_path):
        """加载MHTML文件"""
        try:
            self.status_label.setText("正在解析MHTML文件...")
            extractor = MHTMLExtractor()
            extractor.set_debug(True)
            result = extractor.extract_content(file_path)
            
            if result and result.get('text'):
                # 创建格式化的HTML显示
                text_content = result['text'].replace('\n', '<br>')
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{result.get('title', 'MHTML文档')}</title>
                    <style>
                        body {{
                            font-family: 'Microsoft YaHei', Arial, sans-serif;
                            line-height: 1.8;
                            padding: 30px;
                            max-width: 800px;
                            margin: 0 auto;
                            background-color: #f9f9f9;
                        }}
                        .header {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 10px;
                            margin-bottom: 30px;
                            text-align: center;
                        }}
                        h1 {{
                            margin: 0;
                            font-size: 24px;
                        }}
                        .content {{
                            background: white;
                            padding: 30px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                            font-size: 16px;
                            text-indent: 2em;
                        }}
                        .meta {{
                            color: #666;
                            font-size: 14px;
                            margin-top: 10px;
                        }}
                        .extract-btn {{
                            background: #4CAF50;
                            color: white;
                            padding: 10px 20px;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            margin: 10px 5px;
                        }}
                        .extract-btn:hover {{
                            background: #45a049;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{result.get('title', 'MHTML文档')}</h1>
                        <div class="meta">
                            文件: {os.path.basename(file_path)} | 
                            字符数: {len(result['text'])} | 
                            提取方式: {result.get('extraction_method', 'mhtml_parse')}
                        </div>
                        <button class="extract-btn" onclick="extractContent()">📄 提取内容到阅读器</button>
                    </div>
                    <div class="content">
                        {text_content}
                    </div>
                    <script>
                        function extractContent() {{
                            // 这个函数会被浏览器的提取功能调用
                            alert('请点击浏览器工具栏中的"📄 提取内容"按钮来提取文本到阅读器');
                        }}
                    </script>
                </body>
                </html>
                """
                self.web_view.setHtml(html_content, QUrl.fromLocalFile(file_path))
                self.status_label.setText(f"✅ MHTML文件解析成功 - {len(result['text'])} 字符")
                
                # 自动存储提取结果供后续使用
                self._mhtml_extracted_content = result
            else:
                self.show_error("无法从MHTML文件中提取有效内容")
                self.status_label.setText("❌ MHTML文件解析失败")
        except Exception as e:
            self.show_error(f"加载MHTML文件失败: {str(e)}")
            self.status_label.setText("❌ MHTML文件加载失败")
            
    def go_back(self):
        """后退到上一页"""
        if self.web_view.history().canGoBack():
            self.web_view.back()
    
    def go_forward(self):
        """前进到下一页"""
        if self.web_view.history().canGoForward():
            self.web_view.forward()
    
    def go_home(self):
        """返回主页"""
        if self.default_urls:
            self.load_url(self.default_urls[0])
        else:
            self.load_url("https://www.qidian.com")
            
    def on_load_started(self):
        """页面开始加载"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在加载...")
        
    def on_load_progress(self, progress):
        """页面加载进度"""
        self.progress_bar.setValue(progress)
        
    def on_load_finished(self, success):
        """页面加载完成"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("✅ 页面加载完成")
            current_url = self.web_view.url().toString()
            self.page_loaded.emit(current_url)
        else:
            self.status_label.setText("❌ 页面加载失败")
            self.show_warning("页面加载失败，请检查网络连接或尝试刷新页面")
            
    def on_url_changed(self, url):
        """URL变化"""
        self.address_bar.setText(url.toString())
        
    def on_title_changed(self, title):
        """标题变化"""
        if title:
            self.setWindowTitle(f"{title} - 小说阅读器浏览器")
        else:
            self.setWindowTitle("小说阅读器浏览器")
    
    def link_hovered(self, url):
        """当鼠标悬停在链接上时的处理"""
        if url:
            print(f"悬停链接: {url}")
            self.status_label.setText(f"链接: {url}")
        else:
            self.status_label.setText("就绪")
    
    def test_qidian_extraction(self):
        """测试起点小说内容提取功能"""
        # 使用几个不同的公开测试URL
        test_urls = [
            "https://read.qidian.com/chapter/T5xbHbF-yI1FTfAHd-Wr_A2/SVTsSUN1UwFOw7OTSj-_RA2",  # 大主宰章节
            "https://read.qidian.com/chapter/O9zPuzOQBNt1rJncIam83g2/XJ-I3K5yd-p8Po6gSgj89A2",  # 圣墟章节
            "https://www.qidian.com/chapter/1010734492/34467002/"  # 另一种URL格式
        ]
        
        # 使用第一个URL
        test_url = test_urls[0]
        self.status_label.setText(f"🧪 开始测试：加载起点小说章节...")
        print(f"\n{'='*60}")
        print(f"🧪 测试起点小说内容提取")
        print(f"测试URL: {test_url}")
        print(f"{'='*60}\n")
        
        # 加载测试URL
        self.load_url(test_url)
        
        # 设置定时器，等待页面加载后自动提取
        def auto_extract():
            current_url = self.get_current_url()
            status = self.status_label.text()
            
            print(f"当前URL: {current_url}")
            print(f"加载状态: {status}")
            
            if "qidian.com" in current_url:
                if "✅" in status or "加载完成" in status:
                    print("✅ 页面加载完成，开始提取内容...")
                    self.status_label.setText("🧪 测试中：正在提取内容...")
                    
                    # 等待2秒后提取，确保页面完全渲染
                    QTimer.singleShot(2000, self.extract_page_content)
                else:
                    print("⏳ 页面还在加载，继续等待...")
                    QTimer.singleShot(2000, auto_extract)
            else:
                print("⚠️ URL不正确，可能加载失败")
                self.status_label.setText("❌ 测试失败：页面加载不正确")
        
        # 等待8秒后开始检查，给足够时间加载
        QTimer.singleShot(8000, auto_extract)
            
    def show_error(self, message):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)
        
    def show_warning(self, message):
        """显示警告消息"""
        QMessageBox.warning(self, "警告", message)
        
    def show_info(self, message):
        """显示信息消息"""
        QMessageBox.information(self, "提示", message)
        
    def get_current_url(self):
        """获取当前URL"""
        return self.web_view.url().toString()
        
    def get_current_title(self):
        """获取当前页面标题"""
        return self.web_view.title()
        
    def execute_javascript(self, script):
        """执行JavaScript代码"""
        self.web_view.page().runJavaScript(script)

    def extract_page_content(self):
        """提取当前页面的文本内容"""
        try:
            self.status_label.setText("正在提取网页内容...")
            if hasattr(self, 'extract_content_action') and self.extract_content_action:
                self.extract_content_action.setEnabled(False)
            
            current_url = self.web_view.url().toString()
            if "qidian.com" in current_url or "zongheng.com" in current_url or "17k.com" in current_url:
                self.extract_novel_content()
            else:
                self.get_page_content(self._process_extracted_content)
        except Exception as e:
            self.show_error(f"提取内容失败: {str(e)}")
            self.status_label.setText("提取内容失败")
            if hasattr(self, 'extract_content_action') and self.extract_content_action:
                self.extract_content_action.setEnabled(True)

    def extract_novel_content(self):
        """提取小说网站的内容"""
        print("开始提取小说内容...")
        
        # 直接获取HTML并用正则提取，更可靠
        self.web_view.page().toHtml(self._extract_novel_content_from_html)
        
    def _extract_novel_content_from_html(self, html):
        """从HTML中提取小说内容"""
        try:
            print(f"获取到HTML内容，长度: {len(html)} 字符")
            url = self.web_view.url().toString()
            
            # 分析是否为起点小说网章节页
            is_qidian_chapter = "qidian.com" in url and ("chapter" in url or "read" in url)
            is_zongheng_chapter = "zongheng.com" in url and "chapter" in url
            
            # 提取标题
            title = ""
            title_patterns = [
                r'<h1[^>]*class="j_chapterName"[^>]*>(.*?)</h1>',
                r'<h3[^>]*class="j_chapterName"[^>]*>(.*?)</h3>',
                r'<span[^>]*class="j_chapterName"[^>]*>(.*?)</span>',
                r'<h1[^>]*>(.*?)</h1>',
                r'<div[^>]*class="chapter-name[^"]*"[^>]*>(.*?)</div>',
                r'<title>(.*?)</title>'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    extracted = match.group(1).strip()
                    # 清除HTML标签
                    extracted = re.sub(r'<[^>]+>', '', extracted)
                    if extracted:
                        title = extracted
                        break
            
            # 使用不同的内容提取模式
            content = ""
            chapter_info = ""
            
            # 先检查是否有起点特有的章节内容
            if is_qidian_chapter:
                # 提取章节信息
                info_patterns = [
                    r'<div[^>]*class="info-chapter[^"]*"[^>]*>(.*?)</div>',
                    r'<p[^>]*class="chapter-info[^"]*"[^>]*>(.*?)</p>'
                ]
                for pattern in info_patterns:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        chapter_info = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                        break
                
                # 提取正文内容
                content_patterns = [
                    r'<div[^>]*class="read-content[^"]*"[^>]*>(.*?)</div>',
                    r'<div[^>]*id="content"[^>]*>(.*?)</div>'
                ]
                for pattern in content_patterns:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        content_html = match.group(1)
                        # 移除script和style标签
                        content_html = re.sub(r'<script[^>]*>.*?</script>', '', content_html, flags=re.IGNORECASE | re.DOTALL)
                        content_html = re.sub(r'<style[^>]*>.*?</style>', '', content_html, flags=re.IGNORECASE | re.DOTALL)
                        
                        # 提取所有段落
                        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content_html, re.IGNORECASE | re.DOTALL)
                        if paragraphs:
                            # 处理每个段落
                            cleaned_paragraphs = []
                            for p in paragraphs:
                                # 移除HTML标签
                                p = re.sub(r'<[^>]+>', '', p)
                                # 替换HTML实体
                                p = re.sub(r'&nbsp;', ' ', p)
                                p = re.sub(r'&[a-z]+;', '', p)
                                p = p.strip()
                                if p:  # 只添加非空段落
                                    cleaned_paragraphs.append(p)
                            
                            # 使用双换行连接段落
                            content = "\n\n".join(cleaned_paragraphs)
                        
                        if content:
                            break
            
            # 如果是其他小说网站或上述方法失败，使用通用方法
            if not content:
                # 尝试其他通用模式
                content_patterns = [
                    r'<div[^>]*class="chapter-content[^"]*"[^>]*>(.*?)</div>',
                    r'<article[^>]*class="content[^"]*"[^>]*>(.*?)</article>',
                    r'<div[^>]*id="chapterContent[^"]*"[^>]*>(.*?)</div>'
                ]
                
                for pattern in content_patterns:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        content_html = match.group(1)
                        # 清理HTML
                        content = re.sub(r'<[^>]+>', '', content_html)
                        content = re.sub(r'&nbsp;', ' ', content)
                        content = re.sub(r'&[a-z]+;', '', content)
                        content = re.sub(r'\s+', ' ', content).strip()
                        if content:
                            break
            
            # 如果还是没有找到内容，尝试最后的备选方案
            if not content:
                # 尝试提取所有p标签
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
                if paragraphs:
                    # 过滤和清理段落
                    paragraphs = [re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs]
                    paragraphs = [p for p in paragraphs if len(p) > 30]  # 只保留较长的段落
                    content = "\n\n".join(paragraphs)
            
            # 确保标题和内容都不为空
            if not title:
                title = "未知标题"
            
            # 提取成功
            if content and len(content.strip()) > 100:
                print(f"✅ 成功提取内容: 标题='{title}', 内容长度={len(content)}")
                extracted_content = {
                    'title': title,
                    'text': content.strip(),
                    'chapter_info': chapter_info,
                    'url': url,
                    'word_count': len(content.strip()),
                    'extraction_method': 'direct_html'
                }
                
                # 保存最后提取的内容
                self.last_extracted_content = extracted_content
                
                # 发送提取结果
                self.content_extracted.emit(extracted_content)
                self.status_label.setText(f"✅ 内容提取完成 - 已提取 {len(content)} 字符")
                
                # 显示提取内容对话框
                self.show_extracted_content_dialog(extracted_content)
            else:
                print(f"❌ 内容提取失败: 标题='{title}', 内容长度={len(content) if content else 0}")
                self.show_warning("未能提取到有效内容，请尝试其他页面")
                self.status_label.setText("❌ 内容提取失败 - 无有效内容")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"处理小说内容时出错: {str(e)}")
            self.show_error(f"处理提取内容时出错: {str(e)}")
            self.status_label.setText("❌ 内容处理失败")
        finally:
            if hasattr(self, 'extract_content_action') and self.extract_content_action:
                self.extract_content_action.setEnabled(True)

    def _process_novel_content(self, result):
        try:
            print(f"JavaScript提取返回: {result[:200]}...")  # 打印前200个字符
            data = json.loads(result)
            
            content = data.get('content', '')
            if isinstance(content, dict):
                # 处理字体反爬的情况
                text = content.get('text', '')
                font_url = content.get('fontUrl')
                if font_url:
                    print(f"检测到字体反爬，字体URL: {font_url}")
                    # 这里可以添加字体解密逻辑
                    # 暂时使用未解密的文本
                    content = text
            elif isinstance(content, str):
                content = content.strip()
            
            if content and len(content) > 100:
                # JavaScript提取成功
                extracted_content = {
                    'title': data.get('title', '未知标题'),
                    'text': content,
                    'chapter_info': data.get('chapterInfo', ''),
                    'url': self.web_view.url().toString(),
                    'word_count': len(content)
                }
                print(f"✅ JavaScript提取成功: {len(content)} 字符")
                self.content_extracted.emit(extracted_content)
                self.status_label.setText(f"✅ 内容提取完成 - 已提取 {len(content)} 字符")
                self.show_info(f"内容提取成功！\n标题: {extracted_content['title']}\n提取字符数: {len(content)}\n来源: {self.web_view.url().toString()}")
            else:
                # JavaScript提取失败，使用正则表达式从HTML中提取
                print("JavaScript提取失败，尝试使用正则表达式...")
                html = data.get('html', '')
                if html:
                    self._extract_from_html(html)
                else:
                    self.show_warning("未能提取到有效内容，请尝试其他页面")
                    self.status_label.setText("❌ 内容提取失败 - 无有效内容")
        except Exception as e:
            print(f"处理提取内容时出错: {str(e)}")
            self.show_error(f"处理提取内容时出错: {str(e)}")
            self.status_label.setText("❌ 内容处理失败")
        finally:
            if hasattr(self, 'extract_content_action') and self.extract_content_action:
                self.extract_content_action.setEnabled(True)
    
    def _extract_from_html(self, html):
        """从HTML中使用正则表达式提取内容"""
        print(f"开始从HTML提取，HTML长度: {len(html)}")
        
        # 提取标题
        title = ''
        title_patterns = [
            r'<h1[^>]*>(.*?)</h1>',
            r'class="j_chapterName"[^>]*>(.*?)<',
            r'class="chapter-title"[^>]*>(.*?)<',
            r'<title>(.*?)</title>'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if title:
                    break
        
        # 提取内容
        content = ''
        content_patterns = [
            r'<div[^>]*class="read-content"[^>]*>(.*?)</div>',
            r'<div[^>]*id="content"[^>]*>(.*?)</div>',
            r'<div[^>]*class="chapter-content"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1)
                # 清理HTML标签
                content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
                content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
                content = re.sub(r'<[^>]+>', '', content)
                content = re.sub(r'&nbsp;', ' ', content)
                content = re.sub(r'&[a-z]+;', '', content)
                content = re.sub(r'\s+', ' ', content).strip()
                
                if len(content) > 100:
                    print(f"✅ 正则提取成功: {len(content)} 字符")
                    break
        
        if content and len(content) > 100:
            extracted_content = {
                'title': title or '未知标题',
                'text': content,
                'url': self.web_view.url().toString(),
                'word_count': len(content),
                'extraction_method': 'regex'
            }
            self.content_extracted.emit(extracted_content)
            self.status_label.setText(f"✅ 内容提取完成 - 已提取 {len(content)} 字符")
            self.show_info(f"内容提取成功！\n标题: {title}\n提取字符数: {len(content)}\n来源: {self.web_view.url().toString()}")
        else:
            print(f"❌ 正则提取失败，提取的内容长度: {len(content)}")
            self.show_warning(f"未能提取到有效内容，提取长度: {len(content)}")
            self.status_label.setText("❌ 内容提取失败 - 无有效内容")

    def _process_extracted_content(self, html):
        """处理提取的HTML内容"""
        try:
            current_url = self.web_view.url().toString()
            
            # 检查是否是从MHTML文件加载的内容
            if hasattr(self, '_mhtml_extracted_content') and self._mhtml_extracted_content:
                # 直接使用已解析的MHTML内容
                extracted_content = self._mhtml_extracted_content
                word_count = len(extracted_content.get('text', ''))
                self.content_extracted.emit(extracted_content)
                self.status_label.setText(f"✅ MHTML内容提取完成 - 已提取 {word_count} 字符")
                self.show_info(f"MHTML内容提取成功！\n标题: {extracted_content.get('title', '未知')}\n提取字符数: {word_count}\n来源: {extracted_content.get('source', '本地文件')}")
                # 清除缓存的内容
                self._mhtml_extracted_content = None
                return
            
            if not html or len(html.strip()) < 100:
                self.show_warning("页面内容为空或过短，可能提取失败")
                self.status_label.setText("提取内容失败 - 页面内容不足")
                return
            
            # 尝试提取标题
            title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title.group(1) if title else "未知标题"
            
            # 尝试提取正文内容
            content = ""
            content_patterns = [
                r'<div\s+class="read-content[^"]*">(.*?)</div>',
                r'<div\s+id="content">(.*?)</div>',
                r'<article[^>]*>(.*?)</article>'
            ]
            for pattern in content_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    content = match.group(1)
                    break
            
            if not content:
                # 如果没有找到特定的内容区，尝试提取所有<p>标签的内容
                content = ' '.join(re.findall(r'<p>(.*?)</p>', html, re.IGNORECASE | re.DOTALL))
            
            # 清理HTML标签
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            if content:
                extracted_content = {
                    'title': title,
                    'text': content,
                    'url': current_url,
                    'word_count': len(content)
                }
                self.content_extracted.emit(extracted_content)
                self.status_label.setText(f"✅ 内容提取完成 - 已提取 {len(content)} 字符")
                self.show_info(f"内容提取成功！\n标题: {title}\n提取字符数: {len(content)}\n来源: {current_url}")
            else:
                self.show_warning("未能提取到有效内容，请尝试其他页面")
                self.status_label.setText("❌ 内容提取失败 - 无有效内容")
                
        except Exception as e:
            self.show_error(f"处理提取内容时出错: {str(e)}")
            self.status_label.setText("❌ 内容处理失败")
        finally:
            if hasattr(self, 'extract_content_action') and self.extract_content_action:
                self.extract_content_action.setEnabled(True)

    def extract_and_ocr_images(self):
        """下载页面图片并进行OCR识别"""
        try:
            self.status_label.setText("正在提取页面图片...")
            self.ocr_images_action.setEnabled(False)
            
            # 检查OCR服务是否可用
            try:
                response = requests.get("http://127.0.0.1:5000/status", timeout=3)
                if response.status_code != 200:
                    self.show_warning("OCR服务不可用，请确保PaddleOCR服务正在运行")
                    self.ocr_images_action.setEnabled(True)
                    return
            except requests.RequestException:
                self.show_warning("无法连接到OCR服务，请确保服务已启动")
                self.status_label.setText("❌ OCR服务未连接")
                self.show_info("请按以下步骤启动OCR服务:\n1. 打开新的终端窗口\n2. 导航到paddleocr目录: cd paddleocr\n3. 启动OCR服务: python app.py")
                self.ocr_images_action.setEnabled(True)
                return
                
            # 使用安全的方式获取页面内容
            try:
                self.get_page_content(self._process_images_for_ocr)
            except Exception as e:
                self.show_error(f"获取页面内容失败: {str(e)}")
                self.status_label.setText("❌ 页面内容获取失败")
                self.ocr_images_action.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"启动图片识别失败: {str(e)}")
            self.status_label.setText("❌ 图片识别启动失败")
            self.ocr_images_action.setEnabled(True)

    def _process_images_for_ocr(self, html):
        """处理HTML中的图片并进行OCR"""
        processed_count = 0
        success_count = 0
        
        try:
            current_url = self.web_view.url().toString()
            
            # 安全检查html内容
            if not html:
                self.show_warning("页面内容为空，无法提取图片")
                self.status_label.setText("❌ 页面内容为空")
                self.ocr_images_action.setEnabled(True)
                return
                
            try:
                images = self.web_extractor.extract_images(html, current_url)
            except Exception as e:
                self.show_error(f"提取图片信息失败: {str(e)}")
                self.status_label.setText("❌ 图片提取失败")
                self.ocr_images_action.setEnabled(True)
                return
            
            if not images:
                self.show_info("当前页面未发现可识别的图片")
                self.status_label.setText("ℹ️ 未发现图片")
                self.ocr_images_action.setEnabled(True)
                return
                    
            self.status_label.setText(f"发现 {len(images)} 张图片，开始处理...")
            ocr_results = []
            all_ocr_text = ""
            
            for i, img in enumerate(images, 1):
                try:
                    processed_count += 1
                    self.status_label.setText(f"正在处理第 {i}/{len(images)} 张图片...")
                    self.operation_counter.setText(f"{i}/{len(images)}")
                    
                    # 判断是本地文件还是网络图片
                    img_url = img['url']
                    if img_url.startswith('file://'):
                        # 本地文件，直接使用路径
                        from urllib.parse import unquote
                        from urllib.request import url2pathname
                        local_path = url2pathname(unquote(img_url[7:]))  # 移除 file:// 前缀
                        
                        # 检查文件是否存在
                        if not os.path.exists(local_path):
                            print(f"本地图片文件不存在: {local_path}")
                            continue
                        
                        # 检查文件大小
                        if os.path.getsize(local_path) < 1024:
                            print(f"图片文件太小，跳过: {local_path}")
                            continue
                        
                        temp_img_path = local_path
                        is_temp_file = False
                    else:
                        # 网络图片，需要下载
                        img_response = requests.get(img_url, headers=self.web_extractor.headers, timeout=10)
                        if img_response.status_code != 200:
                            continue
                            
                        img_content = img_response.content
                        if len(img_content) < 1024:  # 图片太小，跳过
                            continue
                            
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img:
                            temp_img.write(img_content)
                            temp_img_path = temp_img.name
                        is_temp_file = True

                    # 调用OCR服务
                    ocr_url = "http://127.0.0.1:5000/ocr"
                    try:
                        with open(temp_img_path, 'rb') as img_file:
                            # 注意：POST请求参数名从"image"改为"file"，与服务端匹配
                            response = requests.post(ocr_url, files={"file": img_file}, timeout=60)
                        
                        if response.status_code == 200:
                            ocr_result = response.json()
                            ocr_text = ""
                            
                            # 处理不同格式的OCR返回结果
                            if ocr_result.get("status") == "success" or ocr_result.get("success", False):
                                if "results" in ocr_result:
                                    # 确保results是列表并且包含text字段
                                    results = ocr_result["results"]
                                    if isinstance(results, list):
                                        ocr_text = "\n".join([item.get("text", "") for item in results if isinstance(item, dict)])
                                elif "data" in ocr_result:
                                    data = ocr_result["data"]
                                    if isinstance(data, list):
                                        ocr_text = "\n".join([item.get("text", "") for item in data if isinstance(item, dict)])
                                elif "text" in ocr_result:
                                    ocr_text = str(ocr_result["text"])
                                    
                            if ocr_text.strip():
                                ocr_results.append({
                                    'image_url': img['url'],
                                    'ocr_text': ocr_text.strip(),
                                    'confidence': ocr_result.get('confidence', 0)
                                })
                                all_ocr_text += ocr_text.strip() + "\n\n"
                                success_count += 1
                    except requests.RequestException as req_err:
                        print(f"OCR请求失败: {req_err}")
                        continue

                    # 删除临时文件（仅删除网络下载的临时文件）
                    if is_temp_file:
                        try:
                            os.unlink(temp_img_path)
                        except:
                            pass
                        
                except Exception as img_error:
                    print(f"处理图片 {i} 时出错: {img_error}")
                    continue

            # 合并文本和OCR结果
            try:
                content = self.web_extractor.extract_text(html)
                combined_result = {
                    'title': '图片OCR识别结果',
                    'text': all_ocr_text,
                    'ocr_results': ocr_results,
                    'url': current_url,
                    'word_count': len(all_ocr_text)
                }
                
                if success_count > 0:
                    self.content_extracted.emit(combined_result)
                    self.status_label.setText(f"✅ 图片识别完成 - 成功识别 {success_count}/{processed_count} 张图片")
                    self.show_extracted_content_dialog(combined_result)
                else:
                    self.show_warning(f"图片识别完成，但未识别出文字内容\n处理了 {processed_count} 张图片")
                    self.status_label.setText(f"⚠️ 未识别出文字 - 已处理 {processed_count} 张图片")
                    
            except Exception as e:
                self.show_error(f"合并识别结果时出错: {str(e)}")
                self.status_label.setText("❌ 结果合并失败")
                
        except Exception as e:
            self.show_error(f"图片识别过程出错: {str(e)}")
            self.status_label.setText("❌ 图片识别失败")
        finally:
            self.ocr_images_action.setEnabled(True)
            self.operation_counter.setText("")
            
        # 保存最后提取的内容，以便进行AI总结
        self.last_extracted_content = combined_result

        
    def get_page_content(self, callback):
        """获取页面内容（异步）- 增强版，支持动态内容"""
        def handle_result(html):
            # 处理None值或空字符串
            if html is None or not html:
                print("警告: 获取到的HTML内容为空")
                callback("")
                return
                
            # 如果HTML内容过短，尝试执行JavaScript获取更多内容
            if len(html) < 1000:
                self.execute_javascript_and_get_content(callback, html)
            else:
                callback(html)
        
        # 首先等待页面完全加载
        self.web_view.page().toHtml(handle_result)
    
    def execute_javascript_and_get_content(self, callback, fallback_html):
        """执行JavaScript脚本获取动态内容，针对起点中文网优化"""
        js_script = """
        function waitForElement(selector, timeout) {
            return new Promise((resolve, reject) => {
                const startTime = Date.now();
                const checkElement = () => {
                    const element = document.querySelector(selector);
                    if (element) {
                        resolve(element);
                    } else if (Date.now() - startTime > timeout) {
                        reject(new Error('超时：未找到元素'));
                    } else {
                        setTimeout(checkElement, 100);
                    }
                };
                checkElement();
            });
        }

        async function extractContent() {
            try {
                // 等待页面加载完成
                await waitForElement('.read-content', 10000);
                
                // 尝试触发懒加载
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 1000));

                // 提取小说内容
                const contentElement = document.querySelector('.read-content');
                if (contentElement) {
                    let content = contentElement.innerText || contentElement.textContent;
                    
                    // 处理字体反爬
                    const fontFace = document.querySelector('style[data-qidian]');
                    if (fontFace) {
                        const fontUrl = fontFace.textContent.match(/url\\(['"]?(.*?)['"]?\\)/);
                        if (fontUrl) {
                            content = {
                                text: content,
                                fontUrl: fontUrl[1]
                            };
                        }
                    }
                    
                    return JSON.stringify({
                        content: content,
                        title: document.querySelector('.j_chapterName').textContent.trim(),
                        chapterInfo: document.querySelector('.info-chapter').textContent.trim()
                    });
                }
            } catch (error) {
                console.error('提取内容时出错：', error);
            }
            
            // 如果提取失败，返回整个HTML
            return document.documentElement.outerHTML;
        }

        return extractContent();
        """
        
        def js_callback(result):
            try:
                # 处理None值情况
                if result is None:
                    print("警告: JavaScript返回了None值")
                    callback(fallback_html)
                    return
                    
                # 尝试解析JSON结果
                parsed_result = json.loads(result)
                if isinstance(parsed_result, dict) and 'content' in parsed_result:
                    # 处理成功提取的内容
                    if isinstance(parsed_result['content'], dict) and 'fontUrl' in parsed_result['content']:
                        # 需要进一步处理字体反爬
                        self.handle_font_obfuscation(parsed_result)
                    callback(json.dumps(parsed_result))
                else:
                    # 如果不是预期的JSON格式，返回原始HTML
                    callback(result if len(str(result)) > len(fallback_html) else fallback_html)
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON或发生类型错误，返回原始HTML
                callback(fallback_html)
        
        self.web_view.page().runJavaScript(js_script, js_callback)
    
    def ai_summarize_content(self):
        """AI总结当前提取的内容"""
        if not self.last_extracted_content:
            self.show_warning("请先提取小说内容后再进行AI总结")
            return
        
        text = self.last_extracted_content.get('text', '')
        title = self.last_extracted_content.get('title', '未知标题')
        
        if not text or len(text.strip()) < 50:
            self.show_warning("提取的内容太短，无法进行有效总结")
            return
        
        self.status_label.setText("正在进行AI总结，请稍候...")
        self.ai_summary_action.setEnabled(False)
        
        try:
            # 调用AI总结功能
            summary = self.generate_summary(text, title)
            
            # 显示总结结果
            self.display_summary(summary, title)
            
            # 发送信号
            self.ai_summary_completed.emit(summary)
            
            self.status_label.setText("✅ AI总结完成")
            
        except Exception as e:
            self.show_error(f"AI总结失败: {str(e)}")
            self.status_label.setText("❌ AI总结失败")
        finally:
            self.ai_summary_action.setEnabled(True)
    
    def generate_summary(self, text, title):
        """生成内容摘要 - 基于规则的简单总结"""
        # 分句
        sentences = []
        for delimiter in ['。', '！', '？', '\n']:
            text = text.replace(delimiter, delimiter + '|||')
        
        raw_sentences = text.split('|||')
        sentences = [s.strip() for s in raw_sentences if s.strip() and len(s.strip()) > 5]
        
        # 构建总结
        summary_parts = []
        summary_parts.append("=" * 50)
        summary_parts.append(f"📖 《{title}》内容摘要")
        summary_parts.append("=" * 50)
        summary_parts.append("")
        
        # 基本信息
        summary_parts.append("📊 基本信息：")
        summary_parts.append(f"  • 原文长度：{len(text)} 字符")
        summary_parts.append(f"  • 段落数量：{len(sentences)} 句")
        summary_parts.append(f"  • 来源：{self.last_extracted_content.get('url', '本地文件')}")
        summary_parts.append("")
        
        # 内容预览
        if len(text) > 200:
            summary_parts.append("🔍 开头内容：")
            summary_parts.append("-" * 30)
            # 取前3句或前200字符
            preview_sentences = sentences[:3] if len(sentences) >= 3 else sentences
            preview_text = ''.join(preview_sentences)
            if len(preview_text) > 200:
                preview_text = preview_text[:200] + "..."
            summary_parts.append(preview_text)
            summary_parts.append("")
            
            if len(sentences) > 6:
                summary_parts.append("🔍 结尾内容：")
                summary_parts.append("-" * 30)
                # 取后3句
                ending_sentences = sentences[-3:]
                ending_text = ''.join(ending_sentences)
                if len(ending_text) > 200:
                    ending_text = ending_text[-200:]
                summary_parts.append(ending_text)
                summary_parts.append("")
        else:
            summary_parts.append("📝 完整内容：")
            summary_parts.append("-" * 30)
            summary_parts.append(text)
            summary_parts.append("")
        
        # 关键词提取（简单的词频统计）
        summary_parts.append("?? 内容特征：")
        char_count = len(text)
        if char_count < 500:
            summary_parts.append("  • 篇幅：短篇")
        elif char_count < 2000:
            summary_parts.append("  • 篇幅：中篇")
        else:
            summary_parts.append("  • 篇幅：长篇")
        
        # 检测常见关键词
        keywords = {
            "对话": ["说道", "说：", "问道", "答道", "回答"],
            "动作": ["走", "跑", "看", "听", "想"],
            "情感": ["喜", "怒", "哀", "乐", "爱", "恨"],
            "描写": ["美丽", "壮观", "宏伟", "精致"]
        }
        
        detected_features = []
        for feature, words in keywords.items():
            if any(word in text for word in words):
                detected_features.append(feature)
        
        if detected_features:
            summary_parts.append(f"  • 包含元素：{', '.join(detected_features)}")
        
        summary_parts.append("")
        summary_parts.append("=" * 50)
        summary_parts.append("💡 提示：这是基于规则的简单总结，未来版本将支持更智能的AI分析")
        summary_parts.append("=" * 50)
        
        return '\n'.join(summary_parts)
    
    def display_summary(self, summary, title):
        """显示AI总结结果"""
        # 创建新窗口显示总结
        from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle(f"AI总结 - {title}")
        dialog.setGeometry(200, 200, 700, 500)

        layout = QVBoxLayout(dialog)

        # 总结文本显示
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(summary)
        layout.addWidget(text_edit)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 复制按钮
        copy_btn = QPushButton("📋 复制总结")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(summary))
        button_layout.addWidget(copy_btn)

        # 保存按钮
        save_btn = QPushButton("💾 保存总结")
        save_btn.clicked.connect(lambda: self.save_summary(summary, title))
        button_layout.addWidget(save_btn)

        # 查看原文按钮
        view_original_btn = QPushButton("👀 查看原文")
        view_original_btn.clicked.connect(lambda: self.view_original_content(self.last_extracted_content))
        button_layout.addWidget(view_original_btn)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec_()

    def show_extracted_content_dialog(self, content):
        """显示提取内容的对话框，包含查看和保存按钮"""
        from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        from datetime import datetime

        dialog = QDialog(self)
        dialog.setWindowTitle(f"内容提取成功 - {content.get('title', '未知标题')}")
        dialog.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout(dialog)

        # 信息区域
        info_text = f"✅ 内容提取成功！\n\n标题: {content.get('title', '未知')}\n字数: {content.get('word_count', 0)} 字符\n来源: {content.get('url', '未知')}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("padding: 10px; background-color: #e8f5e9; border-radius: 5px;")
        layout.addWidget(info_label)

        # 内容预览区域
        preview_label = QLabel("内容预览（前500字符）：")
        layout.addWidget(preview_label)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        preview_text = content.get('text', '')[:500]
        if len(content.get('text', '')) > 500:
            preview_text += "\n\n... (点击\"查看完整内容\"查看全文)"
        text_edit.setPlainText(preview_text)
        layout.addWidget(text_edit)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 查看完整内容按钮
        view_btn = QPushButton("👀 查看完整内容")
        view_btn.clicked.connect(lambda: self.view_full_content(content))
        button_layout.addWidget(view_btn)

        # 保存按钮
        save_btn = QPushButton("💾 保存内容")
        save_btn.clicked.connect(lambda: self.save_extracted_content(content))
        button_layout.addWidget(save_btn)

        # 复制按钮
        copy_btn = QPushButton("📋 复制内容")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(content.get('text', '')))
        button_layout.addWidget(copy_btn)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec_()

    def view_full_content(self, content):
        """查看完整提取内容"""
        from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle(f"完整内容 - {content.get('title', '未知标题')}")
        dialog.setGeometry(150, 150, 900, 700)

        layout = QVBoxLayout(dialog)

        # 完整内容显示
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content.get('text', '无内容'))
        layout.addWidget(text_edit)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def view_original_content(self, content):
        """查看原文内容（用于AI总结对话框）"""
        self.view_full_content(content)

    def save_extracted_content(self, content):
        """保存提取的内容到文件"""
        from PyQt5.QtWidgets import QFileDialog
        from datetime import datetime
        
        title = content.get('title', '未知标题')
        default_filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存提取内容",
            default_filename,
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"标题: {title}\n")
                    f.write(f"来源: {content.get('url', '未知')}\n")
                    f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"字数: {content.get('word_count', 0)}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(content.get('text', ''))
                self.show_info(f"内容已保存到：\n{filename}")
                self.status_label.setText(f"✅ 内容已保存")
            except Exception as e:
                self.show_error(f"保存失败: {str(e)}")
    
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_label.setText("✅ 已复制到剪贴板")
    
    def save_summary(self, summary, title):
        """保存总结到文件"""
        from PyQt5.QtWidgets import QFileDialog
        from datetime import datetime
        
        default_filename = f"{title}_总结_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存AI总结",
            default_filename,
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary)
                self.show_info(f"总结已保存到：\n{filename}")
                self.status_label.setText(f"✅ 总结已保存")
            except Exception as e:
                self.show_error(f"保存失败: {str(e)}")


# 全局QApplication实例
_qapp_instance = None

def get_qapplication():
    """获取或创建QApplication实例"""
    global _qapp_instance
    if _qapp_instance is None:
        # 检查是否已经有QApplication实例
        from PyQt5.QtWidgets import QApplication
        _qapp_instance = QApplication.instance()
        if _qapp_instance is None:
            # 创建新的QApplication实例
            _qapp_instance = QApplication(sys.argv)
    return _qapp_instance

def create_browser_window(parent=None):
    """创建浏览器窗口的工厂函数"""
    if not PYQT_AVAILABLE:
        raise ImportError(f"无法创建浏览器窗口: {PYQT_ERROR}")
    
    try:
        # 确保QApplication已经初始化
        get_qapplication()
        
        # 创建并返回浏览器窗口实例
        browser = NovelBrowser(parent)
        return browser
    except Exception as e:
        print(f"创建浏览器窗口失败: {e}")
        raise


def main():
    """独立运行浏览器的主函数"""
    if not PYQT_AVAILABLE:
        print(f"错误: PyQt5/PyQtWebEngine 不可用: {PYQT_ERROR}")
        print("\n请安装依赖:")
        print("pip install PyQt5 PyQtWebEngine")
        return
        
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("小说阅读器浏览器")
    app.setApplicationVersion("1.0")
    
    try:
        browser = NovelBrowser()
        browser.show()
        
        # 加载默认页面
        browser.go_home()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"启动浏览器失败: {str(e)}")
        QMessageBox.critical(None, "错误", f"启动浏览器失败:\n{str(e)}")


if __name__ == "__main__":
    main()