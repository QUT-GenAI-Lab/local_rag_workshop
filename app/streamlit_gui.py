import streamlit as st
from llama_engine import llama_chat_gen_streamed
from RAG_backend import create_injection_prompt
from chromadb_engine import list_all_collections, make_db_from_csv, make_db_from_docx, make_db_from_pdf, make_db_from_txt
import pandas as pd

# Initialize session state variables
if "all_chat_histories" not in st.session_state:
    st.session_state.all_chat_histories = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "new_chat_name" not in st.session_state:
    st.session_state.new_chat_name = ""

if "use_rag" not in st.session_state:
    st.session_state.use_rag = True

@st.dialog("Create a new vector database")
def create_new_vectordb():
    name = st.text_input("Put your database name here!")
    uploaded_file = st.file_uploader("Upload your .docx, .csv, .pdf, or .txt files here!", accept_multiple_files=False)
    if uploaded_file:
        filename = uploaded_file.name
        
        # options for .csv
        if '.csv' in filename[-4:]:
            cols = list(pd.read_csv(uploaded_file).columns)
            embedding_column = st.selectbox(
                "Select column to generate embedding from",
                options = cols,
                index = 0
            )
            if st.button("create database from csv!"):
                uploaded_file.seek(0) #reset pointer I guess?
                make_db_from_csv(uploaded_file, embedding_column, name)
                st.rerun()

        # options for docx
        elif '.doc' in filename[-5:]: #jankily allowing for detection of .doc and .docx
            split_length = st.slider("number of words per embedding split", 32, 256, 128, 1)
            if st.button("create database from word document!"):
                make_db_from_docx(uploaded_file, name, split_length)
                st.rerun()

        #options for .txt
        elif '.txt' in filename[-4:]:
            split_length = st.slider("number of words per embedding split", 32, 256, 128, 1)
            if st.button("create database from text document!"):
                make_db_from_txt(uploaded_file, name, split_length)
                st.rerun()

        #options for pdf
        elif '.pdf' in filename[-4:]:
            split_length = st.slider("number of words per embedding split", 32, 256, 128, 1)
            if st.button("create database from pdf document!"):
                make_db_from_pdf(uploaded_file, name, split_length)
                st.rerun()

    

@st.dialog("Create a new chat history")
def create_new_chat_hist():
    name = st.text_input("Put your chat name here!")
    system_prompt = st.text_area("Put your system prompt here!")
    injection_template = st.text_area("Put your injection template here! REMEMBER, MUST have {INJECT_TEXT} and {USER_MESSAGE} strings!")
    selected_db = st.selectbox(
        "select injection database",
        options = list_all_collections(),
        index = 0 #defaults to first example injection database
    )
        
    if st.button("Create", use_container_width=True):
        if all([name, system_prompt, injection_template, selected_db]):
            init_messages = [
                {"role": "system", "content": system_prompt},
                # {"role": "assistant", "content": "Hi there, how can I help you today?"}
            ]
            st.session_state.all_chat_histories[name] = {
                'normal_hist': init_messages.copy(),
                'RAG_hist': init_messages.copy(),
                'system_prompt': system_prompt,
                'injection_template': injection_template,
                'selected_db': selected_db,
            }
            st.session_state.current_chat = name
            st.rerun()
            
        elif all(string in injection_template for string in ['{INJECT_TEXT}', '{USER_MESSAGE}']):
            st.error("Injection template format invalid! Remember, put {INJECT_TEXT} where you'd like your RAG results to be injected, and {USER_MESSAGE} where you'd like your input message to be returned. Remember to include the curly brackets!")
        else:
            st.error("Missing chat name, system prompt, injection template, and/or injection database! Take a closer look at your selections.")

# Initial chat creation dialog
# if len(st.session_state.all_chat_histories) == 0:
#     create_new_chat_hist()
# removed for now as it's causing issues with dialogue boxes and st.rerun()

