from chromadb_engine import (
    client,
    switch_db,
    make_db_from_pdf,
    make_db_from_csv,
    make_db_from_docx,
    make_db_from_txt,
)

from llama_engine import llama_chat_gen


def create_injection_prompt(
    db_name,
    input_msg,
    num_return,
    max_dist: float = None,
    inject_col: str = None,
    inject_template: str = "{INJECT_TEXT}, {USER_MESSAGE}",
):
    """
    creates injection prompt based on input msg and query return.
    """
    collection = client.get_collection(db_name)
    # for now, use ONLY INPUT MSG as query. Can change this to whole chain, potentially, but will do that later
    query = input_msg
    results = collection.query(query_texts=[input_msg], n_results=num_return)

    if inject_col:
        inject_list = [x[inject_col] for x in results["metadatas"][0]]

    else:
        inject_list = results["documents"][0]

    injection_str = "\n\n\n".join(inject_list)
    augmented_user_msg = inject_template.format(
        INJECT_TEXT=injection_str, USER_MESSAGE=input_msg
    )
    return augmented_user_msg
