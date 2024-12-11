from llama_cpp import Llama

llm = Llama(model_path = 'Llama-3.2-3B-Instruct-abliterated.Q4_K_S.gguf', n_ctx=2048) #set context window HERE! Then use external logic for setting 

def llama_chat_gen(input_chat: list[dict]):
    """
    returns whole chat from unaugmented chat input
    """
    init_output = llm.create_chat_completion(messages = input_chat)
    response = init_output["choices"][0]['message']
    print(response['content'])
    input_chat.append(response)
    return input_chat