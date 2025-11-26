#!/bin/bash
# 小说阅读器浏览器 - 虚拟环境启动脚本
# 使用专门创建的虚拟环境来避免PyQt5库冲突

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$HOME/novel_browser_venv"

echo "===== 小说阅读器浏览器启动 ====="

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ 错误: 虚拟环境不存在: $VENV_DIR"
    echo ""
    echo "请先运行以下命令创建虚拟环境:"
    echo "/usr/bin/python3 -m venv --system-site-packages $VENV_DIR"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境: $VENV_DIR"
source "$VENV_DIR/bin/activate"

# 确保使用系统Qt库
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# 显示Python版本信息
echo "🐍 Python版本: $(python --version)"
echo "📍 Python路径: $(which python)"
echo ""

# 启动浏览器
echo "🚀 正在启动浏览器..."
cd "$SCRIPT_DIR"
python browser.py "$@"

# 保存退出状态码
EXIT_CODE=$?

# 停用虚拟环境
deactivate

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 浏览器正常退出"
else
    echo "❌ 浏览器退出，状态码: $EXIT_CODE"
fi

exit $EXIT_CODE