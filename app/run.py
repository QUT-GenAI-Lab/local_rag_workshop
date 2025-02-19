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

import sys
from streamlit.web.cli import main

# search for streamlit_gui.py (have to do this because run contexts are different across OSes
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


if __name__ == "__main__":
    # Force streamlit to use the proper CLI args
    sys.argv = [
        "streamlit", "run", GUI_DIR,
        #flags
        "--global.developmentMode", "false",
        "--server.enableCORS", "true",
        "--server.enableXsrfProtection", "true",
    ]
    main()
