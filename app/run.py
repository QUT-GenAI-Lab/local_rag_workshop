import sys
from streamlit.web.cli import main
# import llama_engine
# import RAG_backend
# import streamlit_gui
# import chromadb_engine
# import sklearn

from os import path
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GUI_DIR = None
# Walk through the directory tree
for root, _, files in os.walk(BASE_DIR):
    # Check if the target file is in the current directory
    if "streamlit_gui.py" in files:
        # Return the absolute path of the found file
        GUI_DIR = os.path.join(root, "streamlit_gui.py")

if not GUI_DIR:
    sys.exit("Couldn't find streamlit_gui.py!")
        


if __name__ == '__main__':
    # Force streamlit to use the proper CLI args
    sys.argv = ["streamlit", 
                "run", 
                GUI_DIR,
                '--global.developmentMode','false',
                '--server.enableCORS', 'true',
                '--server.enableXsrfProtection', 'true',
               ]
    main()