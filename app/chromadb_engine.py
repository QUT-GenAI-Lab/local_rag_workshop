import chromadb
import pandas as pd
from pypdf import PdfReader
import docx2txt

#load persistent dir
client = chromadb.PersistentClient(path="chromadbs")

# generic funcs

def split_texts(input_str: str, split_length: int = 150):
    wordlist = input_str.split(' ')
    splitlist = [' '.join(wordlist[i:i+split_length]) for i in range(0, len(wordlist), split_length)]
    return splitlist

### FUNCS FOR IMPORTING AND STUFF

def switch_db(db_name):
    collection = client.get_or_create_collection(name=db_name)
    return collection

def make_db_from_pdf(pdf_dir: str, db_name: str, split_length: int = 150, ):

    #make docs for embedding
    
    reader = PdfReader(pdf_dir)
    pagetexts = []
    total_splits = []
    for page in reader.pages:
        text = page.extract_text()
        text = text.replace('\n', ' ') #clean text of new lines
        pagetexts.append(text, split_length)

    for pagetext in pagetexts:
        textchunks = split_texts(pagetexts, split_length)
        total_splits.extend(text_chunks)

    #get num of ids for chromadb creation
    ids = [f"id{num}" for num in range(len(total_splits))]

    #create (or upsert into) chromadb
    collection = client.get_or_create_collection(name=db_name)

    #using upsert to overwrite existing
    collection.upsert(documents = total_splits,
                  ids = ids)

    return collection

def make_db_from_csv(csv_dir: str, embedding_col: str, db_name: str):
    """
    TODO: make this robust to adding multiple metadatas, allow us to specify which column is returned from embedding etc.
    
    """
    #ingest and prepare data
    init_df = pd.read_csv(csv_dir)
    documents = list(init_df[embedding_col])
    #add metadatas for select querying I guess, or allowing to pick what we query
    metadatas = [init_df.loc[x].to_dict() for x in range(len(init_df))]
    ids = [f"id{num}" for num in range(len(init_df))]
    
    #create or upsert into collection
    collection = client.get_or_create_collection(name=db_name)

    #using upsert to overwrite existing
    collection.upsert(documents = documents,
                   metadatas = metadatas,
                  ids = ids)

    return collection
    

def make_db_from_docx(docx_dir: str, db_name: str, split_length: int = 150, ):
    text = docx2txt.process(docx_dir)
    split_list = split_texts(text, split_length)
    ids = [f"id{num}" for num in range(len(split_list))]

    collection = client.get_or_create_collection(name=db_name)

    collection.upsert(documents = split_list,
                  ids = ids)

    return collection
    
    

def make_db_from_txt(txt_dir: str, db_name: str, split_length: int = 150, ):
    with open(txt_dir, 'r') as f:
        text = f.read()
    
    split_list = split_texts(text, split_length)
    ids = [f"id{num}" for num in range(len(split_list))]

    collection = client.get_or_create_collection(name=db_name)

    collection.upsert(documents = split_list,
                  ids = ids)

    return collection