import streamlit as st
from chromadb_engine import *
import pandas as pd

st.title("testing")

def create_df_from_chromadb(db_name):
    data = client.get_collection(db_name).get()
    documents_df = pd.DataFrame(data['documents'], columns=['Documents that were embedded'])
    if not all(x==None for x in data['metadatas']): #this is assuming that all metadata entries line up and have "None" in each dict entry where there's no data, rather than that key missing entirely. This should happen upstream from default pandas behaviour, but we'll see.
        metadatas_df = pd.DataFrame(data['metadatas'])
        documents_df = pd.concat([documents_df, metadatas_df], axis=1)

    return documents_df


selected_db = st.selectbox(
    "select injection database",
    options = list_all_collections(),
    index = 0 #defaults to first example injection database
)

st.dataframe(create_df_from_chromadb(selected_db))


