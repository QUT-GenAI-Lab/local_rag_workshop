from llama_cpp import Llama

# at the moment, chat template not supported by the llama-cpp-python wrapper. Using this instead
from transformers import AutoTokenizer

context_length = 2048

llm = Llama(model_path = 'models/Llama-3.2-3B-Instruct-abliterated.Q4_K_S.gguf', n_ctx=context_length) #set context window HERE! Then use external logic for setting processed context window idk????


#for checking if inputs have enough room for generation:
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

def trim_inputs(input_chat: list[dict], context_length: int, new_tokens: int) -> list[dict]:
    """
    assumes system prompt - returns chat history with earlier messages removed
    """
    max_length = context_length - new_tokens
    input_length = len(tokenizer.apply_chat_template(input_chat))
    cut_idx = 1
    if input_length < max_length:
        return input_chat
    else:
        while input_length >= max_length:
            cut_idx +=1
            output = [input_chat[0]] + input_chat[cut_idx:]
            input_length = len(tokenizer.apply_chat_template(output))

        return output
    

### ^ also potentially use this for model swap???? Unsure if that's a feature I want people to have

def llama_chat_gen(input_chat: list[dict], context_length: int = context_length, new_tokens: int = 128) -> list[dict]:
    """
    returns whole chat from unaugmented chat input

    inputs:
        - input_chat: list[dict] - list form of whole chat, with 'role' and 'content' keys for each dict entry. 

    output:
        - input_chat: list[dict] - same as input but with new, generated output. Length of list output should be len(input_chat)+1
    """
    inputs = trim_inputs(input_chat, context_length, new_tokens)
    init_output = llm.create_chat_completion(messages = inputs)
    response = init_output["choices"][0]['message']
    print(response['content'])
    input_chat.append(response)
    return input_chat

def llama_chat_gen_streamed(input_chat: list[dict], context_length: int = context_length, new_tokens: int = 128) -> list[dict]:
    """
    returns whole chat from unaugmented chat input

    inputs:
        - input_chat: list[dict] - list form of whole chat, with 'role' and 'content' keys for each dict entry. 

    output:
        - input_chat: list[dict] - same as input but with new, generated output. Length of list output should be len(input_chat)+1
    """
    inputs = trim_inputs(input_chat, context_length, new_tokens)
    for item in llm.create_chat_completion(messages = inputs, stream=True):
        if 'content' in item['choices'][0]['delta'].keys():
            yield item['choices'][0]['delta']['content']
    # return output