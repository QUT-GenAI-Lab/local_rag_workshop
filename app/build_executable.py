import os
import subprocess
import sys
import shutil


def create_executable():
    # Paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure required directories exist
    os.makedirs(os.path.join(project_root, 'dist'), exist_ok=True)
    
    # PyInstaller command
    pyinstaller_command = [
        'pyinstaller',
        '--onedir',           # Create a directory with executable and dependencies
        # '--windowed',         # No console window (for GUI apps)
        '--noconfirm',        # rewrite build and dist folders automatically without confirmation (your fault for deleting your shit brus).
        
        # Add data files and directories
        # '--add-data', f'chromadbs{os.pathsep}chromadbs',
        # '--add-data', f'chats{os.pathsep}chats',
        
        # Add Python source files
        # '--add-data', f'streamlit_gui.py{os.pathsep}.',
        # '--add-data', f'chromadb_engine.py{os.pathsep}.',
        # '--add-data', f'llama_engine.py{os.pathsep}.',
        # '--add-data', f'RAG_backend.py{os.pathsep}.',
        
        # Hidden imports for potential dependencies
        '--hidden-import','sklearn.tree._partitioner',
        
        # Additional options to handle specific libraries
        '--collect-all', 'pypdf',
        '--collect-all', 'chromadb',
        '--collect-all', 'streamlit',
        '--collect-all', 'sklearn', #seems to be having issues with sklearn
        '--collect-all', 'ollama',
        '--collect-all', 'onnxruntime',
        '--collect-all', 'docx2txt',
        '--collect-all', 'umap',
        '--collect-all', 'pynndescent',
        '--collect-all', 'numba',
        '--collect-all', 'tokenizers', #windows-specific issues
        
        
        # Specify the entry point
        'run.py'
    ]
    
    # Run PyInstaller
    try:
        subprocess.run(pyinstaller_command, check=True)
        
        # Additional file copying
        dist_dir = os.path.join(project_root, 'dist', 'run') #change this for different build names, e.g. when you change name of run.py I guess
        
        # List of files to copy
        files_to_copy = [
            'streamlit_gui.py',
            'chromadb_engine.py',
            'llama_engine.py',
            'RAG_backend.py'
        ]

        # list of dirs to copy
        dirs_to_copy = [
            'chromadbs',
            'chats',
        ]
        
        for file in files_to_copy:
            src_path = os.path.join(project_root, file)
            dst_path = os.path.join(dist_dir, file)
            shutil.copy2(src_path, dst_path)

        for dir_str in dirs_to_copy:
            src_path = os.path.join(project_root, dir_str)
            dst_path = os.path.join(dist_dir, dir_str)
            shutil.copytree(src_path, dst_path)            
        
        print("Executable created successfully!")
        print("\nTo run the application:")
        print(f"Navigate to the '{dist_dir}' directory and execute the 'run' executable")
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_executable()