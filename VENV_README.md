# 小说阅读器浏览器 - 专用虚拟环境配置

为了解决PyQt5库与系统Qt库版本不兼容问题，我们创建了一个专用的Python虚拟环境，该环境允许访问系统包（包括系统PyQt5）。

## 虚拟环境信息

- 位置: `~/novel_browser_venv`
- Python版本: 3.10.12（系统Python）
- 特性: 允许访问系统包（`--system-site-packages`）

## 安装的依赖包

- PyQt5 (使用系统包)
- PyQtWebEngine (使用系统包)
- beautifulsoup4
- lxml
- requests (系统包)

## 使用方法

### 方法1: 使用启动脚本（推荐）

直接运行提供的启动脚本:

```bash
./start_browser_venv.sh
```

该脚本会自动激活虚拟环境，设置必要的环境变量，并启动浏览器。

### 方法2: 手动激活虚拟环境

如果您需要修改代码或调试，可以手动激活虚拟环境:

```bash
# 激活虚拟环境
source ~/novel_browser_venv/bin/activate

# 确保使用系统Qt库
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# 运行浏览器
python browser.py
```

## 重新创建虚拟环境（如需要）

如果虚拟环境损坏或需要重新创建:

```bash
# 删除现有虚拟环境
rm -rf ~/novel_browser_venv

# 创建新的虚拟环境
/usr/bin/python3 -m venv --system-site-packages ~/novel_browser_venv

# 激活虚拟环境
source ~/novel_browser_venv/bin/activate

# 安装依赖包
pip install beautifulsoup4 lxml

# 退出虚拟环境
deactivate
```

## 故障排除

如果遇到问题:

1. **确认使用正确的Python版本**:
   运行 `which python` 确认使用的是虚拟环境中的Python

2. **PyQt5库冲突**:
   确保环境变量 `LD_LIBRARY_PATH` 正确设置指向系统Qt库

3. **依赖包缺失**:
   如果收到模块缺失错误，使用pip安装相应的包:
   ```bash
   source ~/novel_browser_venv/bin/activate
   pip install <包名>
   ```

4. **权限问题**:
   确保启动脚本有执行权限:
   ```bash
   chmod +x start_browser_venv.sh
   ```