# Sidebar with chat management in expander
with st.sidebar:
    st.title("llm chat demo")

    st.button("RAG: " + ("ON" if st.session_state.use_rag else "OFF"), 
              on_click=lambda: setattr(st.session_state, 'use_rag', not st.session_state.use_rag), 
              type = ("primary" if st.session_state.use_rag else "secondary"),
              use_container_width=True)
    with st.expander("Chat Management", expanded=True):
        if st.button("Create New Chat"):
            create_new_chat_hist()
        
        if st.session_state.all_chat_histories:
            selected_chat = st.selectbox(
                "Select Chat",
                options=list(st.session_state.all_chat_histories.keys()),
                index=list(st.session_state.all_chat_histories.keys()).index(st.session_state.current_chat) if st.session_state.current_chat else 0
            )
            
            if selected_chat != st.session_state.current_chat:
                st.session_state.current_chat = selected_chat
                st.rerun()

            if len(st.session_state.all_chat_histories) > 1:
                if st.button("Delete Current Chat"):
                    del st.session_state.all_chat_histories[st.session_state.current_chat]
                    st.session_state.current_chat = list(st.session_state.all_chat_histories.keys())[0]
                    st.rerun()


    with st.expander("RAG query options", expanded = False):
        num_return = st.slider("Max number of items to inject", 1, 4, 3, 1)
        max_dist = st.slider("Maximum distance of object from query", 0.5, 2.5, 2.0, 0.1)

    if st.button("Create a new Vector Database"):
        # st.rerun()
        create_new_vectordb()

# Display function for chat histories
def display_chat_hist(mode='normal_hist'):
    if st.session_state.current_chat:
        current_messages = st.session_state.all_chat_histories[st.session_state.current_chat][mode]
        for message in current_messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

# Main chat interface with tabs
normal_tab, rag_tab = st.tabs(["Default", "RAG history"])
with normal_tab:
    display_chat_hist('normal_hist')

with rag_tab:
    display_chat_hist('RAG_hist')

# Single chat input and response handling
if st.session_state.current_chat and not st.session_state.is_generating:

    prompt = st.chat_input("What is up?")

        
    if prompt:
        # Get both histories
        chat_histories = st.session_state.all_chat_histories[st.session_state.current_chat]
        
        # Create normal and RAG versions of the message
        normal_message = {"role": "user", "content": prompt}
        injection_prompt = create_injection_prompt( #### HAVE THIS DICTATED BY STUFF IN THE SIDEBAR!
            chat_histories['selected_db'], 
            prompt, 
            num_return = num_return, 
            max_dist = max_dist, 
            inject_col = None, #how do I do this?????? 
            inject_template=chat_histories['injection_template']
        )
        rag_message = {"role": "user", "content": injection_prompt}

        # Add messages to respective histories
        if st.session_state.use_rag:
            chat_histories['normal_hist'].append(normal_message)
            chat_histories['RAG_hist'].append(rag_message)
        else:
            chat_histories['normal_hist'].append(normal_message)
            chat_histories['RAG_hist'].append(normal_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.is_generating = True
        st.rerun()

if st.session_state.current_chat and st.session_state.is_generating:
    prompt = st.chat_input("Generating...", disabled = st.session_state.is_generating)
    chat_histories = st.session_state.all_chat_histories[st.session_state.current_chat]
    
    # Generate response using RAG-enhanced prompt
    with st.chat_message("assistant"):
        with st.spinner('Responding...'):
            # Use RAG history for generation
            #NOTE - this could blow out memory quite quickly??? Be sure to change context length et cetera.
            if st.session_state.use_rag:
                input_hist = chat_histories['RAG_hist']
            else:
                input_hist = chat_histories['normal_hist']
            generated_response = llama_chat_gen_streamed(input_hist) 
            response = st.write_stream(generated_response)
    
    # Add response to both histories
    assistant_message = {"role": "assistant", "content": response}
    chat_histories['normal_hist'].append(assistant_message)
    chat_histories['RAG_hist'].append(assistant_message)
    
    st.session_state.is_generating = False
    st.rerun()