@echo off
setlocal
streamlit run app/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
endlocal
