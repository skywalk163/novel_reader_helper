#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 修复版
重点实现文本总结功能，不依赖复杂OCR库
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import jieba
import jieba.analyse
import threading
import math
from datetime import datetime

class NovelReaderHelperSimple:
    def __init__(self, root):
        self.root = root
        self.root.title("小说阅读神器 v1.0 (简化版)")
        self.root.geometry("900x700")
        
        # 创建界面
        self.setup_ui()
        
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
        title_label = ttk.Label(main_frame, text="小说阅读神器 (简化版)", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 按钮
        ttk.Button(control_frame, text="?? 输入文本内容", 
                  command=self.input_text_mode, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📂 打开文本文件", 
                  command=self.open_text_file, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📝 AI总结", 
                  command=self.summarize_text, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="💾 保存结果", 
                  command=self.save_results, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="🗑️ 清空内容", 
                  command=self.clear_all, width=20).pack(pady=5, fill=tk.X)
        
        # 添加分隔线
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 添加抽取关键词部分
        ttk.Label(control_frame, text="提取关键词数量:").pack(pady=(10, 0), fill=tk.X)
        self.keyword_num = tk.IntVar(value=8)
        keywords_spin = ttk.Spinbox(control_frame, from_=3, to=20, textvariable=self.keyword_num, width=5)
        keywords_spin.pack(pady=(0, 10), fill=tk.X)
        
        # 添加总结长度
        ttk.Label(control_frame, text="摘要句子数量:").pack(pady=(10, 0), fill=tk.X)
        self.summary_num = tk.IntVar(value=5)
        summary_spin = ttk.Spinbox(control_frame, from_=2, to=10, textvariable=self.summary_num, width=5)
        summary_spin.pack(pady=(0, 10), fill=tk.X)
        
        # 右侧主工作区
        work_frame = ttk.Frame(main_frame)
        work_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        work_frame.columnconfigure(0, weight=1)
        work_frame.rowconfigure(0, weight=1)
        work_frame.rowconfigure(1, weight=1)
        
        # 创建上下分隔的工作区
        input_frame = ttk.LabelFrame(work_frame, text="📄 输入文本", padding="5")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        # 输入文本区域
        self.text_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=15)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 结果区域
        result_frame = ttk.LabelFrame(work_frame, text="📝 总结结果", padding="5")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 总结结果文本区
        self.summary_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def input_text_mode(self):
        """文本输入模式"""
        self.text_input.focus()
        self.status_var.set("请在文本框中输入要总结的内容")
    
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
                self.status_var.set(f"已加载文件: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
                
    def summarize_text(self):
        """AI总结文本"""
        text_to_summarize = self.text_input.get(1.0, tk.END).strip()
        
        if not text_to_summarize:
            messagebox.showwarning("警告", "没有可总结的文本内容")
            return
            
        self.status_var.set("正在进行AI总结，请稍候...")
        
        # 使用线程避免界面卡顿
        threading.Thread(target=self.run_summarize, args=(text_to_summarize,), daemon=True).start()
    
    def run_summarize(self, text):
        """在线程中运行总结功能"""
        try:
            result = self.analyze_chapter(text)
            summary = self.format_chapter_summary(result)
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self.update_summary_result(summary))
        except Exception as e:
            error_msg = f"总结失败: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            self.root.after(0, lambda: self.status_var.set("总结失败"))
    
    def update_summary_result(self, summary):
        """更新AI总结结果"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.status_var.set("AI总结完成")
    
    def extract_keywords(self, text, topK=8):
        """提取关键词"""
        keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
        return keywords
    
    def get_important_sentences(self, text, topK=5):
        """获取最重要的几个句子"""
        # 使用更安全的方式处理正则表达式 - 完全修复了语法问题
        
        # 第一步：在标点符号后添加换行
        text = re.sub(r'([。！？\?])([^"\'"])', r'\1\n\2', text)
        
        # 第二步：处理省略号
        text = re.sub(r'(\.{6})([^"\'"])', r'\1\n\2', text)
        
        # 第三步：处理另一种省略号
        text = re.sub(r'(\…{2})([^"\'"])', r'\1\n\2', text)
        
        # 第四步：处理引号后的标点
        text = re.sub(r'([。！？\?]["\'"])([^，。！？\?])', r'\1\n\2', text)
        
        # 分割文本为句子
        sentences = text.split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= topK:
            return sentences
        
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
            
            # 考虑句子位置因素
            position_weight = 1.0
            if i < len(sentences) * 0.1 or i > len(sentences) * 0.9:
                position_weight = 1.2
            
            score = score * position_weight
            sentence_scores.append((i, sentence, score))
        
        # 按得分排序
        sentence_scores.sort(key=lambda x: x[2], reverse=True)
        
        # 取出得分最高的topK个句子，并按原文顺序排列
        top_sentences = sentence_scores[:topK]
        top_sentences.sort(key=lambda x: x[0])
        
        return [s[1] for s in top_sentences]
    
    def analyze_chapter(self, chapter_text, chapter_title=""):
        """分析小说章节"""
        # 检测章节标题
        if not chapter_title and len(chapter_text) > 0:
            # 尝试从文本开头提取章节标题
            first_line = chapter_text.split('\n')[0].strip()
            if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
                chapter_title = first_line
        
        # 基本统计
        char_count = len(chapter_text)
        
        # 从UI获取参数
        keyword_num = self.keyword_num.get()
        summary_num = self.summary_num.get()
        
        # 提取关键词
        keywords = self.extract_keywords(chapter_text, topK=keyword_num)
        keyword_list = [word for word, _ in keywords]
        
        # 提取重要句子
        important_sentences = self.get_important_sentences(chapter_text, topK=summary_num)
        
        # 组装结果
        result = {
            "title": chapter_title,
            "char_count": char_count,
            "word_count": char_count // 2,  # 汉字近似计算
            "keywords": keyword_list,
            "important_sentences": important_sentences
        }
        
        return result
        
    def format_chapter_summary(self, chapter_analysis):
        """格式化章节总结为易读的形式"""
        result = []
        
        # 添加标题
        if chapter_analysis["title"]:
            result.append(f"# {chapter_analysis['title']}")
        else:
            result.append("# 章节概要")
            
        result.append("")
        
        # 添加统计信息
        result.append(f"📊 字数统计：约 {chapter_analysis['char_count']} 字")
        result.append(f"⏱️ 阅读时间：约 {math.ceil(chapter_analysis['char_count'] / 500)} 分钟")
        result.append("")
        
        # 添加关键词
        result.append("🔑 关键词：")
        result.append("  " + "、".join(chapter_analysis["keywords"]))
        result.append("")
        
        # 添加重要句子
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
                    f.write("小说阅读神器 - 总结结果\n")
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
        self.status_var.set("已清空所有内容")

def main():
    """主函数"""
    root = tk.Tk()
    app = NovelReaderHelperSimple(root)
    root.mainloop()

if __name__ == "__main__":
    main()