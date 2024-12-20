from chromadb_engine import (client, 
                            switch_db, 
                            make_db_from_pdf, 
                            make_db_from_csv, 
                            make_db_from_docx, 
                            make_db_from_txt
                            )

from llama_engine import llama_chat_gen

# # OVERALL CLASS
# class RAGChat():
#     """
#     Class for a RAG chat. Main goal is to have simultaneous histories of augmented and non-augmented chat, where the augmented chat shows the injection template for each user-entered chat, and non-augmented shows just the chat input without the injection template. Both will have identical responses from the chatbot though, so the intention is for chat histories not to diverge.

#     Unsure if this is the best design - mostly co-opted from old code which mostly works. Definitely works in a limited environment though, so dev-ing from here.

#     Descriptions of class methods and stuff put inline.
    
#     """
    
#     ### TO ADD: retry generation func????? Maybe deletion as well????
#     def __init__(self):
#         self.messages = [] # message history without RAG from user input
#         self.RAGmessages = [] # message history WITH RAG from user input
#         self.inject_template = "{INJECT_TEXT}, {USER_MESSAGE}" #injection template - MAYBE put 
#         self.chathead = []

#     def __call__(self):
#         "default call returns non-enhanced chat history"
#         return self.messages

#     def RAG_chathist(self):
#         "returns RAG'd chat history"
#         return self.RAGmessages

#     def __len__(self):
#         "as per (lol)"
#         return len(self.messages)

#     def add_user_message(self, message: str):
#         "add user message. For user input. Intention is to use this first before generating."
#         self.messages.append({
#                 'role': 'user',
#                 'content': message
#             })  

#     def add_augmented_user_message(self, injection: list[str], message):
#         """
#         add augmented user message, using self.inject_template.

#         TO DO: maybe a class method that changes inject_template, and can be called elsewhere for dynamic template updates during chat? Also within that class method, add checks for {INJECT_TEXT} and {USER_MESSAGE} stuff????
        
#         """
#         injection_str = '\n\n\n'.join(injection)
#         self.RAGmessages.append({
#                 'role': 'user',
#                 'content': self.inject_template.format(INJECT_TEXT=injection_str, USER_MESSAGE=message)
#             })  
        
#     def add_assistant_message(self, message: str):
#         """add system message. For adding to message chains from chatbot generated content
        
#         NOTE: ONLY takes in the message content STRING, not the entire generated message dictionary.
#         """
#         self.messages.append({
#                 'role': 'assistant',
#                 'content': message
#             })
#         self.RAGmessages.append({
#                 'role': 'assistant',
#                 'content': message
#             })

#     def temp_chathead(self, chathead, augmented: bool = False):
#         "for textgen-only APIs that might not have an inbuilt chathead. Call this instead of default call for temporary chathead. Also allows for dynamically updating the chathead, which could be funny"
#         self.chathead = [{
#             'role': 'system',
#             'content': chathead
#         }]
#         if augmented:
#             self.chathead.extend(self.RAGmessages)
#         else:
#             self.chathead.extend(self.messages)
#         return self.chathead



# func to chat with, INCLUDES RAG AND UPDATES BOTH CHAT HISTS:
# def RAG_chatfunc(chat: RAGChat, input_msg: str, db_name, num_return, max_dist:float=None, inject_col:str=None, chathead:str = "You are a helpful assistant chatbot."): #maybe add something here that changes the chathead???
#     """
#     function for chatting, with llm, using defined llama_chat_gen (although from how it reads, it looks like you can't dynamically load different llama models easily - only on app startup. Whoops!)

#     Intention of this is to chat with a RAGChat class, using the augmented chat.RAGmessages history, whilst simultaneously updatgin the normal chat.messages history.

#     inputs:
#         - chat: RAGChat - chat object with both unaugmented and augmented chat history
#         - input_msg: str - user input message
#         - db_name: str - name of db to inject from
#         - num_return: int - number of candidates to return from db injection query. NOTE: will potentially be culled by max_dist.
#         - max_dist: float - maximum distance from query allowable from injection candidates, any dist less than max_dist is culled from injection candidates.
#         - inject_col: str - what column to inject. If None, uses the documents that are embedded.

#     outputs: 
#         - chat.messages: list[dict] - unaugmented chat history from input chat
#     """

    
#     # regular chat
#     # add input message
#     chat.add_user_message(input_msg)

#     #RAG CHAT
#     #query and return injection cands
#     collection = client.get_collection(db_name)
#     # for now, use ONLY INPUT MSG as query. Can change this to whole chain, potentially, but will do that later 
#     query = input_msg
#     results = collection.query(query_texts = [input_msg],
#                     n_results = num_return)

#     #filter for distances - if returned items' distances too far from query input, drop them.
#     if max_dist:
#         return_idcs = [i for i, dist in enumerate(results['distances'][0]) if dist <= max_dist]
#         results = {
#             key: [results[key][0][i] for i in close_indices] 
#             for key in results
#         }

#     #pick what is injected - only required if not injecting from the embedding/documents "column"
#     if inject_col:
#         inject_list = [x[inject_col] for x in results['metadatas'][0]]

#     else:
#         inject_list = results['documents'][0]

#     # finally, inject into chat hist:
#     chat.add_augmented_user_message(inject_list, input_msg) #may need to change this to allow for uninjected stuff to go into augmented chat history?????????????

#     outputs = llama_chat_gen(chat.temp_chathead(augmented = True, chathead=chathead))

#     response = outputs[-1]['content']

#     chat.add_assistant_message(response)

#     return chat() #should I just make this blank????
    

    
    




# def normal_chatfunc()

def create_injection_prompt(db_name, input_msg, num_return, max_dist:float=None, inject_col:str=None, inject_template: str = "{INJECT_TEXT}, {USER_MESSAGE}"):
    collection = client.get_collection(db_name)
    # for now, use ONLY INPUT MSG as query. Can change this to whole chain, potentially, but will do that later 
    query = input_msg
    results = collection.query(query_texts = [input_msg],
                    n_results = num_return)
    
    if inject_col:
        inject_list = [x[inject_col] for x in results['metadatas'][0]]

    else:
        inject_list = results['documents'][0]

    injection_str = '\n\n\n'.join(inject_list)
    augmented_user_msg = inject_template.format(INJECT_TEXT=injection_str, USER_MESSAGE=input_msg)
    return augmented_user_msg

    
    