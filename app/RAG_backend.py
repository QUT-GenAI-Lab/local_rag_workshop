from chromadb_engine import (client, 
                            switch_db, 
                            make_db_from_pdf, 
                            make_db_from_csv, 
                            make_db_from_docx, 
                            make_db_from_txt
                            )

from llama_engine import llama_chat_gen

# OVERALL CLASS
class RAGChat():
    ### TO ADD: retry generation func????? Maybe deletion as well????
    def __init__(self):
        self.messages = []
        self.RAGmessages = []
        self.inject_template = "{INJECT_TEXT}, {USER_MESSAGE}"
        self.chathead = []

    def __call__(self):
        "default call returns non-enhanced chat history"
        return self.messages

    def RAG_chathist(self):
        "returns RAG'd chat history"
        return self.RAGmessages

    def __len__(self):
        return len(self.messages)

    def add_user_message(self, message):
        "add user message. For user input."
        self.messages.append({
                'role': 'user',
                'content': message
            })  

    def add_augmented_user_message(self, injection: list[str], message):
        injection_str = '\n\n\n'.join(injection)
        self.RAGmessages.append({
                'role': 'user',
                'content': self.inject_template.format(INJECT_TEXT=injection_str, USER_MESSAGE=message)
            })  
        
    def add_assistant_message(self, message: dict):
        """add system message. For adding to message chains from chatbot generated content
        
        NOTE: ONLY appends the  
        """
        self.messages.append({
                'role': 'assistant',
                'content': message
            })
        self.RAGmessages.append({
                'role': 'assistant',
                'content': message
            })

    def temp_chathead(self, chathead, augmented: bool = False):
        "for textgen-only APIs that might not have an inbuilt chathead. Call this instead of default call for temporary chathead."
        self.chathead = [{
            'role': 'system',
            'content': chathead
        }]
        if augmented:
            self.chathead.extend(self.RAGmessages)
        else:
            self.chathead.extend(self.messages)
        return self.chathead

# func to chat with, INCLUDES RAG AND UPDATES BOTH CHAT HISTS:
def RAG_chatfunc(chat: RAGChat, input_msg, db_name, num_return, max_dist:float=None, inject_col:str=None, chathead:str = "You are a helpful assistant chatbot."): #maybe add something here that changes the chathead???

    # add input message
    chat.add_user_message(input_msg)

    #query and return injection cands
    collection = client.get_collection(db_name)
    # for now, use ONLY INPUT MSG as query. Can change this to whole chain, potentially, but will do that later 
    query = input_msg
    results = collection.query(query_texts = [input_msg],
                    n_results = num_return)

    #filter for distances
    if max_dist:
        return_idcs = [i for i, dist in enumerate(results['distances'][0]) if dist <= max_dist]
        results = {
            key: [results[key][0][i] for i in close_indices] 
            for key in results
        }

    #change what's injected
    if inject_col:
        inject_list = [x[inject_col] for x in results['metadatas'][0]]

    else:
        inject_list = results['documents'][0]

    # finally, inject into chat hist:
    chat.add_augmented_user_message(inject_list, input_msg)

    outputs = llama_chat_gen(chat.temp_chathead(augmented = True, chathead=chathead))

    response = outputs[-1]['content']

    chat.add_assistant_message(response)

    return chat() #should I just make this blank????
    

    
    




# def normal_chatfunc()

    

    
    