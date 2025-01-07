import sys
from streamlit.web.cli import main
# import llama_engine
# import RAG_backend
# import streamlit_gui
# import chromadb_engine
# import sklearn

if __name__ == '__main__':
    # Force streamlit to use the proper CLI args
    sys.argv = ["streamlit", 
                "run", 
                "streamlit_gui.py",
                '--global.developmentMode','false',
                '--server.enableCORS', 'true',
                '--server.enableXsrfProtection', 'true',
               ]
    main()