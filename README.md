# local_rag_workshop
development for local RAG workshop being run by QUT GenAI lab

# High level overview
The intention of this product is to demonstrate how RAGs work.

This product needs to:
- show the prompt template (and allow for the user to edit it)
- allow for some amount of flexibility in terms of what gets returned/injected???? (i.e. have a threshold for cosine sim for how many results get returned, or just a general min and/or max number of injected things)
  - also allow for physical exploration of injections, as well as the database in general 
- STRETCH: do I also allow for novel prompt chains??? Like allow the user to have the model run again on the injected prompts to summarise or evaluate how correct they are before injection, stuff like that? Idk how I'd do that)

- Give intuitive GUI-based interactions for building the Database for the RAG, and allow it to be dynamically updated, saved/loaded, replaced etc.
  - Allow for multiple input datatypes (e.g. .csv, excel, text,  pdf, docx, idk what else)
  - finagle how long the text chunks are????
 
- Expose as much of the generation process to the GUI???
  - e.g. show what the final input prompt looks like?
  - ??????? what else? IDK

# The technical approach
- LLM model: llama 3.2 1b instruct GGUF running on llama.cpp at q6???:
  - llama-cpp-python doco: https://llama-cpp-python.readthedocs.io/en/latest/
  - STRETCH: get this running across all potential hardware platforms -currently only running on CPU :')
 
- RAG model: MiniLM L12 v2 dot product: https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2
  - STRETCH: get this running on llama.cpp: https://huggingface.co/HowardC/all-MiniLM-L12-v2-Q4_K_M-GGUF
 
- Interface: streamlit (for now), maybe gradio? I know nothing about gradio
