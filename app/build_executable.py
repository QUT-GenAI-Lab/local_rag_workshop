'''
    RAGChat - a GUI for the quick development of RAG chatbots, used to
    teach the basic intuitions behind RAG LLMs.
    
    Copyright (C) 2025 QUT GenAI Lab

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    For more information, contact QUT GenAI lab via: genailab@qut.edu.au
'''

import os
import subprocess
import sys
import shutil


def create_executable():
    # Paths
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Ensure required directories exist
    os.makedirs(os.path.join(project_root, "dist"), exist_ok=True)

    # PyInstaller command
    pyinstaller_command = [
        "pyinstaller",
        "--onedir",  # Create a directory with executable and dependencies
        "--noconfirm",  # rewrite build and dist folders automatically without confirmation (your fault for deleting your shit brus).
        # Add data files and directories
        # "--add-data", f"chromadbs{os.pathsep}chromadbs",
        # "--add-data", f"chats{os.pathsep}chats",
        # Add model source viles
        # "--add-data", f"all-MiniLM-L6-v2{os.pathsep}all-MiniLM-L6-v2",
        # "--add-data", f"Llama-3.2-3B-Instruct.Q4_K_M.gguf{os.pathsep}.",
        # Add Python source files
        "--add-data", f"streamlit_gui.py{os.pathsep}.",
        "--add-data", f"chromadb_engine.py{os.pathsep}.",
        "--add-data", f"llama_engine.py{os.pathsep}.",
        "--add-data", f"RAG_backend.py{os.pathsep}.",
        # Additional options to handle specific libraries
        "--collect-all", "pypdf",
        "--collect-all", "chromadb",
        "--collect-all", "streamlit",
        "--collect-all", "sklearn",  # seems to be having issues with sklearn
        "--collect-all", "ollama",
        "--collect-all", "onnxruntime",
        "--collect-all", "docx2txt",
        "--collect-all", "umap",
        "--collect-all", "pynndescent",
        "--collect-all", "numba",
        "--collect-all", "tokenizers",  # windows-specific issues
        # Specify the entry point
        "run.py",
    ]

    # Run PyInstaller
    try:
        subprocess.run(pyinstaller_command, check=True)

        # Additional file copying
        dist_dir = os.path.join(
            project_root, "dist", "run"
        )  # change this for different build names, e.g. when you change name of run.py I guess

        print("Executable created successfully!")
        print("\nTo run the application:")
        print(
            f"Navigate to the '{dist_dir}' directory and execute the 'run' executable"
        )
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_executable()
