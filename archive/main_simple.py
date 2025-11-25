#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 实用版
包含基础OCR和AI总结功能，避免复杂依赖冲突
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import threading
import math
from datetime import datetime
import urllib.request
import urllib.parse
import json
from functools import partial
import logging
import traceback
import queue
from config import *

# 添加一个全局的任务队列
task_queue = queue.Queue()

# 设置日志
logging.basicConfig(filename='novel_reader.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(e):
    logging.error(f"An error occurred: {str(e)}\n{traceback.format_exc()}")

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: PIL/Pillow 未安装，图片功能将不可用")

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("警告: jieba 未安装，智能分词功能将不可用")

# 浏览器功能检查
try:
    from browser import create_browser_window, PYQT_AVAILABLE
    BROWSER_AVAILABLE = PYQT_AVAILABLE
    if not BROWSER_AVAILABLE:
        print("警告: PyQt5/PyQtWebEngine 未安装，浏览器功能将不可用")
except ImportError as e:
    BROWSER_AVAILABLE = False
    print(f"警告: 浏览器模块导入失败: {e}")

# 导入PyQt5用于地址栏功能
if BROWSER_AVAILABLE:
    try:
        from PyQt5.QtCore import QUrl
    except ImportError:
        print("警告: PyQt5.QtCore 导入失败")

OCR_AVAILABLE = False

def check_ocr_service():
    """检查OCR服务是否可用"""
    try:
        response = urllib.request.urlopen(f"{OCR_SERVICE_URL}/status", timeout=2)
        return response.status == 200
    except Exception:
        return False

OCR_AVAILABLE = check_ocr_service()

class NovelReaderMain:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title(WINDOW_TITLE)
            self.root.geometry(WINDOW_SIZE)
            
            # 状态变量
            self.current_image = None
            self.current_image_path = None
            self.browser_window = None  # 保存浏览器窗口引用
            self.browser_status = tk.StringVar(value="准备中")  # 浏览器状态变量
            self.status_var = tk.StringVar()  # 提前初始化状态变量
            self.status_var.set("就绪")
            
            # 设置线程安全标志
            self.summarizing = False
            
            # 先创建界面
            self.setup_ui()
            
            # 延迟初始化浏览器，避免主界面未完成就初始化PyQt5组件
            self.root.after(500, self.initialize_browser)
            
            # 创建浏览器按钮
            self.create_browser_button()
            
            # 添加主窗口关闭事件处理
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            
            # 启动任务处理线程
            self.start_task_thread()
            
        except Exception as e:
            log_error(e)
            raise
    
    def start_task_thread(self):
        """启动任务处理线程"""
        def task_worker():
            while True:
                try:
                    task, args = task_queue.get()
                    if task is None:
                        break
                    task(*args)
                except Exception as e:
                    print(f"任务执行错误: {e}")
                finally:
                    task_queue.task_done()

        threading.Thread(target=task_worker, daemon=True).start()

    def queue_task(self, task, *args):
        """将任务加入队列"""
        task_queue.put((task, args))
    
    def on_close(self):
        """窗口关闭事件处理"""
        try:
            # 确保浏览器实例被正确关闭
            if hasattr(self, 'browser_window') and self.browser_window:
                try:
                    self.browser_window.close()
                    self.browser_window = None
                except:
                    pass
            
            # 退出主窗口
            self.root.destroy()
        except Exception as e:
            print(f"关闭窗口时发生错误: {e}")
            self.root.destroy()

    def initialize_browser(self):
        """初始化浏览器实例（隐藏方式启动）"""
        # 设置一个标志，表示初始化是否已完成
        self.browser_initialized = False
        
        # 添加进度指示
        self.status_var.set("正在初始化浏览器组件...")
        
        try:
            if BROWSER_AVAILABLE:
                try:
                    # 使用全局变量存储QApplication实例，防止被垃圾回收
                    global _qapp_instance
                    from browser import get_qapplication
                    _qapp_instance = get_qapplication()
                    
                    self.browser_window = create_browser_window(None)
                    
                    # 确保browser_window实例已完全初始化并且具有必要属性
                    if hasattr(self.browser_window, 'web_view'):
                        # 初始化web_view之后再进行其他操作
                        if hasattr(self.browser_window, 'page_loaded'):
                            self.browser_window.page_loaded.connect(self.on_browser_page_loaded)
                        if hasattr(self.browser_window, 'content_extracted'):
                            self.browser_window.content_extracted.connect(self.handle_browser_content)
                        if hasattr(self.browser_window, 'closed'):
                            self.browser_window.closed.connect(self.on_browser_closed)
                        
                        # 隐藏浏览器窗口，但保持实例运行
                        if hasattr(self.browser_window, 'hide'):
                            self.browser_window.hide()
                        self.browser_status.set("就绪")
                        
                        # 标记初始化已完成
                        self.browser_initialized = True
                        
                        # 延迟连接URL变化信号到下一个事件循环，使用try-except保护
                        self.root.after(100, self.connect_browser_signals)
                    else:
                        self.browser_status.set("浏览器初始化不完整")
                        print("警告: 浏览器窗口缺少web_view属性")
                except Exception as e:
                    log_error(e)
                    self.browser_status.set("初始化错误")
                    print(f"错误: 浏览器初始化失败: {str(e)}")
                    self.browser_window = None
            else:
                self.browser_status.set("不可用")
                print("警告: 浏览器功能不可用，请检查PyQt5和PyQtWebEngine是否正确安装")
        except Exception as e:
            log_error(e)
            self.browser_status.set("错误")
            print(f"错误: 初始化浏览器失败: {str(e)}")
            
    def connect_browser_signals(self):
        """连接浏览器信号（延迟执行）"""
        try:
            # 检查初始化状态和浏览器实例
            if not hasattr(self, 'browser_initialized') or not self.browser_initialized:
                print("浏览器尚未完全初始化，无法连接信号")
                # 再次尝试延迟连接
                self.root.after(500, self.connect_browser_signals)
                return
                
            if BROWSER_AVAILABLE and self.browser_window:
                # 确保浏览器窗口已完全初始化
                if hasattr(self.browser_window, 'web_view'):
                    try:
                        self.browser_window.web_view.urlChanged.connect(self.on_browser_url_changed)
                        print("浏览器信号连接成功")
                    except Exception as e:
                        print(f"连接urlChanged信号失败: {e}")
                else:
                    print("警告: 浏览器实例缺少 web_view 属性，无法连接信号")
        except Exception as e:
            log_error(e)
            print(f"错误: 连接浏览器信号失败: {str(e)}")
        
    def ocr_image(self, image_path=None):
        """对图片进行OCR识别
        
        Args:
            image_path: 图片路径，如果为None则使用当前加载的图片
        """
        if not OCR_AVAILABLE:
            return "OCR服务不可用，请检查PaddleOCR服务是否正常运行。"
        
        # 如果没有指定路径，使用当前加载的图片
        if image_path is None:
            image_path = self.current_image_path
        
        if not image_path:
            return "没有可识别的图片"
        
        try:
            url = f"{OCR_SERVICE_URL}/ocr/local"
            params = {"path": image_path}
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url) as response:
                result = json.loads(response.read().decode())
                
            if result.get("status") == "success" or result.get("success", False):
                if "results" in result:
                    return "\n".join([item["text"] for item in result["results"]])
                elif "data" in result:
                    return "\n".join([item["text"] for item in result["data"]])
                else:
                    return "OCR识别成功，但返回数据格式不正确"
            else:
                return f"OCR识别失败：{result.get('message', '未知错误')}"
        except Exception as e:
            return f"OCR过程出错：{str(e)}"

    def open_image_file(self):
        """打开图片文件"""
        if not PIL_AVAILABLE:
            messagebox.showwarning("警告", "PIL/Pillow未安装，无法打开图片")
            return
        
        filetypes = [
            ('图片文件', '*.png *.jpg *.jpeg *.bmp *.gif'),
            ('所有文件', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.current_image_path = filename
                img = Image.open(filename)
                
                # 调整图片大小以适应画布
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()
                
                if canvas_width < 100:  # 画布还未渲染
                    canvas_width, canvas_height = 800, 600
                
                img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
                
                self.current_image = ImageTk.PhotoImage(img)
                
                # 清空画布并显示图片
                self.image_canvas.delete("all")
                self.image_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.current_image, anchor=tk.CENTER
                )
                
                self.notebook.select(1)  # 切换到图片预览选项卡
                self.status_var.set(f"已加载图片: {os.path.basename(filename)}")
                
                messagebox.showinfo("提示", 
                    '图片已加载！\n\n点击"OCR识别图片"按钮进行文字识别。')
                
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败: {str(e)}")
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态变量初始化
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        
        # 添加浏览器地址栏（仅在浏览器可用时）
        if BROWSER_AVAILABLE:
            self.create_address_bar(main_frame)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 主工作区权重
        
        # 标题
        title_label = ttk.Label(main_frame, text="小说阅读神器 - 实用版", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        # 按钮
        ttk.Button(control_frame, text="📂 打开文本文件", 
                  command=self.open_text_file, width=20).pack(pady=5, fill=tk.X)
        
        if PIL_AVAILABLE:
            ttk.Button(control_frame, text="🖼️ 打开图片文件", 
                      command=self.open_image_file, width=20).pack(pady=5, fill=tk.X)
            
            ttk.Button(control_frame, text="📷 OCR识别图片", 
                      command=self.perform_ocr, width=20).pack(pady=5, fill=tk.X)
            
            ttk.Button(control_frame, text="🧪 OCR测试", 
                      command=self.test_ocr, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📝 AI总结",
                  command=self.summarize_text, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="💾 保存结果", 
                  command=self.save_results, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="🗑️ 清空内容", 
                  command=self.clear_all, width=20).pack(pady=5, fill=tk.X)
        
        if BROWSER_AVAILABLE:
            ttk.Button(control_frame, text="🌐 打开浏览器", 
                      command=self.open_browser, width=20).pack(pady=5, fill=tk.X)
        
        # 添加分隔线
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 添加配置选项
        if JIEBA_AVAILABLE:
            ttk.Label(control_frame, text="关键词数量:").pack(pady=(10, 0), fill=tk.X)
            self.keyword_num = tk.IntVar(value=8)
            ttk.Spinbox(control_frame, from_=3, to=20, 
                       textvariable=self.keyword_num, width=5).pack(pady=(0, 10), fill=tk.X)
            
            ttk.Label(control_frame, text="摘要句子数量:").pack(pady=(10, 0), fill=tk.X)
            self.summary_num = tk.IntVar(value=5)
            ttk.Spinbox(control_frame, from_=2, to=10, 
                       textvariable=self.summary_num, width=5).pack(pady=(0, 10), fill=tk.X)
        
        # 状态信息
        ttk.Label(control_frame, text="\n功能状态:").pack(pady=(20, 5), fill=tk.X)
        status_text = []
        status_text.append("✅ 文本分析")
        status_text.append(f"✅ 图片预览" if PIL_AVAILABLE else "❌ 图片预览")
        status_text.append(f"✅ OCR识别" if OCR_AVAILABLE else "❌ OCR识别 (服务未启动)")
        status_text.append(f"✅ 内置浏览器" if BROWSER_AVAILABLE else "❌ 内置浏览器")
        
        for text in status_text:
            ttk.Label(control_frame, text=text, font=("Arial", 9)).pack(fill=tk.X)
        
        # 添加分隔线
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 浏览器状态显示
        if BROWSER_AVAILABLE:
            ttk.Label(control_frame, text="浏览器状态:", font=("Arial", 9)).pack(pady=(10, 0), fill=tk.X)
            browser_status_label = ttk.Label(control_frame, textvariable=self.browser_status, 
                                           font=("Arial", 9), foreground="blue")
            browser_status_label.pack(fill=tk.X)
        
        # 右侧主工作区 - 使用Notebook创建选项卡
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文本输入选项卡
        text_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(text_frame, text="📄 文本输入")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=20)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 图片预览选项卡
        if PIL_AVAILABLE:
            image_frame = ttk.Frame(self.notebook, padding="5")
            self.notebook.add(image_frame, text="🖼️ 图片预览")
            image_frame.columnconfigure(0, weight=1)
            image_frame.rowconfigure(0, weight=1)
            
            self.image_canvas = tk.Canvas(image_frame, bg='white')
            self.image_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # AI总结选项卡
        summary_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(summary_frame, text="📝 AI总结")
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, height=20)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 状态栏 (status_var已经在__init__中初始化)
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_address_bar(self, parent):
        """创建顶部地址栏区域"""
        # 地址栏框架
        address_frame = ttk.LabelFrame(parent, text="浏览器地址栏", padding="5")
        address_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        address_frame.columnconfigure(1, weight=1)  # 地址输入框占据大部分空间
        
        # 导航按钮区域
        nav_frame = ttk.Frame(address_frame)
        nav_frame.grid(row=0, column=0, padx=(0, 5))
        
        # 后退按钮
        self.back_btn = ttk.Button(nav_frame, text="←", width=3, 
                                  command=self.browser_back, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # 前进按钮
        self.forward_btn = ttk.Button(nav_frame, text="→", width=3, 
                                     command=self.browser_forward, state=tk.DISABLED)
        self.forward_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(nav_frame, text="🔄", width=3, 
                                     command=self.browser_refresh, state=tk.DISABLED)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # 地址输入框
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(address_frame, textvariable=self.address_var, 
                                      font=("Arial", 10))
        self.address_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.address_entry.bind('<Return>', self.on_address_enter)
        
        # 转到按钮
        self.go_btn = ttk.Button(address_frame, text="转到", width=6, 
                                command=self.navigate_to_address)
        self.go_btn.grid(row=0, column=2, padx=(0, 5))
        
        # 功能按钮区域
        func_frame = ttk.Frame(address_frame)
        func_frame.grid(row=0, column=3)
        
        # 提取内容按钮
        self.extract_btn = ttk.Button(func_frame, text="📄 提取内容", 
                                     command=self.extract_browser_content, state=tk.DISABLED)
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # 识别图片按钮
        self.ocr_btn = ttk.Button(func_frame, text="🖼️ 识别图片", 
                                 command=self.extract_browser_images, state=tk.DISABLED)
        self.ocr_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # 初始化地址栏状态
        self.update_address_bar_state()

    def create_browser_button(self):
        """创建打开/关闭浏览器按钮"""
        if BROWSER_AVAILABLE:
            self.browser_button = ttk.Button(self.root, text="🌐 打开浏览器", 
                                            command=self.toggle_browser)
            self.browser_button.grid(row=4, column=0, columnspan=2, pady=(10, 0))

    def toggle_browser(self):
        """切换浏览器的打开/关闭状态"""
        if self.browser_window is None or not self.browser_window.isVisible():
            self.open_browser()
        else:
            self.close_browser()

    def open_browser(self):
        """打开内置浏览器"""
        if not BROWSER_AVAILABLE:
            messagebox.showwarning("警告", "浏览器功能不可用，请检查PyQt5和PyQtWebEngine是否正确安装")
            return
        
        try:
            self.browser_window = create_browser_window(None)
            self.browser_window.page_loaded.connect(self.on_browser_page_loaded)
            self.browser_window.content_extracted.connect(self.handle_browser_content)
            self.browser_window.closed.connect(self.on_browser_closed)
            self.browser_window.show()
            self.browser_status.set("已打开")
            self.browser_button.configure(text="🌐 关闭浏览器")
            self.update_address_bar_state()
        except Exception as e:
            messagebox.showerror("错误", f"操作浏览器失败: {str(e)}")

    def close_browser(self):
        """关闭内置浏览器"""
        if self.browser_window:
            self.browser_window.close()

    
    def open_text_file(self):
        """打开文本文件"""
        filetypes = [
            ('文本文件', '*.txt'),
            ('所有文件', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=filetypes
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(tk.END, content)
                self.notebook.select(0)  # 切换到文本输入选项卡
                self.status_var.set(f"已加载文件: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
    
    def open_image_file(self):
        """打开图片文件"""
        if not PIL_AVAILABLE:
            messagebox.showwarning("警告", "PIL/Pillow未安装，无法打开图片")
            return
        
        filetypes = [
            ('图片文件', '*.png *.jpg *.jpeg *.bmp *.gif'),
            ('所有文件', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.current_image_path = filename
                img = Image.open(filename)
                
                # 调整图片大小以适应画布
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()
                
                if canvas_width < 100:  # 画布还未渲染
                    canvas_width, canvas_height = 800, 600
                
                img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
                
                self.current_image = ImageTk.PhotoImage(img)
                
                # 清空画布并显示图片
                self.image_canvas.delete("all")
                self.image_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.current_image, anchor=tk.CENTER
                )
                
                self.notebook.select(1)  # 切换到图片预览选项卡
                self.status_var.set(f"已加载图片: {os.path.basename(filename)}")
                
                messagebox.showinfo("提示", "图片已加载！\n\n请点击「OCR识别图片」按钮进行文字识别。")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败: {str(e)}")

    def perform_ocr(self):
        """执行OCR识别"""
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先加载图片")
            return
        
        if not OCR_AVAILABLE:
            messagebox.showwarning("警告", "OCR服务不可用，请检查PaddleOCR服务是否正常运行")
            return
        
        self.status_var.set("正在进行OCR识别...")
        ocr_result = self.ocr_image(self.current_image_path)
        self.text_input.delete(1.0, tk.END)
        self.text_input.insert(tk.END, ocr_result)
        self.notebook.select(0)  # 切换到文本输入选项卡
        self.status_var.set("OCR识别完成")
        messagebox.showinfo("OCR完成", "图片文字识别已完成，结果已添加到文本输入区域。")
    
    def test_ocr(self):
        """测试OCR功能 - 使用指定的测试图片"""
        if not OCR_AVAILABLE:
            messagebox.showwarning("警告", "OCR服务不可用，请检查PaddleOCR服务是否正常运行")
            return
        
        # 检查测试图片是否存在
        if not os.path.exists(TEST_IMAGE_PATH):
            messagebox.showerror("错误", f"测试图片不存在：\n{TEST_IMAGE_PATH}")
            return
        
        self.status_var.set("正在进行OCR测试...")
        
        try:
            # 调用OCR识别方法
            url = f"{OCR_SERVICE_URL}/ocr/local"
            params = {"path": test_image_path}
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url) as response:
                raw_result = response.read().decode()
                result = json.loads(raw_result)
            
            # 显示原始响应
            print("OCR服务原始响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 处理OCR结果
            if result.get("status") == "success" or result.get("success", False):
                if "results" in result:
                    ocr_result = "\n".join([item["text"] for item in result["results"]])
                elif "data" in result:
                    ocr_result = "\n".join([item["text"] for item in result["data"]])
                else:
                    ocr_result = "OCR识别成功，但返回数据格式不正确"
            else:
                ocr_result = f"OCR识别失败：{result.get('message', '未知错误')}"
            
            # 显示识别结果
            result_message = f"OCR测试完成！\n\n测试图片：{os.path.basename(test_image_path)}\n\n识别结果：\n{ocr_result}"
            
            # 更新状态
            self.status_var.set("OCR测试完成")
            
            # 显示结果对话框
            messagebox.showinfo("OCR测试结果", result_message)
            
            # 同时将结果添加到文本输入区域
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(tk.END, f"[OCR测试结果 - {test_image_path}]\n\n原始响应:\n{raw_result}\n\n处理后的结果:\n{ocr_result}")
            self.notebook.select(0)  # 切换到文本输入选项卡
            
        except Exception as e:
            self.status_var.set("OCR测试失败")
            messagebox.showerror("错误", f"OCR测试过程出错：\n{str(e)}")
    
    def summarize_text(self):
        """AI总结文本"""
        text_to_summarize = self.text_input.get(1.0, tk.END).strip()
        
        if not text_to_summarize:
            messagebox.showwarning("警告", "没有可总结的文本内容")
            return
        
        if not JIEBA_AVAILABLE:
            # 如果没有jieba，使用基础分析
            self.basic_analysis(text_to_summarize)
            return
            
        self.status_var.set("正在进行AI总结，请稍候...")
        
        # 使用线程避免界面卡顿
        threading.Thread(target=self.run_summarize, args=(text_to_summarize,), daemon=True).start()
    
    def basic_analysis(self, text):
        """基础文本分析（无需jieba）"""
        char_count = len(text)
        lines = text.count('\n') + 1
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        reading_time = char_count / 500
        
        # 分句
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 提取章节标题
        chapter_title = ""
        first_line = text.split('\n')[0].strip()
        if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
            chapter_title = first_line
        
        # 提取前后几句
        first_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        last_sentences = sentences[-3:] if len(sentences) >= 3 else []
        
        # 组装结果
        result = []
        if chapter_title:
            result.append(f"# {chapter_title}\n")
        else:
            result.append("# 文本分析\n")
        
        result.append("## 基本统计")
        result.append(f"- 总字符数: {char_count} 字符")
        result.append(f"- 中文字符: {chinese_chars} 个汉字")
        result.append(f"- 行数: {lines} 行")
        result.append(f"- 句子数: {len(sentences)} 句")
        result.append(f"- 预计阅读时间: {int(reading_time)} 分钟 {int((reading_time % 1) * 60)} 秒")
        result.append("")
        
        result.append("## 内容概要")
        result.append("### 开始部分:")
        for s in first_sentences:
            result.append(f"- {s}")
        
        if last_sentences and last_sentences != first_sentences:
            result.append("\n### 结束部分:")
            for s in last_sentences:
                result.append(f"- {s}")
        
        result.append("\n\n💡 提示: 安装 jieba 库可获得更智能的关键词提取和摘要功能")
        
        summary = '\n'.join(result)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.notebook.select(2)  # 切换到总结选项卡
        self.status_var.set("基础分析完成")
    
    def run_summarize(self, text):
        """在线程中运行总结功能"""
        try:
            # 如果是字符串，直接处理
            if isinstance(text, str):
                result = self.analyze_chapter(text)
                summary = self.format_chapter_summary(result)
                
                # 使用队列任务更新UI
                self.queue_task(self.update_summary_result, summary)
            # 如果是列表（多段内容），安全处理每段
            elif isinstance(text, list):
                all_summaries = []
                for segment in text:
                    result = self.analyze_chapter(segment)
                    summary = self.format_chapter_summary(result)
                    all_summaries.append(summary)
                
                # 合并所有摘要并使用队列任务更新UI
                final_summary = "\n\n" + "="*40 + "\n\n".join(all_summaries)
                self.queue_task(self.update_summary_result, final_summary)
        except Exception as e:
            error_msg = f"总结失败: {str(e)}"
            self.queue_task(messagebox.showerror, "错误", error_msg)
            self.queue_task(self.status_var.set, "总结失败")
    
    def update_summary_result(self, summary):
        """更新AI总结结果"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.notebook.select(2)  # 切换到总结选项卡
        self.status_var.set("AI总结完成")
    
    def extract_keywords(self, text, topK=8):
        """提取关键词"""
        if not JIEBA_AVAILABLE:
            return []
        keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
        return keywords
    
    def get_important_sentences(self, text, topK=5):
        """获取最重要的几个句子"""
        # 分句
        try:
            text = re.sub(r'([。！？\?])([^"\'"])', r'\1\n\2', text)
            text = re.sub(r'(\.{6})([^"\'"])', r'\1\n\2', text)
            text = re.sub(r'(\…{2})([^"\'"])', r'\1\n\2', text)
            text = re.sub(r'([。！？\?]["\'"])([^，。！？\?])', r'\1\n\2', text)
        except Exception as e:
            log_error(e)
            print(f"分句处理出错: {e}")
            # 如果分句失败，使用简单的方法
            text = re.sub(r'([。！？\?\.])', r'\1\n', text)
        
        sentences = text.split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= topK:
            return sentences
        
        if not JIEBA_AVAILABLE:
            # 简单返回前topK个句子
            return sentences[:topK]
        
        # 提取关键词
        keywords_dict = {}
        keywords = self.extract_keywords(text, topK=20)
        for word, weight in keywords:
            keywords_dict[word] = weight
        
        # 计算句子得分
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0
            for word in jieba.cut(sentence):
                if word in keywords_dict:
                    score += keywords_dict[word]
            
            position_weight = 1.0
            if i < len(sentences) * 0.1 or i > len(sentences) * 0.9:
                position_weight = 1.2
            
            score = score * position_weight
            sentence_scores.append((i, sentence, score))
        
        sentence_scores.sort(key=lambda x: x[2], reverse=True)
        top_sentences = sentence_scores[:topK]
        top_sentences.sort(key=lambda x: x[0])
        
        return [s[1] for s in top_sentences]
    
    def analyze_chapter(self, chapter_text, chapter_title=""):
        """分析小说章节"""
        if not chapter_title and len(chapter_text) > 0:
            first_line = chapter_text.split('\n')[0].strip()
            if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
                chapter_title = first_line
        
        char_count = len(chapter_text)
        
        keyword_num = self.keyword_num.get() if JIEBA_AVAILABLE else 0
        summary_num = self.summary_num.get() if JIEBA_AVAILABLE else 5
        
        keywords = self.extract_keywords(chapter_text, topK=keyword_num)
        keyword_list = [word for word, _ in keywords]
        
        important_sentences = self.get_important_sentences(chapter_text, topK=summary_num)
        
        result = {
            "title": chapter_title,
            "char_count": char_count,
            "word_count": char_count // 2,
            "keywords": keyword_list,
            "important_sentences": important_sentences
        }
        
        return result
        
    def format_chapter_summary(self, chapter_analysis):
        """格式化章节总结"""
        result = []
        
        if chapter_analysis["title"]:
            result.append(f"# {chapter_analysis['title']}")
        else:
            result.append("# 章节概要")
            
        result.append("")
        result.append(f"📊 字数统计：约 {chapter_analysis['char_count']} 字")
        result.append(f"⏱️ 阅读时间：约 {math.ceil(chapter_analysis['char_count'] / 500)} 分钟")
        result.append("")
        
        if chapter_analysis["keywords"]:
            result.append("🔑 关键词：")
            result.append("  " + "、".join(chapter_analysis["keywords"]))
            result.append("")
        
        result.append("📖 重要内容：")
        for sentence in chapter_analysis["important_sentences"]:
            result.append(f"  • {sentence}")
        
        return "\n".join(result)
    
    def save_results(self):
        """保存结果"""
        summary = self.summary_text.get(1.0, tk.END).strip()
        if not summary:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".txt",
            filetypes=[('文本文件', '*.txt'), ('所有文件', '*.*')]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("小说阅读神器 - 分析结果\n")
                    f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(summary)
                
                messagebox.showinfo("成功", f"结果已保存到: {filename}")
                self.status_var.set(f"结果已保存: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def clear_all(self):
        """清空所有内容"""
        self.text_input.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        if PIL_AVAILABLE:
            self.image_canvas.delete("all")
        self.current_image = None
        self.current_image_path = None
        self.status_var.set("已清空所有内容")

    def open_browser(self):
        """打开内置浏览器"""
        if not BROWSER_AVAILABLE:
            messagebox.showwarning("警告", "浏览器功能不可用，请检查PyQt5和PyQtWebEngine是否正确安装")
            return
        
        try:
            if self.browser_window is None or not self.browser_window.isVisible():
                self.browser_window = create_browser_window(None)  # 使用None替代self.root，创建独立窗口
                self.browser_window.page_loaded.connect(self.on_browser_page_loaded)
                self.browser_window.content_extracted.connect(self.handle_browser_content)
                self.browser_window.closed.connect(self.on_browser_closed)
                self.browser_window.show()
                self.browser_status.set("已打开")
                self.browser_button.configure(text="🌐 关闭浏览器")
            else:
                self.browser_window.close()
        except Exception as e:
            messagebox.showerror("错误", f"操作浏览器失败: {str(e)}")

    def on_browser_closed(self):
        """浏览器关闭的回调"""
        try:
            if hasattr(self, 'browser_status'):
                self.browser_status.set("已关闭")
            # 重置地址栏状态
            if hasattr(self, 'address_var'):
                self.address_var.set("")
            if hasattr(self, 'update_address_bar_state'):
                self.update_address_bar_state()
            self.browser_window = None
            print("浏览器窗口已关闭")
        except Exception as e:
            print(f"关闭浏览器窗口时出错: {e}")

    def on_browser_page_loaded(self, url):
        """浏览器页面加载完成的回调"""
        try:
            if hasattr(self, 'status_var') and self.status_var:
                self.status_var.set(f"浏览器加载完成: {url}")
            else:
                print(f"浏览器加载完成: {url}")
            # 更新地址栏按钮状态
            if hasattr(self, 'update_address_bar_state'):
                self.update_address_bar_state()
            # 更新地址栏显示
            if hasattr(self, 'address_var') and url:
                self.address_var.set(url)
        except Exception as e:
            print(f"页面加载回调时出错: {e}")

    def handle_browser_content(self, content_dict):
        """处理从浏览器提取的内容"""
        # 使用 try-except 捕获可能的错误
        try:
            # 处理不同格式的内容字典
            if 'text_content' in content_dict:
                # 处理OCR图片内容的格式
                text_content = content_dict.get('text_content', '')
                ocr_results = content_dict.get('ocr_results', [])
                url = self.get_browser_url()
                title = self.get_browser_title()
                
                # 合并文本内容
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                full_content = f"# 浏览器内容提取 ({timestamp})\n\n"
                full_content += f"**标题**: {title}\n"
                full_content += f"**来源**: {url}\n"
                full_content += f"**提取方式**: 图像识别\n\n"
                full_content += "=" * 40 + "\n\n"  # 添加分隔线
                full_content += text_content
                
                # 处理OCR结果
                if ocr_results:
                    full_content += "\n\n" + "=" * 40 + "\n## 图片OCR识别结果:\n"
                    for i, result in enumerate(ocr_results, 1):
                        ocr_text = result.get('ocr_text', '')
                        confidence = result.get('confidence', 0)
                        img_url = result.get('image_url', '未知')
                        full_content += f"\n### 图片 {i}:\n"
                        full_content += f"- 来源: {img_url}\n"
                        full_content += f"- 识别内容: {ocr_text}\n"
                        if confidence:
                            full_content += f"- 可信度: {confidence:.2f}\n"
            else:
                # 处理普通文本内容的格式
                text_content = content_dict.get('text', '')
                images = content_dict.get('images', [])
                title = content_dict.get('title', '')
                chapter_info = content_dict.get('chapter_info', {})
                url = content_dict.get('url', '')
                word_count = content_dict.get('word_count', 0)
            
                # 合并文本内容
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                full_content = f"# 浏览器内容提取 ({timestamp})\n\n"
                full_content += f"**标题**: {title}\n"
                full_content += f"**来源**: {url}\n"
                if word_count:
                    full_content += f"**字数统计**: 约{word_count}字\n"
                full_content += f"**提取方式**: 网页文本提取\n\n"
                
                if chapter_info:
                    full_content += f"## 章节信息\n"
                    if isinstance(chapter_info, dict):
                        for key, value in chapter_info.items():
                            full_content += f"- {key}: {value}\n"
                    else:
                        full_content += f"{chapter_info}\n"
                    full_content += "\n"
                    
                full_content += "=" * 40 + "\n\n"  # 添加分隔线
                full_content += text_content
                
                # 添加图片信息
                if images:
                    full_content += "\n\n" + "=" * 40 + "\n## 图片信息:\n"
                    for i, img in enumerate(images, 1):
                        img_url = img.get('url', '未知')
                        img_alt = img.get('alt', '')
                        img_title = img.get('title', '')
                        full_content += f"\n### 图片 {i}:\n"
                        full_content += f"- URL: {img_url}\n"
                        if img_alt:
                            full_content += f"- 描述: {img_alt}\n"
                        if img_title:
                            full_content += f"- 标题: {img_title}\n"
            # 处理内容过长的情况
            if len(full_content) > MAX_CONTENT_LENGTH:
                full_content = full_content[:MAX_CONTENT_LENGTH-5000] + "\n\n...(内容过长，已截断)...\n\n" + "建议分段处理或保存到文件"

            # 在文本输入区域显示内容
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(tk.END, full_content)

            # 切换到文本输入选项卡
            self.notebook.select(0)

            # 更新状态栏
            self.status_var.set(f"已从浏览器提取内容: {title if title else '未知标题'}")

            # 询问用户是否进行AI总结
            self.ask_for_ai_summary()
        except Exception as e:
            print(f"处理浏览器内容时出错: {e}")
            messagebox.showerror("错误", f"处理内容时出错: {str(e)}")
            self.status_var.set("内容处理失败")
        
    def get_browser_url(self):
        """获取当前浏览器URL"""
        try:
            if hasattr(self, 'browser_window'):
                return self.browser_window.get_current_url()
            return "未知URL"
        except:
            return "未知URL"
            
    def get_browser_title(self):
        """获取当前浏览器标题"""
        try:
            if hasattr(self, 'browser_window'):
                return self.browser_window.get_current_title()
            return "未知标题"
        except:
            return "未知标题"

    def ask_for_ai_summary(self):
        """询问用户是否进行AI总结"""
        answer = messagebox.askyesno("AI总结", "是否对提取的内容进行AI总结？\n\n注意：较长内容可能会被分段处理。")
        if answer:
            self.summarize_text()

    def preprocess_content(self, content):
        """预处理提取的内容"""
        # 移除多余的空行
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 如果内容过长，进行分段处理
        if len(content) > MAX_SEGMENT_LENGTH:
            segments = []
            current_segment = ""
            for line in content.split('\n'):
                if len(current_segment) + len(line) > MAX_SEGMENT_LENGTH:
                    segments.append(current_segment)
                    current_segment = line + "\n"
                else:
                    current_segment += line + "\n"
            if current_segment:
                segments.append(current_segment)
            return segments
        else:
            return [content]

    def summarize_text(self):
        """AI总结文本"""
        text_to_summarize = self.text_input.get(1.0, tk.END).strip()
        
        if not text_to_summarize:
            messagebox.showwarning("警告", "没有可总结的文本内容")
            return
        
        if not JIEBA_AVAILABLE:
            # 如果没有jieba，使用基础分析
            self.basic_analysis(text_to_summarize)
            return
            
        self.status_var.set("正在进行AI总结，请稍候...")
        
        # 使用线程安全的方式处理
        # 如果文本较长，分段处理
        if len(text_to_summarize) > MAX_SEGMENT_LENGTH:
            # 直接在主线程中预处理，避免多线程问题
            segments = self.preprocess_content(text_to_summarize)
            if len(segments) > 1:
                self.status_var.set(f"文本较长，分为 {len(segments)} 部分处理...")
            
            # 安全启动线程
            thread = threading.Thread(target=self.run_summarize, args=(segments,), daemon=True)
            thread.start()
        else:
            # 短文本直接处理
            thread = threading.Thread(target=self.run_summarize, args=(text_to_summarize,), daemon=True)
            thread.start()

    # 删除重复定义，因为已经在上面合并了功能
    
    # ==================== 浏览器地址栏交互方法 ====================
    
    def update_address_bar_state(self):
        """更新地址栏按钮状态"""
        if BROWSER_AVAILABLE and self.browser_window:
            try:
                # 启用所有按钮
                self.go_btn.configure(state=tk.NORMAL)
                self.refresh_btn.configure(state=tk.NORMAL)
                self.extract_btn.configure(state=tk.NORMAL)
                self.ocr_btn.configure(state=tk.NORMAL)
                
                # 根据历史记录状态更新前进后退按钮
                if hasattr(self.browser_window, 'web_view'):
                    history = self.browser_window.web_view.page().history()
                    self.back_btn.configure(state=tk.NORMAL if history.canGoBack() else tk.DISABLED)
                    self.forward_btn.configure(state=tk.NORMAL if history.canGoForward() else tk.DISABLED)
            except Exception as e:
                log_error(e)
                print(f"更新地址栏状态失败: {str(e)}")
        else:
            # 禁用所有按钮
            self.back_btn.configure(state=tk.DISABLED)
            self.forward_btn.configure(state=tk.DISABLED)
            self.refresh_btn.configure(state=tk.DISABLED)
            self.go_btn.configure(state=tk.DISABLED)
            self.extract_btn.configure(state=tk.DISABLED)
            self.ocr_btn.configure(state=tk.DISABLED)
    
    def on_address_enter(self, event):
        """地址栏回车事件"""
        self.navigate_to_address()
    
    def navigate_to_address(self):
        """导航到地址栏指定的URL"""
        if not BROWSER_AVAILABLE or not self.browser_window:
            messagebox.showwarning("警告", "浏览器未初始化")
            return
        
        url_text = self.address_var.get().strip()
        if not url_text:
            messagebox.showwarning("警告", "请输入网址")
            return
        
        try:
            # 如果不是完整URL，添加协议
            if not url_text.startswith(('http://', 'https://')):
                # 检查是否像是域名
                if '.' in url_text and ' ' not in url_text:
                    url_text = 'https://' + url_text
                else:
                    # 否则当作搜索内容
                    url_text = SEARCH_ENGINE_URL.format(urllib.parse.quote(url_text))
            
            # 加载URL
            self.browser_window.load_url(url_text)
            if hasattr(self, 'status_var'):
                self.status_var.set(f"正在加载: {url_text}")
            else:
                print(f"正在加载: {url_text}")
            
            # 更新按钮状态
            self.update_address_bar_state()
            
        except Exception as e:
            log_error(e)
            messagebox.showerror("错误", f"加载网址失败: {str(e)}")
    
    def browser_back(self):
        """浏览器后退"""
        if BROWSER_AVAILABLE and self.browser_window:
            try:
                self.browser_window.web_view.back()
                self.update_address_bar_state()
            except Exception as e:
                log_error(e)
                messagebox.showerror("错误", f"后退失败: {str(e)}")
    
    def browser_forward(self):
        """浏览器前进"""
        if BROWSER_AVAILABLE and self.browser_window:
            try:
                self.browser_window.web_view.forward()
                self.update_address_bar_state()
            except Exception as e:
                log_error(e)
                messagebox.showerror("错误", f"前进失败: {str(e)}")
    
    def browser_refresh(self):
        """刷新浏览器"""
        if BROWSER_AVAILABLE and self.browser_window:
            try:
                self.browser_window.web_view.reload()
                self.status_var.set("正在刷新页面...")
            except Exception as e:
                log_error(e)
                messagebox.showerror("错误", f"刷新失败: {str(e)}")
    
    def extract_browser_content(self):
        """提取浏览器当前页面内容"""
        if not BROWSER_AVAILABLE or not self.browser_window:
            messagebox.showwarning("警告", "浏览器未初始化")
            return
        
        try:
            # 调用浏览器的提取内容方法
            self.browser_window.extract_page_content()
            self.status_var.set("正在提取网页内容...")
        except Exception as e:
            log_error(e)
            messagebox.showerror("错误", f"提取内容失败: {str(e)}")
    
    def extract_browser_images(self):
        """提取并识别浏览器页面中的图片"""
        if not BROWSER_AVAILABLE or not self.browser_window:
            messagebox.showwarning("警告", "浏览器未初始化")
            return
        
        try:
            # 调用浏览器的图片识别方法
            self.browser_window.extract_and_ocr_images()
            self.status_var.set("正在识别页面图片...")
        except Exception as e:
            log_error(e)
            messagebox.showerror("错误", f"图片识别失败: {str(e)}")
    
    def on_browser_url_changed(self, qurl):
        """浏览器URL变化时更新地址栏"""
        try:
            url_string = qurl.toString()
            self.address_var.set(url_string)
            self.update_address_bar_state()
        except Exception as e:
            log_error(e)
            print(f"更新地址栏失败: {str(e)}")

def main():
    """主函数"""
    root = tk.Tk()
    app = NovelReaderMain(root)
    
    def process_queue():
        try:
            root.after(100, process_queue)  # 设置下一次检查
            while not task_queue.empty():
                task, args = task_queue.get_nowait()
                root.after_idle(task, *args)
        except queue.Empty:
            pass

    root.after(100, process_queue)  # 开始队列处理
    root.mainloop()

if __name__ == "__main__":
    main()