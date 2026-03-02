from __future__ import annotations

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8001"

st.set_page_config(page_title="股票智能体", page_icon="📈", layout="centered")
st.title("📈 股票智能体（LangChain + Ollama + MCP + RAG）")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.subheader("对话框")
chat_box = st.container(border=True)
with chat_box:
    if not st.session_state.messages:
        st.caption("暂无对话，输入股票名称后点击提交。")
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f"**你：** {content}")
        else:
            st.markdown(f"**助手：** {content}")

st.subheader("输入与操作")
stock_name = st.text_input("股票名称", value="请输入股票名称，我可以为您生成评论")
uploaded_file = st.file_uploader("上传资料文件（txt/md/pdf/docx）", type=["txt", "md", "pdf", "docx", "doc"])

col1, col2 = st.columns(2)

with col1:
    if st.button("上传文件", use_container_width=True):
        if uploaded_file is None:
            st.warning("请先选择文件")
        else:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            resp = requests.post(f"{API_BASE}/upload", files=files, timeout=120)
            if resp.ok:
                st.success(resp.json().get("message", "上传成功"))
            else:
                st.error(f"上传失败: {resp.text}")

with col2:
    if st.button("提交", use_container_width=True, type="primary"):
        st.session_state.messages.append(("user", stock_name))
        resp = requests.post(f"{API_BASE}/chat", json={"stock_name": stock_name}, timeout=180)
        if resp.ok:
            answer = resp.json().get("answer", "")
            st.session_state.messages.append(("assistant", answer))
        else:
            st.session_state.messages.append(("assistant", f"请求失败: {resp.text}"))
        st.rerun()
