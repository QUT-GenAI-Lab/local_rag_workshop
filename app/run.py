import os
import sys
import streamlit.web.cli as stcli

#jankily adding imports so that pyinstaller will recognise them
import streamlit_gui
import llama_engine
import chromadb_engine
import RAG_backend


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    # Set up paths
    chromadb_path = get_resource_path('chromadbs')
    models_path = get_resource_path('models')
    
    # Set environment variables
    os.environ['CHROMADB_PATH'] = chromadb_path
    os.environ['MODELS_PATH'] = models_path

    # Determine the path to Streamlit_gui.py
    streamlit_gui_path = get_resource_path('streamlit_gui.py')

    # Modify sys.argv to run Streamlit with specific port
    sys.argv = [
        'streamlit', 
        'run', 
        streamlit_gui_path,
        '--global.developmentMode','false',
        '--server.enableCORS', 'true',
        '--server.enableXsrfProtection', 'true'
    ]

    # Run Streamlit
    sys.exit(stcli.main())

if __name__ == '__main__':
    main()