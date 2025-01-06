import subprocess
#forcing pyinstaller to recognise these things
import llama_engine
import RAG_backend
import streamlit_gui
import chromadb_engine
subprocess.run("streamlit run streamlit_gui.py", shell=True)