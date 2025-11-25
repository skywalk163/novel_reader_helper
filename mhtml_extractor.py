#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTML文件内容提取器
用于从MHTML格式的离线网页中提取小说内容
"""

import os
import re
import email
import binascii
from bs4 import BeautifulSoup
from urllib.parse import unquote
import base64
import quopri

class MHTMLExtractor:
    """MHTML文件内容提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.debug_mode = False
    
    def set_debug(self, debug_mode=False):
        """设置调试模式"""
        self.debug_mode = debug_mode
    
    def log(self, message):
        """打印日志信息"""
        if self.debug_mode:
            print(f"[MHTML提取] {message}")
    
    def extract_content(self, file_path):
        """从MHTML文件中提取内容"""
        self.log(f"正在处理文件: {file_path}")
        
        if not os.path.exists(file_path):
            self.log(f"文件不存在: {file_path}")
            return None
            
        try:
            # 使用email库处理MHTML文件（因为MHTML是基于MIME标准的）
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                mhtml_content = file.read()
            
            self.log(f"成功读取文件，内容长度: {len(mhtml_content)} 字符")
            
            # 尝试解析为email/MIME消息
            try:
                msg = email.message_from_string(mhtml_content)
                self.log("成功解析MHTML为MIME消息")
                
                # 提取HTML部分
                html_content = None
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/html":
                        self.log(f"找到HTML部分，编码: {part.get_content_charset()}")
                        try:
                            # 尝试获取HTML内容
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or 'utf-8'
                            html_content = payload.decode(charset, errors='ignore')
                            self.log(f"成功解码HTML内容，长度: {len(html_content)}")
                            break
                        except Exception as decode_error:
                            self.log(f"解码HTML内容失败: {decode_error}")
                
                if html_content:
                    # 使用解析出的HTML内容
                    html_blocks = [html_content]
                else:
                    # 回退到正则表达式提取
                    self.log("未能从MIME消息中提取HTML，回退到正则表达式")
                    html_blocks = re.findall(r'<html[\s\S]*?</html>', mhtml_content, re.IGNORECASE)
            except Exception as mime_error:
                self.log(f"解析MIME消息失败，使用正则表达式: {mime_error}")
                # 回退到正则表达式提取
                html_blocks = re.findall(r'<html[\s\S]*?</html>', mhtml_content, re.IGNORECASE)
            
            self.log(f"找到 {len(html_blocks)} 个HTML块")
            
            if not html_blocks:
                # 尝试最后的备选方案：直接从原始内容中提取文本
                self.log("未找到HTML块，尝试直接提取文本")
                soup = BeautifulSoup(mhtml_content, 'html.parser')
                text = soup.get_text()
                if len(text) > 500:  # 确保有足够的文本
                    return {
                        'title': os.path.basename(file_path).replace('.mhtml', ''),
                        'text': text,
                        'word_count': len(text),
                        'images': [],
                        'source': file_path,
                        'extraction_method': 'direct_text_extraction'
                    }
                else:
                    self.log("直接文本提取也失败了")
                    return None
                
            # 处理所有HTML块，寻找最佳结果
            results = []
            for i, html_block in enumerate(html_blocks):
                self.log(f"正在处理HTML块 {i+1}/{len(html_blocks)}")
                result = self._process_html_block(html_block, i)
                if result:
                    results.append(result)
            
            if not results:
                self.log("未能从任何HTML块中提取内容")
                return None
                
            # 返回最佳结果（内容最长的）
            best_result = max(results, key=lambda x: x['content_length'])
            self.log(f"找到最佳结果，内容长度: {best_result['content_length']}")
            
            return {
                'title': best_result['title'],
                'text': best_result['content'],
                'word_count': best_result['content_length'],
                'images': [],  # MHTML中的图片暂不处理
                'source': file_path,
                'extraction_method': 'mhtml_direct_parse'
            }
            
        except Exception as e:
            self.log(f"提取过程中出错: {e}")
            import traceback
            self.log(traceback.format_exc())
            return None
    
    def _decode_text(self, text):
        """尝试解码文本"""
        original_text = text
        
        # 检查是否包含大量"=XX"格式，这是quoted-printable编码的特征
        if '=' in text and text.count('=') > 10 and len(text) > 100:
            try:
                # 尝试修复可能的格式问题并解码
                text = text.replace('\n', '')
                text = text.replace(' ', '')
                # 确保每个等号后面都有两个字符（quoted-printable格式）
                cleaned_text = ""
                i = 0
                while i < len(text):
                    if text[i] == '=' and i+2 < len(text):
                        try:
                            # 检查后两个字符是否是有效的十六进制
                            int(text[i+1:i+3], 16)
                            cleaned_text += text[i:i+3]
                            i += 3
                        except ValueError:
                            cleaned_text += text[i]
                            i += 1
                    else:
                        cleaned_text += text[i]
                        i += 1
                
                # 尝试使用quopri解码
                decoded = quopri.decodestring(cleaned_text).decode('utf-8', errors='ignore')
                self.log(f"成功应用quoted-printable解码")
                return decoded
            except Exception as e:
                self.log(f"quoted-printable解码失败: {e}")
                
        # 尝试标准的quoted-printable解码
        try:
            if '=' in text:
                decoded = quopri.decodestring(text).decode('utf-8', errors='ignore')
                if decoded != text and len(decoded) > 10:
                    self.log("标准quoted-printable解码成功")
                    return decoded
        except:
            pass
            
        # 检查是否可能是Base64编码（只包含Base64字符）
        base64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
        if all(c in base64_chars for c in text.strip()):
            try:
                padding_needed = 4 - (len(text) % 4)
                if padding_needed < 4:
                    text += "=" * padding_needed
                decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
                if decoded.isprintable() and len(decoded) > 10:
                    self.log("Base64解码成功")
                    return decoded
            except:
                pass

        # 尝试URL解码
        try:
            decoded = unquote(text)
            if decoded != text:
                self.log("URL解码成功")
                return decoded
        except:
            pass

        # 如果所有解码方法都失败，返回原始文本
        return original_text

    def _process_html_block(self, html_block, block_index):
        """处理单个HTML块"""
        try:
            soup = BeautifulSoup(html_block, 'html.parser')
            
            # 查找标题 - 使用多种选择器
            title_selectors = [
                'h1.j_chapterName',
                'h1[class*="chapter"]',
                '.chapter-title',
                'h1',
                'h2',
                '.title'
            ]
            
            title = "未找到标题"
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    title = title_elem.get_text().strip()
                    self.log(f"使用选择器 '{selector}' 找到标题")
                    break
            
            # 查找内容 - 使用多种选择器
            content_selectors = [
                '.read-content',
                '.j_readContent',
                '[class*="read-content"]',
                '[class*="chapter-content"]',
                '[id*="content"]',
                '.content',
                'main',
                'article'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 尝试提取所有段落
                    paragraphs = content_elem.find_all(['p', 'div'])
                    if paragraphs:
                        content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    else:
                        content = content_elem.get_text().strip()
                    
                    if len(content) > 100:  # 只接受足够长的内容
                        self.log(f"使用选择器 '{selector}' 找到内容")
                        break
            
            if not content or len(content) < 100:
                self.log("未找到足够长的内容")
                return None
                
            # 处理可能的编码问题
            if title and title != "未找到标题":
                title = self._decode_text(title)

            # 解码内容
            content = self._decode_text(content)
            
            # 如果标题看起来是编码的，尝试使用文件名作为标题
            if '%' in title or '=' in title:
                self.log("标题可能是编码的，将尝试使用文件名")
                file_name = os.path.basename(file_path) if 'file_path' in locals() else "unknown.mhtml"
                if file_name.endswith('.mhtml'):
                    file_name = file_name[:-6]  # 去掉扩展名
                title = file_name.replace('_', ' ').strip()
            
            return {
                'block_index': block_index,
                'title': title,
                'content': content,
                'content_length': len(content)
            }
            
        except Exception as e:
            self.log(f"处理HTML块 {block_index} 时出错: {e}")
            return None

# 测试代码
if __name__ == "__main__":
    file_path = r"E:\360Downloads\test.mhtml"
    extractor = MHTMLExtractor()
    extractor.set_debug(True)
    
    result = extractor.extract_content(file_path)
    if result:
        print("=" * 50)
        print(f"标题: {result['title']}")
        print(f"内容长度: {result['word_count']} 字符")
        print("内容预览:")
        print("-" * 30)
        print(result['text'][:1000] + "..." if len(result['text']) > 1000 else result['text'])
        
        # 保存提取结果到txt文件，方便查看
        try:
            output_path = os.path.join(os.path.dirname(file_path), "extracted_content.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"标题: {result['title']}\n\n")
                f.write(result['text'])
            print(f"\n提取内容已保存到: {output_path}")
        except Exception as save_error:
            print(f"保存提取内容失败: {save_error}")
    else:
        print("提取失败")