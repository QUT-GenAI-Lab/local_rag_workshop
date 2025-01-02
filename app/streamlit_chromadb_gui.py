import streamlit as st
from chromadb_engine import *
import pandas as pd

st.title("ChromaDB Explorer")

chromadb_col1, chromadb_col2, chromadb_col3 = st.columns([3,3,1])
# Collection selection
with chromadb_col1:
    selected_db = st.selectbox(
        "Collection:",
        options=list_all_collections(),
        index=0,
        key='collection_selector'
    )
with chromadb_col2:
    query_text = st.text_input("Query:", key='query_text')

with chromadb_col3:
    n_results = st.number_input("No. Results:", min_value=1, max_value=50, value=5, step = 1)

# Initialize collection
collection = client.get_collection(selected_db)

# Display either query results or all data based on whether there's a query
if query_text:
    results = collection.query(query_texts = [query_text], 
                               n_results = n_results)
    
    # Display results with similarity scores
    if results['documents'] and results['documents'][0]:
        st.dataframe(create_df_from_chromadb_query(results), use_container_width=True)
    else:
        st.write("No results found")
else:
    # Show all documents if no query
    data = collection.get()
    st.dataframe(create_df_from_chromadb_get(data), use_container_width=True)

# # Add collection info
# st.sidebar.subheader("Collection Info")
collection_count = collection.count()
st.write(f"Total documents: {collection_count}")