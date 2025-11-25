#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 专门测试从起点小说网提取内容的功能
"""

import sys
import time
import json
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QTextEdit, QLabel, QWidget
from browser import NovelBrowser

class TestWindow(QMainWindow):
    """测试窗口，显示提取结果"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("起点小说内容提取测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 浏览器部分
        self.browser = NovelBrowser()
        self.browser.setFixedHeight(500)  # 限制浏览器高度
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        # 起点测试按钮
        self.test_btn = QPushButton("测试起点章节")
        self.test_btn.clicked.connect(self.test_qidian)
        control_layout.addWidget(self.test_btn)
        
        # 提取按钮
        self.extract_btn = QPushButton("提取内容")
        self.extract_btn.clicked.connect(self.extract_content)
        control_layout.addWidget(self.extract_btn)
        
        # 提取结果
        self.result_label = QLabel("提取结果:")
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        # 添加到布局
        layout.addWidget(self.browser)
        layout.addLayout(control_layout)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_text)
        
        # 连接信号
        self.browser.content_extracted.connect(self.on_content_extracted)
        
        # 设置测试URL
        self.test_urls = [
            "https://read.qidian.com/chapter/T5xbHbF-yI1FTfAHd-Wr_A2/SVTsSUN1UwFOw7OTSj-_RA2",
            "https://www.qidian.com/book/1030713177/643897823/",
            "https://read.qidian.com/chapter/1030713177/643897823"
        ]
    
    def test_qidian(self):
        """测试起点小说提取"""
        # 使用第一个测试URL
        self.clear_result()
        self.log_message("开始测试起点小说内容提取...")
        self.log_message(f"加载测试URL: {self.test_urls[0]}")
        
        self.browser.load_url(self.test_urls[0])
        
        # 设置定时器检查页面加载
        QTimer.singleShot(5000, self.check_page_loaded)
    
    def check_page_loaded(self):
        """检查页面是否加载完成"""
        status = self.browser.status_label.text()
        url = self.browser.get_current_url()
        
        self.log_message(f"当前URL: {url}")
        self.log_message(f"加载状态: {status}")
        
        if "qidian.com" in url or "read.qidian.com" in url:
            if "✅" in status or "加载完成" in status:
                self.log_message("页面加载完成，请点击'提取内容'按钮测试提取功能")
                self.extract_btn.setEnabled(True)
            else:
                self.log_message("页面仍在加载，继续等待...")
                QTimer.singleShot(2000, self.check_page_loaded)
        else:
            self.log_message("页面未正确加载到起点小说，请重试")
    
    def extract_content(self):
        """手动触发内容提取"""
        self.log_message("开始提取页面内容...")
        self.browser.extract_page_content()
    
    def on_content_extracted(self, content):
        """处理提取的内容"""
        self.log_message("✅ 内容提取成功!")
        
        # 显示提取结果的基本信息
        if isinstance(content, dict):
            title = content.get('title', '')
            text = content.get('text', '')
            url = content.get('url', '')
            
            self.log_message(f"标题: {title}")
            self.log_message(f"URL: {url}")
            self.log_message(f"字符数: {len(text)}")
            
            # 显示前500个字符的内容预览
            preview_text = text[:500] + "..." if len(text) > 500 else text
            self.log_message("\n--- 内容预览 ---\n")
            self.result_text.append(preview_text)
            
            # 保存到文件以便检查
            try:
                with open("extracted_qidian_content.txt", "w", encoding="utf-8") as f:
                    f.write(f"标题: {title}\n\n")
                    f.write(f"URL: {url}\n\n")
                    f.write(f"字符数: {len(text)}\n\n")
                    f.write("--- 内容 ---\n\n")
                    f.write(text)
                self.log_message("\n内容已保存到 extracted_qidian_content.txt")
            except Exception as e:
                self.log_message(f"保存到文件时出错: {e}")
        else:
            self.log_message("提取内容格式不正确")
    
    def log_message(self, message):
        """记录消息到结果区域"""
        self.result_text.append(message)
    
    def clear_result(self):
        """清除结果区域"""
        self.result_text.clear()

def main():
    """主函数"""
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    window = TestWindow()
    window.show()
    
    print("测试窗口已启动")
    print("请点击'测试起点章节'按钮开始测试")
    
    return app.exec_()

if __name__ == "__main__":
    main()