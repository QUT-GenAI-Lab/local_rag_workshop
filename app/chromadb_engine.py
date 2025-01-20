import chromadb
import pandas as pd
from pypdf import PdfReader
import docx2txt

import numpy as np
import plotly.express as px
from umap.umap_ import UMAP

from os import path
import os

BASE_DIR = path.abspath(path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "chromadbs")

# load persistent dir
client = chromadb.PersistentClient(path=DB_DIR)

# generic funcs

def batch_upsert(db_name, documents, ids, metadatas = None,):
    """
    function to batch upsert into chromadb (currently has a limit of 5461 docs per upsert, for some reason)
    """

    # create or upsert into collection
    collection = client.get_or_create_collection(name=db_name)

    batch_size = 5000 #somewhat arbitrarily lower than 5461, but I just like a nice round number lol

    documents_batch = [documents[i:i+batch_size] for i in range(0, len(documents), batch_size)]
    ids_batch = [ids[i:i+batch_size] for i in range(0, len(ids), batch_size)]
    if metadatas is not None:
        metadatas_batch = [metadatas[i:i+batch_size] for i in range(0, len(metadatas), batch_size)]
        for i in range(len(ids_batch)):
            collection.upsert(documents=documents_batch[i],
                              metadatas=metadatas_batch[i],
                              ids=ids_batch[i]
                             )
    else:
        for i in range(len(ids_batch)):
            collection.upsert(documents=documents_batch[i],
                                 ids=ids_batch[i]
                                ) 

    return collection

def clean_utf8(input_str):
    """
    function to clean strings to UTF-8 compatible encoding.
    """
    input_str = bytes(input_str, "utf-8").decode("utf-8", "ignore")
    return input_str


def split_texts(input_str: str, split_length: int = 128) -> list[str]:
    """
    takes a text input and splits it into a list of strings of 128 words (or less for the last entry if it doesn't make it up to 128 words)

    inputs:
        - input_str: str - candidate string to split
        - split_length: int - number of words per split

    outputs:
        - splitlist: list[str] - list of split strings generated from inputs, which each string being split_length number of words
    """
    wordlist = input_str.split(" ")
    splitlist = [
        " ".join(wordlist[i : i + split_length])
        for i in range(0, len(wordlist), split_length)
    ]
    return splitlist


### FUNCS FOR IMPORTING AND STUFF


def switch_db(db_name: str):
    """
    abstracting function to switch collections, but I've called them dbs because silly me.

    unsure how necessary it is.

    inputs:
        - db_name: str - name of db to connect to
    outputs:
        - collection - connection to ChromaDB client collection (should it exist
    """
    collection = client.get_collection(name=db_name)
    return collection


def make_db_from_pdf(
    pdf_dir,
    db_name: str,
    split_length: int = 128,
):
    """
    function which creates a db from pdf.

    inputs:
        - pdf_dir: str - directory where pdf can be read from
        - db_name: str - name of db (really just name of collection)
        - split_length: int - length of each chunk to be used in injection/embedding

    outputs:
        - collection: returns ChromaDB collection that was just created.

    """

    # make docs for embedding
    reader = PdfReader(pdf_dir)
    pagetexts = []
    total_splits = []
    for page in reader.pages:
        text = page.extract_text()
        text = text.replace("\n", " ")  # clean text of new lines
        text = clean_utf8(text)
        pagetexts.append(text)

    for pagetext in pagetexts:
        text_chunks = split_texts(pagetext, split_length)
        total_splits.extend(text_chunks)

    # get num of ids for chromadb creation
    ids = [f"id{num}" for num in range(len(total_splits))]

    # create (or upsert into) chromadb
    collection = batch_upsert(db_name, total_splits, ids, metadatas = None)

    return collection


def make_db_from_csv(csv_dir, embedding_col: str, db_name: str):
    """
    function which creates a db from csv, preserving all cols in csv as metadatas.

    inputs:
        - csv_dir: str - directory where csv can be read from
        - embedding_col: str - name of column with text in it that should be embedded
        - db_name: str - name of ChromaDB collection

    outputs:
        - collection: returns ChromaDB collection that was just created.
    """
    # ingest and prepare data
    init_df = pd.read_csv(csv_dir)
    documents = list(init_df[embedding_col])
    documents = [clean_utf8(str(x)) for x in documents]
    # add metadatas for select querying I guess, or allowing to pick what we query
    metadatas = [init_df.loc[x].to_dict() for x in range(len(init_df))]
    ids = [f"id{num}" for num in range(len(init_df))]

    collection = batch_upsert(db_name, documents, ids, metadatas)

    return collection


