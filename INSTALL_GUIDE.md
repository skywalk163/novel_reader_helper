# 小说阅读神器 - 详细安装使用指南

## 目录
1. [系统要求](#系统要求)
2. [Windows 系统安装指南](#windows-系统安装指南)
3. [Linux 系统安装指南](#linux-系统安装指南)
4. [MacOS 系统安装指南](#macos-系统安装指南)
5. [详细使用教程](#详细使用教程)
6. [常见问题解决](#常见问题解决)

---

## 系统要求

### 基本要求
- **操作系统**: Windows 10/11, Ubuntu 18.04+, MacOS 10.15+
- **Python**: 3.7 或更高版本
- **内存**: 建议 4GB 以上
- **磁盘空间**: 至少 2GB 可用空间（用于模型文件）
- **网络**: 首次运行需要网络连接（下载模型文件）

### 推荐配置
- **Python**: 3.9 或更高版本
- **内存**: 8GB 或以上
- **处理器**: 支持 AVX 指令集的 CPU

---

## Windows 系统安装指南

### 步骤 1: 安装 Python

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载最新版本的 Python（推荐 3.9 或更高版本）
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH" 选项
5. 点击 "Install Now" 完成安装

### 步骤 2: 验证 Python 安装

打开命令提示符（CMD）或 PowerShell，运行：

```bash
python --version
```

如果显示 Python 版本号，说明安装成功。

### 步骤 3: 下载项目文件

1. 下载项目压缩包并解压到任意目录
2. 例如：`C:\novel_reader_helper`

### 步骤 4: 安装依赖包

打开命令提示符，进入项目目录：

```bash
cd C:\novel_reader_helper
```

现在，您有两个安装选项：

#### 选项 1: 快速安装（不包含 OCR 功能）

```bash
python install.py --quick
```

这将安装基本依赖，不包括 OCR 相关的包，适合想要快速开始使用或不需要 OCR 功能的用户。

#### 选项 2: 完整安装（包含所有功能）

```bash
python install.py --full
```

完整安装会包括所有依赖，包括 OCR 功能所需的 PaddleOCR 等包。

安装脚本会自动：
- 检查 Python 版本
- 安装所需依赖包（快速安装时不包括 PaddleOCR）
- 下载必要的模型文件（仅完整安装）
- 创建小说词典文件

**注意**: 完整安装首次运行可能需要较长时间（10-20分钟），请耐心等待。快速安装通常只需要 2-5 分钟。

### 步骤 5: OCR 服务配置（仅限完整安装）

如果您选择了完整安装并需要使用 OCR 功能，请按以下步骤启动 OCR 服务：

1. 打开新的命令提示符窗口
2. 导航到 paddleocrapp 目录：
   ```bash
   cd C:\novel_reader_helper\paddleocrapp
   ```
3. 启动 OCR 服务：
   ```bash
   python app.py
   ```

OCR 服务将在后台运行，地址为 `http://127.0.0.1:5000`。保持此窗口开启以确保 OCR 功能可用。


### 步骤 5: 启动应用程序

```bash
python start.py
```

或直接运行主程序：

```bash
python main.py
```

---

## Linux 系统安装指南

### 步骤 1: 安装 Python 和 pip

大多数 Linux 发行版已预装 Python。如果没有，请使用包管理器安装：

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

**Fedora**:
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

### 步骤 2: 验证安装

```bash
python3 --version
pip3 --version
```

### 步骤 3: 下载项目

使用 git 克隆或下载压缩包：

```bash
# 使用 git
git clone [项目地址]
cd novel_reader_helper

# 或下载并解压
wget [下载链接]
unzip novel_reader_helper.zip
cd novel_reader_helper
```

### 步骤 4: 安装依赖

现在，您有两个安装选项：

#### 选项 1: 快速安装（不包含 OCR 功能）

```bash
python3 install.py --quick
```

这将安装基本依赖，不包括 OCR 相关的包，适合想要快速开始使用或不需要 OCR 功能的用户。

#### 选项 2: 完整安装（包含所有功能）

```bash
python3 install.py --full
```

完整安装会包括所有依赖，包括 OCR 功能所需的 PaddleOCR 等包。

**注意**: 完整安装首次运行可能需要较长时间（10-20分钟），请耐心等待。快速安装通常只需要 2-5 分钟。

### 步骤 5: OCR 服务配置（仅限完整安装）

如果您选择了完整安装并需要使用 OCR 功能，请按以下步骤启动 OCR 服务：

1. 打开新的终端窗口
2. 导航到 paddleocrapp 目录：
   ```bash
   cd /path/to/novel_reader_helper/paddleocrapp
   ```
3. 启动 OCR 服务：
   ```bash
   python3 app.py
   ```

OCR 服务将在后台运行，地址为 `http://127.0.0.1:5000`。保持此终端窗口开启以确保 OCR 功能可用。

### 步骤 6: 启动应用

```bash
python3 start.py
```

---

## MacOS 系统安装指南

### 步骤 1: 安装 Python

MacOS 通常预装 Python，但可能版本较旧。建议安装最新版本：

**方法一：使用 Homebrew**
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.9
```

**方法二：从官网下载**
访问 [Python 官网](https://www.python.org/downloads/mac-osx/) 下载并安装。

### 步骤 2: 下载并安装项目

```bash
cd ~/Downloads
# 下载并解压项目
unzip novel_reader_helper.zip
cd novel_reader_helper
```

### 步骤 3: 安装依赖

现在，您有两个安装选项：

#### 选项 1: 快速安装（不包含 OCR 功能）

```bash
python3 install.py --quick
```

这将安装基本依赖，不包括 OCR 相关的包，适合想要快速开始使用或不需要 OCR 功能的用户。

#### 选项 2: 完整安装（包含所有功能）

```bash
python3 install.py --full
```

完整安装会包括所有依赖，包括 OCR 功能所需的 PaddleOCR 等包。

**注意**: 完整安装首次运行可能需要较长时间（10-20分钟），请耐心等待。快速安装通常只需要 2-5 分钟。

### 步骤 4: OCR 服务配置（仅限完整安装）

如果您选择了完整安装并需要使用 OCR 功能，请按以下步骤启动 OCR 服务：

1. 打开新的终端窗口
2. 导航到 paddleocrapp 目录：
   ```bash
   cd ~/Downloads/novel_reader_helper/paddleocrapp
   ```
3. 启动 OCR 服务：
   ```bash
   python3 app.py
   ```

OCR 服务将在后台运行，地址为 `http://127.0.0.1:5000`。保持此终端窗口开启以确保 OCR 功能可用。

### 步骤 5: 启动应用

```bash
python3 start.py
```

---

## 详细使用教程

### 功能一：图片文字识别

**使用场景**: 当您遇到图片格式的小说章节，文字太小看不清时。

**操作步骤**:
1. 点击 "📁 选择图片文件" 按钮
2. 从文件浏览器中选择包含小说文字的图片
3. 图片会显示在预览区域
4. 点击 "🔍 文字识别" 按钮
5. 等待几秒钟，识别出的文字会显示在 "识别结果" 选项卡中

**支持的图片格式**:
- PNG, JPG, JPEG, BMP, TIFF, GIF

**最佳实践**:
- 使用清晰度高的图片
- 确保文字对比度足够（黑字白底效果最好）
- 避免倾斜、模糊的图片

### 功能二：直接文本输入

**使用场景**: 当您已有文本格式的小说内容，需要快速总结。

**操作步骤**:
1. 点击 "📄 输入文本内容" 按钮
2. 在文本框中粘贴或输入小说章节内容
3. 点击 "📝 AI总结" 按钮
4. 总结结果会显示在 "AI总结" 选项卡中

### 功能三：AI 智能总结

**功能说明**:
- 自动提取章节关键词
- 识别重要情节和句子
- 生成简洁的内容概要
- 计算阅读时间预估

**总结内容包括**:
- 📊 字数统计
- ⏱️ 预计阅读时间
- 🔑 关键词提取
- 📖 重要情节摘要

### 功能四：保存处理结果

**操作步骤**:
1. 完成文字识别或 AI 总结后
2. 点击 "?? 保存结果" 按钮
3. 选择保存位置和文件名
4. 结果会保存为 .txt 文本文件

**保存内容包括**:
- 处理时间戳
- 文字识别结果（如有）
- AI 总结内容（如有）

---

## 常见问题解决

### Q1: 安装时出现 "No module named 'pip'" 错误

**解决方案**:
```bash
# Windows
python -m ensurepip --upgrade

# Linux/MacOS
python3 -m ensurepip --upgrade
```

### Q2: PaddleOCR 安装失败

**可能原因**:
- 网络连接问题
- Python 版本不兼容
- 系统缺少必要的编译工具

**解决方案**:
```bash
# 尝试使用国内镜像源
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或分步安装
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 文字识别速度很慢

**原因**: 第一次运行时需要下载模型文件

**解决方案**:
- 保持网络连接稳定
- 模型下载完成后，后续识别会快很多
- 模型文件会缓存在本地，下次直接使用

### Q4: 图形界面无法显示

**可能原因**: 缺少 tkinter 模块

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# MacOS（通常已包含）
brew install python-tk
```

### Q5: 识别结果不准确

**改进方法**:
1. 使用更清晰的图片
2. 调整图片对比度和亮度
3. 确保图片文字方向正确（不倾斜）
4. 避免复杂背景的图片

### Q6: 内存不足错误

**解决方案**:
- 关闭其他占用内存的程序
- 处理较小的图片或文本
- 升级系统内存

### Q7: 无法启动应用程序

**检查清单**:
1. 确认 Python 版本 >= 3.7
2. 确认所有依赖包已安装
3. 检查是否有其他程序占用相关端口
4. 查看错误日志信息

**重新安装**:
```bash
# 清理并重新安装
pip uninstall paddleocr paddlepaddle -y
python install.py
```

---

## 性能优化建议

1. **首次运行优化**:
   - 首次运行前确保网络连接稳定
   - 等待所有模型文件下载完成
   - 后续运行会更快

2. **图片处理优化**:
   - 压缩过大的图片（建议 < 5MB）
   - 使用常见图片格式（PNG, JPG）
   - 避免处理超高分辨率图片

3. **文本处理优化**:
   - 单次处理文本建议 < 10000 字
   - 超长文本可分段处理
   - 定期清空历史记录

---

## 高级使用技巧

### 批量处理图片

虽然当前版本不直接支持批量处理，但您可以：
1. 使用脚本循环调用功能
2. 将结果保存到不同文件
3. 最后合并整理

### 自定义词典

编辑 `novel_dict.txt` 文件，添加您常见的小说专用词汇，以提高总结质量。

### 快捷键（计划中）

未来版本将支持：
- Ctrl+O: 打开图片
- Ctrl+S: 保存结果
- Ctrl+N: 清空内容
- F5: 刷新界面

---

## 技术支持

如果以上方法无法解决您的问题，请：

1. 查看详细错误日志
2. 记录错误信息和操作步骤
3. 访问项目主页提交 Issue
4. 联系技术支持

---

## 更新日志

### v1.0 (2025-11-22)
- ✅ 实现基础 OCR 文字识别功能
- ✅ 实现 AI 文本总结功能
- ✅ 完成图形用户界面
- ✅ 支持图片和文本两种输入方式
- ✅ 添加结果保存功能

### 未来计划
- [ ] 集成更先进的 AI 模型
- [ ] 支持批量处理
- [ ] 添加翻译功能
- [ ] 开发移动端版本

---

**祝您使用愉快！**