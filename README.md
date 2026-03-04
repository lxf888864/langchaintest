# LangChain 股票智能体 Web 工程

一个可在本地运行的智能体 Web 项目，支持：
- 本地 Ollama 或 OpenAI 作为底层模型（可配置切换）
- MCP 工具获取指定股票当前价格
- 用户上传文件并写入向量库（RAG）
- 输入股票名后生成结合“实时价格 + RAG资料”的股票评论

## 快速开始
请先阅读：`docs/HELP.md`

## 项目结构
```text
app/
  backend/
  frontend/
  tools/
  config/
data/
docs/
```


## Windows 快速启动
1. 启动后端：`run_backend.bat`（CMD）或 `./run_backend.ps1`（PowerShell）
2. 启动前端：`run_frontend.bat`（CMD）或 `./run_frontend.ps1`（PowerShell）
3. 打开浏览器访问：`http://localhost:8501`

## PyCharm 调试后端（Windows）
详见 `docs/HELP.md` 的“在 PyCharm 中启动后端并 Debug（Windows）”章节。

## PyCharm 运行配置模板
项目已内置 `.run/` 目录配置，可直接在 PyCharm 中选择：
- `Backend FastAPI (uvicorn)`
- `Frontend Streamlit`

如解释器路径不一致，请在 PyCharm 中改为本机 `.venv` 的实际路径。


## 模型提供商切换（Ollama / OpenAI）
在 `app/config/settings.yaml` 中设置：
- `llm_provider`: `ollama` 或 `openai`
- `embedding_provider`: `ollama` 或 `openai`

若使用 OpenAI，建议通过环境变量配置密钥：
```bash
export OPENAI_API_KEY="your-key"   # Windows PowerShell: $env:OPENAI_API_KEY="your-key"
```
