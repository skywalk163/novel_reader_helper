import os
import re
import base64
from urllib.parse import unquote
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, QEventLoop, QByteArray, QTimer

def extract_content_from_mhtml(file_path):
    print("开始从 MHTML 文件提取内容...")
    
    # 添加调试信息
    print(f"正在读取文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            mhtml_content = file.read()
        print(f"成功读取文件，内容长度: {len(mhtml_content)} 字符")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None

    # 使用正则表达式提取 HTML 部分
    html_match = re.search(r'<html[\s\S]*?</html>', mhtml_content, re.IGNORECASE)
    if html_match:
        html_content = html_match.group(0)
    else:
        print("无法在 MHTML 文件中找到 HTML 内容")
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 尝试提取标题
    title = soup.find('h1', class_='j_chapterName') or soup.find('h1')
    if title:
        title = title.text.strip()
        # 解码标题
        try:
            title = base64.b64decode(title).decode('utf-8')
        except:
            try:
                title = unquote(title)
            except:
                pass  # 如果解码失败，保留原始标题
    else:
        title = "未找到标题"

    # 尝试提取正文内容
    content_div = soup.find('div', class_='read-content') or soup.find('div', id='content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = '\n'.join([p.text.strip() for p in paragraphs])
        # 尝试解码内容
        try:
            content = base64.b64decode(content).decode('utf-8')
        except:
            try:
                content = unquote(content)
            except:
                pass  # 如果解码失败，保留原始内容
    else:
        content = "未找到正文内容"

    return {
        'title': title,
        'content': content
    }

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS: {message}")

def extract_content_with_browser(file_path):
    print("使用浏览器方法提取内容...")
    
    # 添加调试信息
    print(f"正在初始化浏览器环境...")
    
    app = QApplication([])
    view = QWebEngineView()
    page = CustomWebEnginePage(view)
    view.setPage(page)
    
    loop = QEventLoop()
    view.loadFinished.connect(loop.quit)
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        html_content = file.read()
    
    view.setHtml(html_content, QUrl.fromLocalFile(file_path))
    
    # 设置超时
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(10000)  # 10秒超时
    
    loop.exec_()
    
    if timer.isActive():
        timer.stop()
    else:
        print("浏览器渲染超时")
        return None

    result = {}
    
    def handle_title(title):
        result['title'] = title

    def handle_content(content):
        result['content'] = content

    view.page().runJavaScript("""
        var title = document.querySelector('.j_chapterName') || document.querySelector('h1');
        title ? title.textContent : '未找到标题';
    """, handle_title)
    view.page().runJavaScript("""
        var content = document.querySelector('.read-content') || document.querySelector('#content');
        content ? content.innerText : '未找到正文内容';
    """, handle_content)

    timer.start(15000)  # 增加到15秒超时
    loop.exec_()
    
    if timer.isActive():
        timer.stop()
    else:
        print("JavaScript执行超时")
        return None
    
    return result

def main():
    file_path = r"E:\360Downloads\test.mhtml"
    print(f"测试文件路径: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在")
        return

    # 方法1：直接解析 MHTML
    print("\n===== 方法1：直接解析 MHTML =====")
    result1 = extract_content_from_mhtml(file_path)
    if result1:
        print(f"标题: {result1['title']}")
        print(f"内容预览: {result1['content'][:200]}...")
        print(f"内容长度: {len(result1['content'])}")

    # 方法2：使用浏览器渲染
    print("\n===== 方法2：使用浏览器渲染 =====")
    result2 = extract_content_with_browser(file_path)
    if result2:
        print(f"标题: {result2['title']}")
        print(f"内容预览: {result2['content'][:200]}...")
        print(f"内容长度: {len(result2['content'])}")

    print("\n===== 比较两种方法 =====")
    if result1 and result2:
        title_match = result1['title'] == result2['title']
        content_match = result1['content'] == result2['content']
        print(f"标题匹配: {'是' if title_match else '否'}")
        print(f"内容匹配: {'是' if content_match else '否'}")
        if not content_match:
            print("内容不匹配，可能需要进一步调查。")
    else:
        print("无法比较结果，因为至少有一种方法失败了。")

if __name__ == "__main__":
    main()