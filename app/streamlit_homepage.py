import streamlit as st

chat_page = st.Page("streamlit_gui.py", title = "Chat")
db_page = st.Page("streamlit_chromadb_gui.py", title = "Vector DataBase Explore")

pg = st.navigation([chat_page, db_page])

pg.run()