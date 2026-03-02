# 帮助文档：本地运行股票智能体工程

## 1. 前置软件
1. Python 3.10+
2. Ollama（本地大模型服务）
3. （可选）Git

## 2. 安装 Ollama 与模型

### 2.1 安装 Ollama
- macOS/Linux: 参考 https://ollama.com/download
- Windows: 使用官方安装包

### 2.2 启动模型
```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
ollama serve
```

## 3. 安装 Python 依赖
在项目根目录执行：
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -U pip
pip install -r requirements.txt
```

> Windows 首次执行 PowerShell 脚本若被策略拦截，可在 PowerShell（管理员）中执行：
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 4. 修改本地配置
配置文件：`app/config/settings.yaml`
关键项：
- `ollama.base_url`: Ollama 服务地址（默认 `http://localhost:11434`）
- `ollama.model`: 对话模型名称
- `ollama.embedding_model`: 向量模型名称
- `mcp.server_command/server_args`: MCP 工具启动命令

## 5. 启动服务

### 5.1 启动后端 API
- macOS/Linux:
```bash
./run_backend.sh
```
- Windows (CMD):
```bat
run_backend.bat
```
- Windows (PowerShell):
```powershell
./run_backend.ps1
```

### 5.2 启动前端 Web
新开一个终端：
- macOS/Linux:
```bash
./run_frontend.sh
```
- Windows (CMD):
```bat
run_frontend.bat
```
- Windows (PowerShell):
```powershell
./run_frontend.ps1
```

浏览器打开：`http://localhost:8501`

## 6. 使用说明
1. 点击“上传文件”前先在页面选择本地文件（txt/md/pdf/docx）
2. 上传成功后，文本会被解析并写入 Chroma 向量库
3. 输入股票代码（如 `AAPL`, `TSLA`, `600519.SS`）并点击“提交”
4. 系统会：
   - 通过 MCP 工具获取实时价格
   - 从向量库检索相关资料
   - 调用 Ollama 生成评论并显示在对话框

## 7. 常见问题
1. **报错无法连接 Ollama**
   - 检查 `ollama serve` 是否运行
   - 检查 `settings.yaml` 中 `ollama.base_url`
2. **股票无结果**
   - 请使用 Yahoo 支持的代码格式，例如 `600519.SS`（上证）
3. **PDF/DOCX 解析失败**
   - 先尝试 txt/md 文件
   - 确保依赖已完整安装

## 8. 注意事项
- 本项目输出仅供学习和演示，不构成投资建议。
- 股票数据依赖公网接口，网络不可用时会失败。


## 9. 在 PyCharm 中启动后端并 Debug（Windows）
1. 用 PyCharm 打开项目根目录 `langchaintest`。
2. 先在 PyCharm 终端创建并选择解释器：
   - `python -m venv .venv`
   - Windows 解释器路径建议选择：`.venv\Scripts\python.exe`
   - 安装依赖：`pip install -r requirements.txt`
3. 在 PyCharm 顶部点击 **Run | Edit Configurations...**，新增 **Python** 配置：
   - **Name**: `Backend FastAPI (uvicorn)`
   - **Module name**: `uvicorn`
   - **Parameters**: `app.backend.api:app --host 127.0.0.1 --port 8001 --reload`
   - **Working directory**: 项目根目录（`...\langchaintest`）
   - **Python interpreter**: `.venv\Scripts\python.exe`
4. 点击 Run/Debug 启动该配置，看到 `Uvicorn running on http://127.0.0.1:8001` 即成功。
5. 在 `app/backend/api.py` 或 `app/backend/agent_service.py` 打断点，使用 Debug 启动后，即可在接口请求时命中断点。
6. 可选：在 PyCharm 再加一个 **Streamlit 前端** 配置（普通 Run 即可）：
   - **Module name**: `streamlit`
   - **Parameters**: `run app/frontend/streamlit_app.py --server.port 8501`
   - 启动后访问 `http://localhost:8501`。

> 提示：如果后端 Debug 时希望同时启动 MCP 工具，无需手动额外运行工具进程，后端会按 `app/config/settings.yaml` 的 `mcp.server_command/server_args` 自动拉起。

