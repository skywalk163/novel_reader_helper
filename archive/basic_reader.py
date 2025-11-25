#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 基础版
简单的文本分析和总结功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
from datetime import datetime

class BasicNovelReader:
    def __init__(self, root):
        self.root = root
        self.root.title("小说阅读神器 - 基础版")
        self.root.geometry("900x600")
        
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
        title_label = ttk.Label(main_frame, text="小说阅读神器 - 基础版", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 按钮
        ttk.Button(control_frame, text="📂 打开文本文件", 
                  command=self.open_text_file, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="📊 简单分析", 
                  command=self.analyze_text, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="💾 保存结果", 
                  command=self.save_results, width=20).pack(pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="??️ 清空内容", 
                  command=self.clear_all, width=20).pack(pady=5, fill=tk.X)
        
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
        self.text_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=12)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 结果区域
        result_frame = ttk.LabelFrame(work_frame, text="📝 分析结果", padding="5")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 总结结果文本区
        self.summary_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=12)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
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
                self.status_var.set(f"已加载文件: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
    
    def analyze_text(self):
        """简单分析文本"""
        text = self.text_input.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("警告", "没有可分析的文本内容")
            return
        
        # 进行简单分析
        result = self.simple_analysis(text)
        
        # 更新结果显示
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, result)
        
        self.status_var.set("文本分析完成")
    
    def simple_analysis(self, text):
        """进行简单的文本分析"""
        # 基础统计
        char_count = len(text)
        lines = text.count('\n') + 1
        words = len(re.findall(r'\b\w+\b', text))
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 预计阅读时间（按照每分钟阅读500个字符计算）
        reading_time = char_count / 500
        
        # 提取段落
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 尝试提取章节标题
        chapter_title = ""
        first_line = text.split('\n')[0].strip()
        if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
            chapter_title = first_line
        
        # 提取前几句话和最后几句话
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        first_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        last_sentences = sentences[-3:] if len(sentences) >= 3 else []
        
        # 组装结果
        result = []
        if chapter_title:
            result.append(f"# {chapter_title}\n")
        else:
            result.append("# 文章分析\n")
        
        result.append("## 基本统计")
        result.append(f"- 总字符数: {char_count} 字符")
        result.append(f"- 中文字符数: {chinese_chars} 个汉字")
        result.append(f"- 单词数: {words} 个")
        result.append(f"- 行数: {lines} 行")
        result.append(f"- 段落数: {len(paragraphs)} 段")
        result.append(f"- 估计阅读时间: {int(reading_time)} 分钟 {int((reading_time % 1) * 60)} 秒")
        result.append("")
        
        result.append("## 内容概要")
        result.append("### 开始部分:")
        for s in first_sentences:
            result.append(f"- {s}")
        
        if last_sentences and last_sentences != first_sentences:
            result.append("\n### 结束部分:")
            for s in last_sentences:
                result.append(f"- {s}")
        
        return '\n'.join(result)
    
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
        self.status_var.set("已清空所有内容")

def main():
    """主函数"""
    root = tk.Tk()
    app = BasicNovelReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()