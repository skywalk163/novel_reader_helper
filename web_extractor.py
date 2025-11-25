#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
web_extractor.py - 网页内容提取模块

此模块提供从网页中提取文本和图片的功能，专为小说阅读神器项目设计。
主要用于解析各类网页，提取正文内容、图片链接，并进行内容清洗。

作者: Comate Team
日期: 2023
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebExtractor:
    """
    网页内容提取器类
    
    用于从HTML页面中提取文本内容、图片链接以及综合信息，
    支持多种网页结构，特别优化了对小说网站的识别和提取。
    """
    
    def __init__(self):
        """初始化网页提取器"""
        # 小说网站常见的正文容器标识
        self.novel_content_patterns = [
            {"class": re.compile(r"article|content|text|body|chapter|read")},
            {"id": re.compile(r"article|content|text|body|chapter|read")}
        ]
        
        # 广告和无用内容的标识
        self.ad_patterns = [
            {"class": re.compile(r"ad|banner|recommend|footer|copyright|comment")},
            {"id": re.compile(r"ad|banner|recommend|footer|copyright|comment")},
            {"role": "advertisement"}
        ]
        
        # 用户代理，避免被某些网站拦截
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
    
    def fetch_url(self, url):
        """
        获取网页内容
        
        Args:
            url (str): 要获取的网页URL
            
        Returns:
            str: 网页HTML内容，如果获取失败则返回空字符串
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
            
            # 尝试检测并处理编码
            if response.encoding == 'ISO-8859-1':
                # 尝试从内容中检测编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
                for enc in encodings:
                    try:
                        response.content.decode(enc)
                        response.encoding = enc
                        break
                    except UnicodeDecodeError:
                        continue
            
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"获取网页失败: {e}")
            return ""
    
    def extract_text(self, html, url=None):
        """
        从HTML中提取纯文本内容
        
        Args:
            html (str): 网页HTML内容
            url (str, optional): 网页URL，用于记录日志
            
        Returns:
            str: 提取的纯文本内容
        """
        if not html:
            logger.warning("HTML内容为空")
            return ""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除不需要的元素
        for element in soup(["script", "style", "nav", "iframe", "noscript"]):
            element.decompose()
        
        # 尝试使用多种方法找到主要内容区域
        main_content = None
        
        # 1. 尝试使用小说网站常见的内容容器标识
        for pattern in self.novel_content_patterns:
            main_content = soup.find(attrs=pattern)
            if main_content:
                break
        
        # 2. 尝试使用常见的文章容器标签
        if not main_content:
            for tag_name in ['article', 'main', 'section']:
                main_content = soup.find(tag_name)
                if main_content:
                    break
        
        # 3. 寻找文本最多的div
        if not main_content:
            divs = soup.find_all('div')
            if divs:
                main_content = max(divs, key=lambda div: len(div.get_text()), default=None)
        
        # 4. 如果以上都失败，使用body
        if not main_content or len(main_content.get_text()) < 100:
            main_content = soup.body
        
        # 如果连body都没有，返回空字符串
        if not main_content:
            logger.warning("无法找到主要内容区域")
            return ""
        
        # 移除广告和无用内容
        for ad_pattern in self.ad_patterns:
            for ad in main_content.find_all(attrs=ad_pattern):
                ad.decompose()
        
        # 提取文本
        text = main_content.get_text(separator='\n', strip=True)
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 进一步清理常见的网页广告和无用文本
        text = self.clean_text(text)
        
        if len(text) < 100:
            logger.warning(f"提取的文本内容过短 ({len(text)} 字符)")
            # 如果内容过短，尝试直接从body提取全部内容
            body = soup.body
            if body:
                text = body.get_text(separator='\n', strip=True)
                text = self.clean_text(text)
        
        return text
    
    def extract_images(self, html, base_url=None):
        """
        从HTML中提取图片链接
        
        Args:
            html (str): 网页HTML内容
            base_url (str, optional): 基础URL，用于将相对路径转换为绝对路径
            
        Returns:
            list: 图片链接列表
        """
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除不需要的元素
        self._remove_unwanted_elements(soup)
        
        # 尝试识别正文内容
        content_element = self._identify_main_content(soup)
        
        if not content_element:
            content_element = soup
        
        # 提取图片链接
        images = []
        for img in content_element.find_all('img'):
            src = img.get('src', img.get('data-src', img.get('data-original')))
            if src:
                # 将相对URL转换为绝对URL
                if base_url and not bool(urlparse(src).netloc):
                    src = urljoin(base_url, src)
                images.append({
                    'url': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        
        return images
    
    def extract_content(self, html, url=None):
        """
        综合提取文本和图片信息
        
        Args:
            html (str): 网页HTML内容
            url (str, optional): 网页URL，用于将相对路径转换为绝对路径
            
        Returns:
            dict: 包含文本和图片信息的字典
        """
        base_url = url if url else None
        
        text = self.extract_text(html)
        images = self.extract_images(html, base_url)
        
        # 提取标题
        title = self._extract_title(html)
        
        # 识别小说章节信息
        chapter_info = self._identify_chapter_info(html)
        
        return {
            'title': title,
            'text': text,
            'images': images,
            'word_count': len(text),
            'chapter_info': chapter_info
        }
    
    def clean_text(self, text):
        """
        清理提取的文本
        
        Args:
            text (str): 需要清理的文本
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
        
        # 替换连续的空白字符为单个换行
        text = re.sub(r'\s+', '\n', text)
        
        # 移除空行
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 移除常见的广告文本
        ad_patterns = [
            r'本章完',
            r'未完待续',
            r'(推荐|热门)小说[：:].*',
            r'添加书签.*',
            r'手机阅读.*',
            r'http[s]?://\S+',
            r'www\.\S+',
            r'请记住本站[：:]\s*\S+',
            r'最新章节[：:]\s*\S+',
            r'\d+章节.*',
            r'如果您喜欢.*',
            r'温馨提示[：:]\s*\S+',
            r'免费阅读.*',
            r'转码阅读.*',
            r'txt下载.*',
            r'本站首发.*'
        ]
        
        for pattern in ad_patterns:
            text = re.sub(pattern, '', text)
        
        # 删除多余的空白行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 删除首尾空白
        text = text.strip()
        
        return text
    
    def _remove_unwanted_elements(self, soup):
        """移除不需要的HTML元素"""
        # 移除script和style元素
        for tag in soup(['script', 'style', 'iframe', 'noscript']):
            tag.decompose()
        
        # 移除广告和其他无用元素
        for pattern in self.ad_patterns:
            for element in soup.find_all(attrs=pattern):
                element.decompose()
    
    def _identify_main_content(self, soup):
        """
        识别网页中的主要内容区域
        
        尝试使用多种启发式方法来识别网页中的主要内容区域，
        特别针对小说网站进行了优化。
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            BeautifulSoup对象中的主要内容元素，如果未找到则返回None
        """
        # 1. 尝试使用小说网站常见的内容容器标识
        for pattern in self.novel_content_patterns:
            content = soup.find(attrs=pattern)
            if content:
                return content
        
        # 2. 尝试使用常见的文章容器标签
        for tag_name in ['article', 'main', 'section']:
            content = soup.find(tag_name)
            if content:
                return content
        
        # 3. 寻找文本最多的div
        divs = soup.find_all('div')
        if divs:
            max_text_div = max(divs, key=lambda div: len(div.get_text()), default=None)
            if max_text_div and len(max_text_div.get_text()) > 200:  # 确保内容足够长
                return max_text_div
        
        # 4. 尝试查找内容中常见的小说标记
        paragraphs = soup.find_all('p')
        if len(paragraphs) > 5:  # 如果有足够多的段落
            return soup.body
        
        return None
    
    def _extract_title(self, html):
        """提取网页标题"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 尝试从title标签获取
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.string
            # 移除网站名称等无关信息
            title = re.sub(r'[-_|]\s*\w+\.\w+.*$', '', title)
            return title.strip()
        
        # 尝试从h1标签获取
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "未找到标题"
    
    def _identify_chapter_info(self, html):
        """识别小说章节信息"""
        soup = BeautifulSoup(html, 'html.parser')
        
        chapter_info = {
            'number': None,
            'title': None,
            'prev_url': None,
            'next_url': None
        }
        
        # 尝试从h1或其他标题标签中提取章节信息
        header_tags = soup.find_all(['h1', 'h2', 'h3'])
        for tag in header_tags:
            text = tag.get_text().strip()
            # 寻找常见的章节标记，如"第X章"
            chapter_match = re.search(r'第[0-9一二三四五六七八九十百千万]+[章节卷]', text)
            if chapter_match:
                chapter_info['title'] = text
                # 尝试提取章节编号
                num_match = re.search(r'第([0-9一二三四五六七八九十百千万]+)[章节卷]', text)
                if num_match:
                    chapter_info['number'] = num_match.group(1)
                break
        
        # 寻找上一章和下一章的链接
        prev_link = soup.find(string=re.compile(r'上一[章页]|前一[章页]|上页|前页'))
        if prev_link and prev_link.parent.name == 'a':
            chapter_info['prev_url'] = prev_link.parent['href']
        else:
            # 尝试查找包含"上一"的链接
            for link in soup.find_all('a'):
                if link.string and '上一' in link.string:
                    chapter_info['prev_url'] = link['href']
                    break
        
        next_link = soup.find(string=re.compile(r'下一[章页]|后一[章页]|下页|后页'))
        if next_link and next_link.parent.name == 'a':
            chapter_info['next_url'] = next_link.parent['href']
        else:
            # 尝试查找包含"下一"的链接
            for link in soup.find_all('a'):
                if link.string and '下一' in link.string:
                    chapter_info['next_url'] = link['href']
                    break
        
        return chapter_info


# 使用示例
if __name__ == "__main__":
    extractor = WebExtractor()
    
    # 从URL获取内容
    url = "https://example.com/some-novel-chapter"
    html = extractor.fetch_url(url)
    
    if html:
        # 提取文本
        text = extractor.extract_text(html)
        print("提取的文本：")
        print(text[:500] + "..." if len(text) > 500 else text)
        
        # 提取图片
        images = extractor.extract_images(html, url)
        print(f"\n找到 {len(images)} 张图片:")
        for i, img in enumerate(images[:3]):  # 仅显示前3张
            print(f"{i+1}. {img['url']}")
        
        # 综合提取
        content = extractor.extract_content(html, url)
        print(f"\n标题: {content['title']}")
        print(f"文本长度: {content['word_count']} 字符")
        
        if content['chapter_info']['number']:
            print(f"章节号: {content['chapter_info']['number']}")
        
        if content['chapter_info']['prev_url']:
            print(f"上一章链接: {content['chapter_info']['prev_url']}")
        
        if content['chapter_info']['next_url']:
            print(f"下一章链接: {content['chapter_info']['next_url']}")