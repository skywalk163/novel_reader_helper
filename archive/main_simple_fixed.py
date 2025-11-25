#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 稳定版
专注于核心功能，避免复杂依赖冲突
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
import logging

# 设置日志
logging.basicConfig(filename='novel_reader.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(e):
    logging.error(f"An error occurred: {str(e)}")
    print(f"错误: {e}")

# 可选依赖检查
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

# PaddleOCR 服务配置
OCR_SERVICE_URL = "http://127.0.0.1:5000"

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
        self.root = root
        self.root.title("小说阅读神器 - 稳定版")
        self.root.geometry("1000x700")
        
        # 状态变量
        self.current_image = None
        self.current_image_path = None
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        
        # 创建界面
        self.setup_ui()
        
        # 添加窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """窗口关闭事件处理"""
        self.root.destroy()

    def setup_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="小说阅读神器 - 稳定版", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 功能按钮
        ttk.Button(control_frame, text="📂 打开文本文件", 
                  command=self.open_text_file, width=20).pack(pady=5, fill=tk.X)
        
        if PIL_AVAILABLE:
            ttk.Button(control_frame, text="🖼️ 打开图片文件", 
                      command=self.open_image_file, width=20).pack(pady=5, fill=tk.X)
            
            ttk.Button(control_frame, text="📷 OCR识别图片", 
                      command=self.perform_ocr, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📝 AI总结",
                  command=self.summarize_text, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="💾 保存结果", 
                  command=self.save_results, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="🗑️ 清空内容", 
                  command=self.clear_all, width=20).pack(pady=5, fill=tk.X)
        
        # 添加分隔线
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 配置选项
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
        status_text.append(f"{'✅' if PIL_AVAILABLE else '❌'} 图片预览")
        status_text.append(f"{'✅' if OCR_AVAILABLE else '❌'} OCR识别")
        status_text.append(f"{'✅' if JIEBA_AVAILABLE else '❌'} 智能分析")
        
        for text in status_text:
            ttk.Label(control_frame, text=text, font=("Arial", 9)).pack(fill=tk.X)
        
        # 右侧主工作区
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        
        # 状态栏
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

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
                self.notebook.select(0)
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
                
                # 调整图片大小
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()
                
                if canvas_width < 100:
                    canvas_width, canvas_height = 800, 600
                
                img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
                
                self.current_image = ImageTk.PhotoImage(img)
                
                # 显示图片
                self.image_canvas.delete("all")
                self.image_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.current_image, anchor=tk.CENTER
                )
                
                self.notebook.select(1)
                self.status_var.set(f"已加载图片: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败: {str(e)}")

    def ocr_image(self, image_path=None):
        """OCR识别图片"""
        if not OCR_AVAILABLE:
            return "OCR服务不可用，请检查PaddleOCR服务是否正常运行。"
        
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

    def perform_ocr(self):
        """执行OCR识别"""
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先加载图片")
            return
        
        if not OCR_AVAILABLE:
            messagebox.showwarning("警告", "OCR服务不可用")
            return
        
        self.status_var.set("正在进行OCR识别...")
        
        try:
            ocr_result = self.ocr_image(self.current_image_path)
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(tk.END, ocr_result)
            self.notebook.select(0)
            self.status_var.set("OCR识别完成")
        except Exception as e:
            self.status_var.set("OCR识别失败")
            messagebox.showerror("错误", f"OCR识别失败: {str(e)}")

    def summarize_text(self):
        """AI总结文本"""
        text_to_summarize = self.text_input.get(1.0, tk.END).strip()
        
        if not text_to_summarize:
            messagebox.showwarning("警告", "没有可总结的文本内容")
            return
        
        if not JIEBA_AVAILABLE:
            self.basic_analysis(text_to_summarize)
            return
        
        self.status_var.set("正在进行AI总结...")
        
        try:
            result = self.analyze_chapter(text_to_summarize)
            summary = self.format_chapter_summary(result)
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary)
            self.notebook.select(2)
            self.status_var.set("AI总结完成")
            
        except Exception as e:
            self.status_var.set("总结失败")
            messagebox.showerror("错误", f"总结失败: {str(e)}")

    def basic_analysis(self, text):
        """基础文本分析"""
        char_count = len(text)
        lines = text.count('\n') + 1
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        reading_time = char_count / 500
        
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        first_line = text.split('\n')[0].strip()
        chapter_title = ""
        if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
            chapter_title = first_line
        
        first_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        
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
        result.append(f"- 预计阅读时间: {int(reading_time)} 分钟")
        result.append("")
        
        result.append("## 内容开头:")
        for s in first_sentences:
            result.append(f"- {s}")
        
        result.append("\n\n💡 提示: 安装 jieba 库可获得更智能的分析功能")
        
        summary = '\n'.join(result)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.notebook.select(2)
        self.status_var.set("基础分析完成")

    def extract_keywords(self, text, topK=8):
        """提取关键词"""
        if not JIEBA_AVAILABLE:
            return []
        keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
        return keywords

    def get_important_sentences(self, text, topK=5):
        """获取重要句子"""
        text = re.sub(r'([。！？\?])([^"\'"])', r'\1\n\2', text)
        sentences = text.split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= topK:
            return sentences
        
        if not JIEBA_AVAILABLE:
            return sentences[:topK]
        
        # 关键词权重
        keywords_dict = {}
        keywords = self.extract_keywords(text, topK=20)
        for word, weight in keywords:
            keywords_dict[word] = weight
        
        # 句子评分
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0
            for word in jieba.cut(sentence):
                if word in keywords_dict:
                    score += keywords_dict[word]
            
            # 位置权重
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
        """分析章节"""
        if not chapter_title:
            first_line = chapter_text.split('\n')[0].strip()
            if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
                chapter_title = first_line
        
        char_count = len(chapter_text)
        
        keyword_num = self.keyword_num.get() if JIEBA_AVAILABLE else 0
        summary_num = self.summary_num.get() if JIEBA_AVAILABLE else 5
        
        keywords = self.extract_keywords(chapter_text, topK=keyword_num)
        keyword_list = [word for word, _ in keywords]
        
        important_sentences = self.get_important_sentences(chapter_text, topK=summary_num)
        
        return {
            "title": chapter_title,
            "char_count": char_count,
            "word_count": char_count // 2,
            "keywords": keyword_list,
            "important_sentences": important_sentences
        }

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

def main():
    """主函数"""
    root = tk.Tk()
    app = NovelReaderMain(root)
    root.mainloop()

if __name__ == "__main__":
    main()