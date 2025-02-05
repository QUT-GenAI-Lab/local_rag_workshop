# Local RAG workshop app
This is an app built for the local RAG workshop being run by QUT's GenAI lab.

This is a barebones app that allows non-technical users to build their own RAG-enabled LLM chats. The RAG backend is ChromaDB (using their default all-MiniLM-L6-v2 embedding model), whereas the LLM chat backend is enabled by a separate, external install of Ollama.

# Features
- drag-and-drop Vector Database creation for .doc/.docx, .pdf, .txt, and .csv files
- sliders for Vector DB injection return (number of items injected, maximum distance from query)
- support for multiple persistent chat histories and databases over sessions
- can tab between RAG and non-RAG chat histories to see exactly what has been injected into prompt
- can toggle on/off RAG enablement
- explore VectorDBs with queries and 3D UMAP visualisation of embedding space

# Build instructions
This codebase was built on python 3.11, but also (accidentally) confirmed working on python 3.12. Should also work on Python 3.10.

### Building the app
Currently, if you know python (which if you're on github, I'm imagining you do), you just need to install everything in requirements.txt and you can either navigate to `/app` and then run `python3 run.py` or  `streamlit run streamlit_gui.py` to boot the app.

To 'compile' into an executable file for the OS+instruction set you're currently running on, navigate to `/app` and run `python3 build_executable.py`, which will execute the relevant PyInstaller command to build the app into a portable executable file. The output will be in `/app/dist/run`, which is a directory which will contain the executable `run` file, as well as an `_internal` directory for relevant packages and other stuff. Moving the `/run' folder around will allow you to run the RAG GUI on whatever computer has an Ollama install!

### Pre-reqs for running the app
- Ollama installed

## Compatibility
Currently, 'compilation' of functioning executables are confirmed on:
- Windows x86/64
- Linux x86/64
- MacOS ARM
- MacOS x86/64
