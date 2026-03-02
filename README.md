# LangChain 股票智能体 Web 工程

一个可在本地运行的智能体 Web 项目，支持：
- 本地 Ollama 大模型（模型名本地可配置）
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
