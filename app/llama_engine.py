from llama_cpp import Llama

llm = Llama(model_path = 'models/Llama-3.2-3B-Instruct-abliterated.Q4_K_S.gguf', n_ctx=2048) #set context window HERE! Then use external logic for setting processed context window idk????


### ^ also potentially use this for model swap???? Unsure if that's a feature I want people to have

def llama_chat_gen(input_chat: list[dict]) -> list[dict]:
    """
    returns whole chat from unaugmented chat input

    inputs:
        - input_chat: list[dict] - list form of whole chat, with 'role' and 'content' keys for each dict entry. 

    output:
        - input_chat: list[dict] - same as input but with new, generated output. Length of list output should be len(input_chat)+1
    """
    init_output = llm.create_chat_completion(messages = input_chat)
    response = init_output["choices"][0]['message']
    print(response['content'])
    input_chat.append(response)
    return input_chat

def llama_chat_gen_streamed(input_chat: list[dict]) -> list[dict]:
    """
    returns whole chat from unaugmented chat input

    inputs:
        - input_chat: list[dict] - list form of whole chat, with 'role' and 'content' keys for each dict entry. 

    output:
        - input_chat: list[dict] - same as input but with new, generated output. Length of list output should be len(input_chat)+1
    """
    for item in llm.create_chat_completion(messages = input_chat, stream=True):
        if 'content' in item['choices'][0]['delta'].keys():
            yield item['choices'][0]['delta']['content']
    # return output