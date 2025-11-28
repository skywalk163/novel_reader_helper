#!/bin/bash
# 小说阅读器浏览器启动脚本
# 用于解决Qt和OpenGL库冲突问题

echo "正在启动小说阅读器浏览器..."

# 确保使用系统的图形库，而不是Python环境中的库
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# 移除Python环境中可能冲突的库路径
if [ -n "$CONDA_PREFIX" ]; then
    export LD_LIBRARY_PATH=$(echo $LD_LIBRARY_PATH | tr ':' '\n' | grep -v "$CONDA_PREFIX" | tr '\n' ':')
fi

# 设置Qt平台为xcb（X11）
export QT_QPA_PLATFORM=xcb

# 禁用Qt的xcb日志，减少干扰
export QT_LOGGING_RULES="qt.qpa.*=false"

# 强制使用系统Python3而不是虚拟环境中的Python
PYTHON_CMD=python3

# 清除PYTHONPATH，避免使用虚拟环境中的包
export PYTHONPATH=""

# 使用系统PyQt5启动浏览器
echo "尝试使用系统Python3和系统PyQt5启动..."
$PYTHON_CMD browser.py "$@"

# 如果上面失败了，尝试直接导入浏览器模块功能
if [ $? -ne 0 ]; then
    echo "尝试替代方案..."
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from browser import create_browser_window, get_qapplication
    app = get_qapplication()
    browser = create_browser_window()
    browser.show()
    browser.go_home()
    sys.exit(app.exec_())
except Exception as e:
    print(f'启动失败: {e}')
    "
fi