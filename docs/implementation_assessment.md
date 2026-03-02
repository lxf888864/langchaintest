# 智能体 Web 工程评估资料（LangChain + Ollama + MCP + RAG）

## 1. 可行性结论
该项目**可行**，并且可以在本地完整运行。建议采用：

- 前端：`Streamlit`（开发效率高，内置聊天区与上传控件）
- 服务端编排：`FastAPI` + `LangChain`
- 本地模型：`Ollama`（模型名称通过本地配置文件读取）
- 向量数据库：`Chroma`（本地持久化）
- 工具协议：`MCP`（本地注册“股票实时价格”工具）

该方案满足你提出的全部要求，并保留后续扩展空间（多工具、多模型、多数据源）。

---

## 2. 界面效果图（原型）
已提供静态原型页面用于评估交互布局（见 `docs/mockup_ui.html`），主要元素如下：

1. 股票名称输入框（默认文案：`请输入股票名称，我可以为您生成评论`）
2. 对话显示区（展示用户消息与模型回复）
3. 文件上传按钮（上传本地资料用于 RAG）
4. 提交按钮（触发“查股价 + 检索资料 + 生成评论”）

> 说明：该原型仅用于确认界面布局与交互流，不代表最终样式。

---

## 3. 目标工程结构（建议）

```text
stock-agent-web/
├─ app/
│  ├─ frontend/
│  │  └─ streamlit_app.py            # Web UI
│  ├─ backend/
│  │  ├─ api.py                      # FastAPI 路由
│  │  ├─ agent_service.py            # LangChain Agent / Chain 逻辑
│  │  ├─ rag_service.py              # 文档解析、切分、向量化、检索
│  │  ├─ mcp_client.py               # MCP 工具注册与调用
│  │  └─ model_provider.py           # 读取本地配置并初始化 Ollama 模型
│  ├─ tools/
│  │  └─ stock_price_tool_mcp.py     # 通过公网获取股票价格的 MCP 工具
│  └─ config/
│     ├─ settings.yaml               # 用户可修改：ollama 模型名等
│     └─ settings.example.yaml
├─ data/
│  ├─ uploads/                       # 用户上传文件
│  └─ chroma_db/                     # 向量库持久化目录
├─ docs/
│  ├─ implementation_assessment.md   # 本评估文档
│  ├─ mockup_ui.html                 # 界面原型
│  └─ HELP.md                        # 安装、运行、注意事项（最终交付时提供）
├─ requirements.txt
└─ README.md
```

---

## 4. 运行流程（端到端）

1. 用户在 Web 界面上传资料文件（txt/pdf/md/docx）
2. 服务端解析文件内容并切分
3. 文本写入本地 Chroma 向量库，作为当前会话/租户的 RAG 语料
4. 用户输入股票名称并点击提交
5. Agent 调用 MCP 工具，从公网获取该股票当前价格
6. Agent 并行/串行执行向量检索，抽取与该股票相关的背景信息
7. LLM（Ollama 本地模型）融合“实时价格 + RAG 资料”生成股评
8. 前端对话框展示“用户输入 + 模型输出”

---

## 5. 关键技术设计点

### 5.1 Ollama 模型可配置
- 在 `settings.yaml` 中定义：
  - `ollama.base_url`（例如 `http://localhost:11434`）
  - `ollama.model`（例如 `qwen2.5:7b`）
- 启动时读取配置并初始化 `ChatOllama`，无需改代码即可切换模型。

### 5.2 MCP 股票价格工具
- 本地启动 MCP Server，暴露 `get_stock_price(symbol_or_name)` 工具。
- 工具内部请求可信财经 API（如新浪/腾讯/AlphaVantage 等可替换源）。
- Agent 仅通过 MCP 协议调用工具，满足“本地通过 MCP 注册工具”的要求。

### 5.3 RAG 数据链路
- 文件上传后保存至 `data/uploads/`
- 根据后缀选择解析器（txt/pdf/docx/md）
- 文本切片 + embedding + 写入 Chroma
- 查询阶段按“股票名 + 语义相似”检索 top-k 片段注入 Prompt

### 5.4 生成结果约束
输出模板建议包含：
- 股票名、当前价格、抓取时间
- 基于资料的核心观点（引用片段摘要）
- 风险提示（非投资建议）

---

## 6. 交付物清单（确认后实施）
确认后我将一次性生成完整可运行工程，至少包含：

1. 前后端源码（可本地运行）
2. MCP 工具与调用逻辑
3. 文件上传 + 向量入库 + 检索增强
4. 对话式股票评论生成
5. `docs/HELP.md`（前置软件安装、启动步骤、常见问题）
6. 示例配置文件与启动脚本

---

## 7. 待你确认的信息
为保证最终代码一次到位，建议你确认以下偏好：

1. 前端框架是否接受 `Streamlit`（最快交付）？
2. 股票行情 API 你是否有指定来源（或密钥）？
3. 默认 Ollama 模型用哪个（如 `qwen2.5:7b`）？
4. 上传文件作用范围是“当前会话”还是“长期持久化”？

> 你确认后，我将进入下一步：直接生成完整工程代码与帮助文档。
