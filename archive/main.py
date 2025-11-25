#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 主程序
支持文字识别和AI总结功能，帮助快速浏览小说内容
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import paddleocr
import threading
import queue
import json
import requests
from datetime import datetime

class NovelReaderHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("小说阅读神器 v1.0")
        self.root.geometry("1000x700")
        
        # 初始化OCR引擎
        self.ocr = None
        self.init_ocr()
        
        # 创建界面
        self.setup_ui()
        
        # 状态变量
        self.current_image = None
        self.extracted_text = ""
        
    def init_ocr(self):
        """初始化PaddleOCR"""
        try:
            print("正在初始化PaddleOCR...")
            self.ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            print("PaddleOCR初始化完成")
        except Exception as e:
            messagebox.showerror("错误", f"PaddleOCR初始化失败: {str(e)}")
            
    def setup_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="小说阅读神器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 按钮
        ttk.Button(control_frame, text="📁 选择图片文件", 
                  command=self.select_image_file, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📄 输入文本内容", 
                  command=self.input_text_mode, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="🔍 文字识别", 
                  command=self.extract_text, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📝 AI总结", 
                  command=self.summarize_text, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="💾 保存结果", 
                  command=self.save_results, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="🗑️ 清空内容", 
                  command=self.clear_all, width=20).pack(pady=5, fill=tk.X)
        
        # 设置按钮
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Button(control_frame, text="⚙️ 设置", 
                  command=self.open_settings, width=20).pack(pady=5, fill=tk.X)
        
        # 右侧主工作区
        work_frame = ttk.Frame(main_frame)
        work_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        work_frame.columnconfigure(0, weight=1)
        work_frame.rowconfigure(1, weight=1)
        
        # 创建Notebook（选项卡）
        self.notebook = ttk.Notebook(work_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 图片预览选项卡
        self.image_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.image_frame, text="📷 图片预览")
        
        # 图片显示区域
        self.image_canvas = tk.Canvas(self.image_frame, bg="white", width=400, height=300)
        self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文本输入选项卡
        self.text_input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.text_input_frame, text="📝 文本输入")
        
        # 文本输入区域
        self.text_input = scrolledtext.ScrolledText(self.text_input_frame, wrap=tk.WORD, height=15)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 下方结果显示区域
        result_frame = ttk.LabelFrame(work_frame, text="处理结果", padding="5")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建结果选项卡
        self.result_notebook = ttk.Notebook(result_frame)
        self.result_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 识别结果选项卡
        self.ocr_result_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.ocr_result_frame, text="🔍 识别结果")
        
        self.ocr_text = scrolledtext.ScrolledText(self.ocr_result_frame, wrap=tk.WORD, height=8)
        self.ocr_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # AI总结选项卡
        self.summary_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.summary_frame, text="📋 AI总结")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, wrap=tk.WORD, height=8)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def select_image_file(self):
        """选择图片文件"""
        file_types = [
            ('图片文件', '*.png *.jpg *.jpeg *.bmp *.tiff *.gif'),
            ('所有文件', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if filename:
            self.load_image(filename)
            
    def load_image(self, filepath):
        """加载并显示图片"""
        try:
            # 打开图片
            image = Image.open(filepath)
            self.current_image = filepath
            
            # 调整图片大小以适应画布
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 400, 300
            
            # 计算缩放比例
            img_width, img_height = image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整图片大小
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.photo = ImageTk.PhotoImage(image)
            
            # 清空画布并显示图片
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                canvas_width//2, canvas_height//2, 
                image=self.photo, anchor=tk.CENTER
            )
            
            # 切换到图片预览选项卡
            self.notebook.select(self.image_frame)
            
            self.status_var.set(f"已加载图片: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {str(e)}")
            
    def input_text_mode(self):
        """切换到文本输入模式"""
        self.notebook.select(self.text_input_frame)
        self.text_input.focus()
        self.status_var.set("请在文本框中输入要总结的内容")
        
    def extract_text(self):
        """提取文字"""
        if self.current_image:
            self.extract_text_from_image()
        else:
            # 从文本输入框获取文本
            text = self.text_input.get(1.0, tk.END).strip()
            if text:
                self.extracted_text = text
                self.ocr_text.delete(1.0, tk.END)
                self.ocr_text.insert(1.0, text)
                self.result_notebook.select(self.ocr_result_frame)
                self.status_var.set("文本内容已准备就绪")
            else:
                messagebox.showwarning("警告", "请先选择图片或输入文本内容")
                
    def extract_text_from_image(self):
        """从图片中提取文字"""
        if not self.ocr:
            messagebox.showerror("错误", "OCR引擎未初始化")
            return
            
        if not self.current_image:
            messagebox.showwarning("警告", "请先选择图片文件")
            return
            
        # 在新线程中执行OCR，避免界面卡顿
        self.status_var.set("正在进行文字识别，请稍候...")
        
        def ocr_thread():
            try:
                result = self.ocr.ocr(self.current_image, cls=True)
                
                # 提取文本
                text_lines = []
                if result and result[0]:
                    for line in result[0]:
                        if len(line) >= 2:
                            text_lines.append(line[1][0])
                
                extracted_text = '\n'.join(text_lines)
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_ocr_result(extracted_text))
                
            except Exception as e:
                error_msg = f"文字识别失败: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
                self.root.after(0, lambda: self.status_var.set("识别失败"))
        
        threading.Thread(target=ocr_thread, daemon=True).start()
        
    def update_ocr_result(self, text):
        """更新OCR识别结果"""
        self.extracted_text = text
        self.ocr_text.delete(1.0, tk.END)
        self.ocr_text.insert(1.0, text)
        self.result_notebook.select(self.ocr_result_frame)
        self.status_var.set(f"文字识别完成，共识别 {len(text)} 个字符")
        
    def summarize_text(self):
        """AI总结文本"""
        text_to_summarize = self.extracted_text
        
        if not text_to_summarize:
            # 尝试从OCR结果获取文本
            text_to_summarize = self.ocr_text.get(1.0, tk.END).strip()
        
        if not text_to_summarize:
            messagebox.showwarning("警告", "没有可总结的文本内容")
            return
            
        self.status_var.set("正在进行AI总结，请稍候...")
        
        def summarize_thread():
            try:
                summary = self.ai_summarize(text_to_summarize)
                self.root.after(0, lambda: self.update_summary_result(summary))
            except Exception as e:
                error_msg = f"AI总结失败: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
                self.root.after(0, lambda: self.status_var.set("总结失败"))
        
        threading.Thread(target=summarize_thread, daemon=True).start()
        
    def ai_summarize(self, text):
        """AI总结功能 - 这里可以集成各种AI服务"""
        # 简单的基于规则的总结（可以替换为真正的AI服务）
        sentences = text.replace('。', '。\n').split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return text
        
        # 简单的摘要：取前面几句和最后几句
        summary_lines = []
        summary_lines.append("📖 内容概要：")
        summary_lines.append("")
        
        # 如果文本很长，进行简单的总结
        if len(text) > 500:
            summary_lines.append(f"📊 原文长度：{len(text)} 字符")
            summary_lines.append(f"📄 段落数量：{len(sentences)} 句")
            summary_lines.append("")
            summary_lines.append("🔍 开头内容：")
            summary_lines.extend(sentences[:2])
            summary_lines.append("")
            if len(sentences) > 4:
                summary_lines.append("🔍 结尾内容：")
                summary_lines.extend(sentences[-2:])
        else:
            summary_lines.append("📝 原文较短，建议直接阅读：")
            summary_lines.append(text)
        
        return '\n'.join(summary_lines)
        
    def update_summary_result(self, summary):
        """更新AI总结结果"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.result_notebook.select(self.summary_frame)
        self.status_var.set("AI总结完成")
        
    def save_results(self):
        """保存结果"""
        if not self.extracted_text and not self.summary_text.get(1.0, tk.END).strip():
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
                    f.write("小说阅读神器 - 处理结果\n")
                    f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    if self.extracted_text:
                        f.write("🔍 文字识别结果:\n")
                        f.write("-" * 30 + "\n")
                        f.write(self.extracted_text)
                        f.write("\n\n")
                    
                    summary = self.summary_text.get(1.0, tk.END).strip()
                    if summary:
                        f.write("📋 AI总结结果:\n")
                        f.write("-" * 30 + "\n")
                        f.write(summary)
                        f.write("\n")
                
                messagebox.showinfo("成功", f"结果已保存到: {filename}")
                self.status_var.set(f"结果已保存: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
                
    def clear_all(self):
        """清空所有内容"""
        self.current_image = None
        self.extracted_text = ""
        self.image_canvas.delete("all")
        self.text_input.delete(1.0, tk.END)
        self.ocr_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.status_var.set("已清空所有内容")
        
    def open_settings(self):
        """打开设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="设置选项", font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Label(settings_window, text="AI总结服务配置:").pack(pady=5)
        ttk.Label(settings_window, text="(未来版本将支持更多AI服务)").pack(pady=5)
        
        ttk.Button(settings_window, text="关闭", 
                  command=settings_window.destroy).pack(pady=20)

def main():
    """主函数"""
    root = tk.Tk()
    app = NovelReaderHelper(root)
    root.mainloop()

if __name__ == "__main__":
    main()