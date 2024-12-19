import os
import sys
import streamlit.web.cli as stcli

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
    models_path = get_resource_path('Models')
    
    # Set environment variables
    os.environ['CHROMADB_PATH'] = chromadb_path
    os.environ['MODELS_PATH'] = models_path

    # Determine the path to Streamlit_gui.py
    streamlit_gui_path = get_resource_path('Streamlit_gui.py')

    # Modify sys.argv to run Streamlit with specific port
    sys.argv = [
        'streamlit', 
        'run', 
        streamlit_gui_path,
        '--global.developmentMode','false',
        '--server.port', '8501',
        '--server.address', 'localhost',
    ]

    # Run Streamlit
    sys.exit(stcli.main())

if __name__ == '__main__':
    main()