def make_db_from_docx(
    docx_dir,
    db_name: str,
    split_length: int = 128,
):
    """
    func to create db from docx file.

    inputs:
        - docx_dir: str - directory where docx file needs to be read from
        - db_name: str - name of ChromaDB collection
        - split_length: int - length of each chunk of text to be embedded

    outputs:
        - collection: returns ChromaDB collection that was just created.
    """
    text = docx2txt.process(docx_dir)
    text = clean_utf8(text)
    split_list = split_texts(text, split_length)
    ids = [f"id{num}" for num in range(len(split_list))]

    collection = batch_upsert(db_name, split_list, ids, metadatas = None)

    return collection


def make_db_from_txt(
    txt,
    db_name: str,
    split_length: int = 128,
):
    """
    func to create db from txt file.

    inputs:
        - txt_dir: str - directory where txt file needs to be read from
        - db_name: str - name of ChromaDB collection
        - split_length: int - length of each chunk of text to be embedded

    outputs:
        - collection: returns ChromaDB collection that was just created.
    """
    # with open(txt_dir, 'r') as f:
    #     text = f.read()

    text = txt.read().decode("utf-8").replace("\n", " ")
    text = clean_utf8(text)
    split_list = split_texts(text, split_length)
    ids = [f"id{num}" for num in range(len(split_list))]

    collection = batch_upsert(db_name, split_list, ids, metadatas = None)

    return collection


def list_all_collections():
    """
    lists all collections currently available on chromadb
    """
    collections_list = [x.name for x in client.list_collections()]
    return collections_list


def create_df_from_chromadb_get(data):
    """
    turns returned collection.get() into a pd dataframe.
    """
    documents_df = pd.DataFrame(
        data["documents"], columns=["Documents that were embedded"]
    )
    if not all(x == None for x in data["metadatas"]):
        metadatas_df = pd.DataFrame(data["metadatas"])
        documents_df = pd.concat([documents_df, metadatas_df], axis=1)
    return documents_df


def create_df_from_chromadb_query(results):
    """
    turns returned collection.query() into a pd dataframe.
    """
    results_df = pd.DataFrame(
        {
            "Document": results["documents"][0],
            "Distance": (
                results["distances"][0]
                if "distances" in results
                else ["N/A"] * len(results["documents"][0])
            ),
        }
    )

    if results["metadatas"] and not all(x == None for x in results["metadatas"][0]):
        metadata_df = pd.DataFrame(results["metadatas"][0])
        results_df = pd.concat([results_df, metadata_df], axis=1)

    return results_df


def visualise_embeddings_3d(collection):
    """
    Create an interactive 3D visualisation of the embeddings using UMAP and Plotly
    """
    # Get embeddings
    data = collection.get(include=["embeddings", "documents"])
    embeddings = np.array(data["embeddings"])

    # Reduce dimensionality to 3D with UMAP
    umap = UMAP(n_components=3, n_jobs=-1)
    embeddings_3d = umap.fit_transform(embeddings)

    # Create dataframe for plotting
    plot_df = pd.DataFrame(embeddings_3d, columns=["UMAP1", "UMAP2", "UMAP3"])
    plot_df["text"] = data["documents"]
    plot_df["wrapped_text"] = plot_df["text"].apply(
        lambda x: "<br>".join([x[i : i + 50] for i in range(0, len(x), 50)])
    )  # Add documents for hover text with breaks for plotly.

    # Create 3D scatter plot
    fig = px.scatter_3d(
        plot_df,
        x="UMAP1",
        y="UMAP2",
        z="UMAP3",
        hover_data={"wrapped_text": True},
        # title='3D Document Embeddings Visualization',
    )

    # Update layout for better interaction
    fig.update_layout(
        scene=dict(
            xaxis=dict(showbackground=False),
            yaxis=dict(showbackground=False),
            zaxis=dict(showbackground=False),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5),
            ),
        ),
        autosize=True,
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    fig.update_traces(
        marker=dict(size=1),
    )

    return fig


def delete_collection(collection_name):
    """
    delete chromadb collection
    """
    client.delete_collection(collection_name)
