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

import streamlit as st

with st.spinner("loading ollama backend..."):
    from llama_engine import (
        check_ollama_install,
        check_and_serve_ollama,
        ollama_list_and_install_models,
        ollama_load_model,
        llama_chat_gen_streamed
    )

# initialise base directories
from os import path
import os

#only for errors
import chromadb

BASE_DIR = path.abspath(path.dirname(__file__))
CHAT_DIR = os.path.join(BASE_DIR, "chats")
os.makedirs(CHAT_DIR, exist_ok = True) #create chat dir if doesn't exist

# janky way of starting llama chat engine
if "initialisation" not in st.session_state:
    st.session_state.initialisation = True

if "ollama_model" not in st.session_state:
    st.session_state.ollama_model = "llama3.2"


@st.dialog("Initialize Ollama engine")
def initialise_ollama():
    with st.spinner(
        "loading ollama (this may take a while on first run - we'll need to download a default model!)..."
    ):
        if not check_ollama_install():
            st.error(
                "You don't have ollama installed! Install from [here](https://ollama.com/) and restart"
            )
        else:
            check_and_serve_ollama()
            chat_model = st.selectbox(
                "Select model to run on ollama",
                options=ollama_list_and_install_models(),
                index=0,
            )
            if st.button("Initialise Ollama chat"):
                st.session_state.ollama_model = chat_model
                ollama_load_model(chat_model)
                st.session_state.initialisation = False
                st.rerun()


if st.session_state.initialisation == True:
    st.title("Initialise Ollama!")
    initialise_ollama()

