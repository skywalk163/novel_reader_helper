#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - AI总结模块
提供多种方式对文本进行智能总结
"""

import re
import math
import jieba
import jieba.analyse
from collections import defaultdict

class TextSummarizer:
    """文本总结类，提供多种总结方法"""
    
    def __init__(self):
        """初始化"""
        # 加载jieba自定义词典
        try:
            jieba.load_userdict("novel_dict.txt")
        except:
            print("未找到自定义词典")
    
    def extract_keywords(self, text, topK=10):
        """提取关键词"""
        keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
        return keywords
    
    def get_important_sentences(self, text, topK=3):
        """获取最重要的几个句子"""
        # 分句
        text = re.sub(r'([。！？\?])([^"'])', r'\1\n\2', text)
        text = re.sub(r'(\.{6})([^"'])', r'\1\n\2', text)
        text = re.sub(r'(\…{2})([^"'])', r'\1\n\2', text)
        text = re.sub(r'([。！？\?]["'])([^，。！？\?])', r'\1\n\2', text)
        
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
            # 开头和结尾的句子权重略高
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
    
    def summarize(self, text, max_ratio=0.3, max_sentences=5):
        """总结文本"""
        # 1. 文本预处理
        text = text.replace("\n\n", "\n").strip()
        
        # 如果文本很短，直接返回
        if len(text) < 200:
            return {"summary": text, "keywords": [], "ratio": 1.0}
        
        # 2. 提取关键词
        keywords = self.extract_keywords(text, topK=8)
        keyword_list = [word for word, _ in keywords]
        
        # 3. 提取重要句子
        max_num_sentences = min(max_sentences, int(len(text) / 100))
        if max_num_sentences < 3:
            max_num_sentences = 3
            
        important_sentences = self.get_important_sentences(text, topK=max_num_sentences)
        
        # 4. 生成总结
        summary = "【内容概要】\n\n"
        summary += "◆ 关键词：" + "、".join(keyword_list) + "\n\n"
        summary += "◆ 重要内容：\n"
        summary += "\n".join(["· " + s for s in important_sentences])
        summary += "\n\n"
        
        # 计算压缩比
        ratio = len(summary) / len(text)
        summary_info = {
            "summary": summary,
            "keywords": keyword_list,
            "important_sentences": important_sentences,
            "ratio": ratio
        }
        
        return summary_info

    def chapter_analysis(self, chapter_text, chapter_title=""):
        """分析小说章节"""
        # 检测章节标题
        if not chapter_title and len(chapter_text) > 0:
            # 尝试从文本开头提取章节标题
            first_line = chapter_text.split('\n')[0].strip()
            if len(first_line) < 30 and ('章' in first_line or '节' in first_line):
                chapter_title = first_line
        
        # 基本统计
        char_count = len(chapter_text)
        
        # 总结文本
        summary_info = self.summarize(chapter_text)
        
        # 组装结果
        result = {
            "title": chapter_title,
            "char_count": char_count,
            "word_count": char_count // 2,  # 汉字近似计算
            "summary": summary_info["summary"],
            "keywords": summary_info["keywords"],
            "compression_ratio": summary_info["ratio"]
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
        
        # 添加总结内容
        result.append(chapter_analysis["summary"])
        
        return "\n".join(result)

if __name__ == "__main__":
    # 简单测试
    sample_text = """
    张无忌自从学会了乾坤大挪移和太极拳，武功大进，现在终于可以为父母报仇了。
    他来到了光明顶，看到了阳顶天留下的七个字"光明正大，洗刷污垢"，心中感慨万千。
    这时，赵敏带着一群蒙古兵闯了进来，张无忌立即迎上前去，二人战在一处。
    赵敏出招狠辣，张无忌则招招相让，不愿伤她。
    战了几十招，张无忌以乾坤大挪移化解了赵敏的招式，并点中了她的穴道。
    "张教主，你为何不杀我？"赵敏问道。
    张无忌叹了口气："我与姑娘无冤无仇，又怎会取你性命？"
    赵敏心中感动，从此对张无忌芳心暗许。
    """
    
    summarizer = TextSummarizer()
    analysis = summarizer.chapter_analysis(sample_text, "第二十章 光明顶之战")
    print(summarizer.format_chapter_summary(analysis))