if st.session_state.initialisation == False:
    # rest of code
    with st.spinner("loading packages..."):
        from RAG_backend import create_injection_prompt
        from chromadb_engine import (
            client,
            list_all_collections,
            make_db_from_csv,
            make_db_from_docx,
            make_db_from_pdf,
            make_db_from_txt,
            create_df_from_chromadb_get,
            create_df_from_chromadb_query,
            visualise_embeddings_3d,
            delete_collection,
        )
        import pandas as pd
        import pickle
        import re

    def load_chat_histories():
        chathist_list = [file for file in os.listdir(CHAT_DIR) if ".pickle" in file]
        chathist_returndict = {}
        for chatfile in chathist_list:
            chatname = chatfile.replace(".pickle", "")
            with open(os.path.join(CHAT_DIR, chatfile), "rb") as f:
                chathist_returndict[chatname] = pickle.load(f)
        return chathist_returndict

    with st.spinner("loading chat history..."):
        init_chat_hist = load_chat_histories()
    # Initialize session state variables
    if "all_chat_histories" not in st.session_state:
        st.session_state.all_chat_histories = init_chat_hist

    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None

    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

    if "use_rag" not in st.session_state:
        st.session_state.use_rag = True

    # jank way to load chromadb on startup
    if "chromadb_loaded" not in st.session_state:
        st.session_state.chromadb_loaded = False

    if not st.session_state.chromadb_loaded:
        # load_chromadb() <- disabling for now - don't think it's necessary
        st.session_state.chromadb_loaded=True

    def save_chat_hist(chat_name):
        chat_to_save = st.session_state.all_chat_histories[chat_name]
        with open(os.path.join(CHAT_DIR, f"{chat_name}.pickle"), "wb") as f:
            pickle.dump(chat_to_save, f)

    def delete_chat_hist(chat_name):
        chat_hist_path = os.path.join(CHAT_DIR, f"{chat_name}.pickle")
        os.remove(chat_hist_path)

    def delete_chromadb_collection(collection_name):
        # delete all chat histories with collection name in it
        all_histories = st.session_state.all_chat_histories
        list_of_relevant_chats = [
            x
            for x in list(all_histories.keys())
            if all_histories[x]["selected_db"] == collection_name
        ]
        for chatname in list_of_relevant_chats:
            del st.session_state.all_chat_histories[chatname]
            delete_chat_hist(chatname)
        delete_collection(collection_name)

    @st.dialog("Create a new vector database")
    def create_new_vectordb():
        name = st.text_input("Put your database name here!")
        uploaded_file = st.file_uploader(
            "Upload your .docx, .csv, .pdf, or .txt files here!",
            accept_multiple_files=False,
        )
        if uploaded_file:
            filename = uploaded_file.name

            # options for .csv
            if ".csv" in filename[-4:]:
                cols = list(pd.read_csv(uploaded_file).columns)
                embedding_column = st.selectbox(
                    "Select column to generate embedding from", options=cols, index=0
                )
                if st.button("create database from csv!"):
                    if not re.match("^[a-zA-Z0-9_-]*$", name):
                        st.error(
                            "Chat history name contains characters other than alphanumeric, underscores, and/or hyphens. Please change the name to only include the aforementioned characters"
                        )

                    elif name in list_all_collections():
                        st.error(
                            "db with that name already exists! Use a different name."
                        )

                    else:
                        with st.spinner(
                            "creating vector database (this can take really long depending on the filesize!)..."
                        ):
                            uploaded_file.seek(0)  # reset pointer I guess?
                            make_db_from_csv(uploaded_file, embedding_column, name)
                        st.rerun()

            # options for docx
            elif (
                ".doc" in filename[-5:]
            ):  # jankily allowing for detection of .doc and .docx
                split_length = st.slider(
                    "number of words per embedding split", 32, 256, 128, 1
                )
                if st.button("create database from word document!"):

                    if not re.match("^[a-zA-Z0-9_-]*$", name):
                        st.error(
                            "Chat history name contains characters other than alphanumeric, underscores, and/or hyphens. Please change the name to only include the aforementioned characters"
                        )

                    elif name in list_all_collections():
                        st.error(
                            "db with that name already exists! Use a different name."
                        )
                    else:
                        with st.spinner(
                            "creating vector database (this can take really long depending on the filesize!)..."
                        ):
                            make_db_from_docx(uploaded_file, name, split_length)
                        st.rerun()

            # options for .txt
            elif ".txt" in filename[-4:]:
                split_length = st.slider(
                    "number of words per embedding split", 32, 256, 128, 1
                )
                if st.button("create database from text document!"):
                    if not re.match("^[a-zA-Z0-9_-]*$", name):
                        st.error(
                            "Chat history name contains characters other than alphanumeric, underscores, and/or hyphens. Please change the name to only include the aforementioned characters"
                        )

                    elif name in list_all_collections():
                        st.error(
                            "db with that name already exists! Use a different name."
                        )

                    else:
                        with st.spinner(
                            "creating vector database (this can take really long depending on the filesize!)..."
                        ):
                            make_db_from_txt(uploaded_file, name, split_length)
                        st.rerun()

            # options for pdf
            elif ".pdf" in filename[-4:]:
                split_length = st.slider(
                    "number of words per embedding split", 32, 256, 128, 1
                )
                if st.button("create database from pdf document!"):
                    if not re.match("^[a-zA-Z0-9_-]*$", name):
                        st.error(
                            "Chat history name contains characters other than alphanumeric, underscores, and/or hyphens. Please change the name to only include the aforementioned characters"
                        )

                    elif name in list_all_collections():
                        st.error(
                            "db with that name already exists! Use a different name."
                        )

                    else:
                        with st.spinner(
                            "creating vector database (this can take really long depending on the filesize!)..."
                        ):
                            make_db_from_pdf(uploaded_file, name, split_length)
                    st.rerun()

    @st.dialog("Create a new chat history")
    def create_new_chat_hist():
        try:
            name = st.text_input("Put your chat name here!", max_chars=156)
            selected_db = st.selectbox(
                "select injection database",
                options=list_all_collections(),
                index=0,  # defaults to first example injection database
            )
            with st.expander("Advanced Options 🤓", expanded = False):
                system_prompt = st.text_area("Put your system prompt here!", 
                                             value="You are a helpful chatbot assistant.",
                                             max_chars=750)
                injection_template = st.text_area(
                    "Put your injection template here! REMEMBER, MUST have {INJECT_TEXT} and {USER_MESSAGE} strings!",
                    value="""Documents to refer to:
    
{INJECT_TEXT}

Message to respond to:

{USER_MESSAGE}""",
                    max_chars=750,
                )
    
                # checking if there are metadatas/"columns" that have options for injection, making selectbox if so
                quick_sample = client.get_collection(selected_db).get(limit=5)
                if not all(x == None for x in quick_sample["metadatas"]):
                    init_list = [None]
                    init_list.extend(list(
                            quick_sample["metadatas"][0].keys()
                        )
                                    )# assuming first item in quick_sample has all metadatas, which as of 03/01/2025, is correct
                    injection_col = st.selectbox(
                        "select column for injection into RAG",
                        options=init_list,  
                        index=0, #first item is None, so default doc is used for injection
                    )
    
            if st.button("Create", use_container_width=True):
                # error checking
                if not re.match("^[a-zA-Z0-9_-]*$", name):
                    st.error(
                        "Chat history name contains characters other than alphanumeric, underscores, and/or hyphens. Please change the name to only include the aforementioned characters"
                    )
                elif name in list(st.session_state.all_chat_histories.keys()):
                    st.error(
                        "Chat history with that name already exists! Choose a different chat name."
                    )
                elif (
                    "{INJECT_TEXT}" not in injection_template
                    or "{USER_MESSAGE}" not in injection_template
                ):
                    st.error(
                        "Injection template format invalid! Remember, put {INJECT_TEXT} where you'd like your RAG results to be injected, and {USER_MESSAGE} where you'd like your input message to be returned. Remember to include the curly brackets!"
                    )
                else:
                    if all([name, system_prompt, injection_template, selected_db]):
                        init_messages = [
                            {"role": "system", "content": system_prompt},
                            # {"role": "assistant", "content": "Hi there, how can I help you today?"}
                        ]
                        st.session_state.all_chat_histories[name] = {
                            "normal_hist": init_messages.copy(),
                            "RAG_hist": init_messages.copy(),
                            "system_prompt": system_prompt,
                            "injection_template": injection_template,
                            "selected_db": selected_db,
                            "injection_col": (
                                None if "injection_col" not in locals() else injection_col
                            ),  # check if injection_col var exists
                        }
                        st.session_state.current_chat = name
                        # save chat history now:
                        save_chat_hist(name)
                        st.rerun()
    
                    else:  # catchall error (so janky - I'm so sorry)
                        st.error(
                            "Missing chat name, system prompt, injection template, and/or injection database! Take a closer look at your selections."
                        )
        except chromadb.errors.InvalidCollectionException:
            st.error(
                    "You don't have any databases! Create a database first!"
                    )

    @st.dialog("Explore your ChromaDB databases", width="large")
    def chromadb_explore():
        try:
            default_db = st.session_state.all_chat_histories[st.session_state.current_chat][
                "selected_db"
            ] if st.session_state.current_chat is not None else 0
            default_index = list_all_collections().index(default_db) if default_db != 0 else 0
            selected_db = st.selectbox(
                "Collection:",
                options=list_all_collections(),
                index=default_index,
                key="collection_selector",
            )
    
            tab1, tab2 = st.tabs(["Query", "Visualize"])
    
            with tab1:
                chromadb_col1, chromadb_col2 = st.columns([6, 1])
    
                with chromadb_col1:
                    query_text = st.text_input("Query:", key="query_text")
                with chromadb_col2:
                    n_results = st.number_input(
                        "No. Results:", min_value=1, max_value=50, value=5, step=1
                    )
    
                # Initialize collection
                collection = client.get_collection(selected_db)
    
                # Display either query results or all data based on whether there's a query
                if query_text:
                    results = collection.query(
                        query_texts=[query_text], n_results=n_results
                    )
    
                    # Display results with similarity scores
                    if results["documents"] and results["documents"][0]:
                        st.dataframe(
                            create_df_from_chromadb_query(results), use_container_width=True
                        )
                    else:
                        st.write("No results found")
                else:
                    # Show all documents if no query
                    data = collection.get()
                    st.dataframe(
                        create_df_from_chromadb_get(data), use_container_width=True
                    )
    
                collection_count = collection.count()
                st.write(f"Total documents: {collection_count}")
    
            with tab2:
                st.subheader("3D Embedding Visualization")
                st.markdown("Explore the embedding space of your vector database!")
                st.info("Drag to rotate, scroll to zoom, double-click to reset view")
                with st.spinner("generating 3D UMAP of embeddings..."):
                    try:
                        fig = visualise_embeddings_3d(collection)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Unable to visualize collection: {str(e)}")
        except chromadb.errors.InvalidCollectionException:
            st.error(
                    "You don't have any databases! Create a database first!"
                    )

    @st.dialog("Are you sure you want to delete this database?")
    def delete_database_confirmation(collection_name):
        st.write(
            f"Are you sure you want to delete {collection_name} database? Doing so will erase the database AS WELL AS ALL ASSOCIATED CHATS!!! THIS ACTION CANNOT BE UNDONE!!!"
        )
        if st.button("YES, I WANT TO DELETE THIS DATABASE! 💀"):
            delete_chromadb_collection(collection_name)
            st.session_state.current_chat = None  # temporary catchall for if you're deleting a chat wiht the same db you're deleting
            st.rerun()

    # Sidebar with chat management in expander
    with st.sidebar:
        st.title("RAGChat")

        st.button(
            "RAG: " + ("ON" if st.session_state.use_rag else "OFF"),
            on_click=lambda: setattr(
                st.session_state, "use_rag", not st.session_state.use_rag
            ),
            type=("primary" if st.session_state.use_rag else "secondary"),
            use_container_width=True,
        )
        with st.expander("Chat Management", expanded=True):
            if st.button("Create New Chat"):
                create_new_chat_hist()

            if st.session_state.all_chat_histories:
                selected_chat = st.selectbox(
                    "Select Chat",
                    options=list(st.session_state.all_chat_histories.keys()),
                    index=(
                        list(st.session_state.all_chat_histories.keys()).index(
                            st.session_state.current_chat
                        )
                        if st.session_state.current_chat
                        else 0
                    ),
                )

                if selected_chat != st.session_state.current_chat:
                    st.session_state.current_chat = selected_chat
                    st.rerun()

                if len(st.session_state.all_chat_histories) > 1:
                    if st.button("Delete Current Chat"):
                        delete_chat_hist(st.session_state.current_chat)
                        del st.session_state.all_chat_histories[
                            st.session_state.current_chat
                        ]
                        st.session_state.current_chat = list(
                            st.session_state.all_chat_histories.keys()
                        )[0]
                        st.rerun()

        with st.expander("RAG query options", expanded=False):
            num_return = st.slider("Max number of items to inject", 1, 4, 3, 1)
            max_dist = st.slider(
                "Maximum distance of object from query", 0.5, 2.5, 2.0, 0.1
            )

        if st.button("Create a new Vector Database", use_container_width = True):
            # st.rerun()
            create_new_vectordb()

        if st.button("Explore existing Databases", use_container_width = True):
            chromadb_explore()

        with st.expander("DB management", expanded=False):
            db_to_delete = st.selectbox(
                "Select DB to delete",
                options=list_all_collections(),
                index=None, #quick fix of db errors 
            )
            
            if st.button("DELETE DATABASE! 💀", type="secondary"):
                delete_database_confirmation(db_to_delete)

    # Display function for chat histories
    def display_chat_hist(mode="normal_hist"):
        if st.session_state.current_chat:
            current_messages = st.session_state.all_chat_histories[
                st.session_state.current_chat
            ][mode]
            for message in current_messages:
                if message["role"] != "system":
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

    # Main chat interface with tabs
    normal_tab, rag_tab = st.tabs(["Default", "RAG history"])
    with normal_tab:
        display_chat_hist("normal_hist")

    with rag_tab:
        display_chat_hist("RAG_hist")

    # Single chat input and response handling
    if st.session_state.current_chat and not st.session_state.is_generating:

        prompt = st.chat_input("What is up?", max_chars=3000)

        if prompt:
            # Get both histories
            chat_histories = st.session_state.all_chat_histories[
                st.session_state.current_chat
            ]
            with st.chat_message("user"):
                st.markdown(prompt)

            # Create normal and RAG versions of the message
            normal_message = {"role": "user", "content": prompt}
            injection_prompt = create_injection_prompt(  #### HAVE THIS DICTATED BY STUFF IN THE SIDEBAR!
                chat_histories["selected_db"],
                prompt,
                num_return=num_return,
                max_dist=max_dist,
                inject_col=chat_histories["injection_col"],
                inject_template=chat_histories["injection_template"],
            )
            rag_message = {"role": "user", "content": injection_prompt}

            # Add messages to respective histories
            if st.session_state.use_rag:
                chat_histories["normal_hist"].append(normal_message)
                chat_histories["RAG_hist"].append(rag_message)
            else:
                chat_histories["normal_hist"].append(normal_message)
                chat_histories["RAG_hist"].append(normal_message)

            # Display user message

            st.session_state.is_generating = True
            st.rerun()

    if st.session_state.current_chat and st.session_state.is_generating:
        prompt = st.chat_input("Generating...", disabled=st.session_state.is_generating)
        chat_histories = st.session_state.all_chat_histories[
            st.session_state.current_chat
        ]

        # Generate response using RAG-enhanced prompt
        with st.chat_message("assistant"):
            with st.spinner(
                "Responding..."
            ):  # <--- POTENTIALLY REMOVE FOR OLLAMA because it's so fast
                # Use RAG history for generation
                # NOTE - this could blow out memory quite quickly??? Be sure to change context length et cetera.
                if st.session_state.use_rag:
                    input_hist = chat_histories["RAG_hist"]
                else:
                    input_hist = chat_histories["normal_hist"]
                generated_response = llama_chat_gen_streamed(
                    input_hist, model=st.session_state.ollama_model
                )
                response = st.write_stream(generated_response)

        # Add response to both histories
        assistant_message = {"role": "assistant", "content": response}
        chat_histories["normal_hist"].append(assistant_message)
        chat_histories["RAG_hist"].append(assistant_message)
        save_chat_hist(st.session_state.current_chat)
        st.session_state.is_generating = False
        st.rerun()
        
    #allow user to delete just the chat history
    if st.session_state.current_chat and len(st.session_state.all_chat_histories[
            st.session_state.current_chat
        ]["normal_hist"])>=2:
        if st.button("Restart chat 🔄️", use_container_width = True):
            chat_histories = st.session_state.all_chat_histories[
                    st.session_state.current_chat
                ]
            chat_histories["normal_hist"]=[
                        {"role": "system", "content": chat_histories["system_prompt"]},
                    ]
            chat_histories["RAG_hist"]=[
                        {"role": "system", "content": chat_histories["system_prompt"]},
                    ]
            save_chat_hist(st.session_state.current_chat)
            st.rerun()
