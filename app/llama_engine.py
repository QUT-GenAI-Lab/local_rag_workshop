import ollama
from ollama import chat, ChatResponse
import subprocess
import requests
from requests.exceptions import RequestException
import os
from os import path

BASE_DIR = path.abspath(path.dirname(__file__))

def check_ollama_install():
    '''
    returns bool for if ollama exists on the system
    '''
    test = subprocess.run('ollama --version', shell=True, check=False)
    if test.returncode == 0:
        return True
    else:
        return False

def check_and_serve_ollama():
    '''
    checks if ollama is being served to port 11434 (assumes ollama is installed)
    '''
    try:
        requests.get('http://localhost:11434').raise_for_status()
        return
    except RequestException:
        subprocess.run('ollama serve', shell=True)
        return

def ollama_list_and_install_models():
    '''
    lists models installed on ollama. If none, installs llama3.2 by default
    '''
    model_list = ollama.list()['models']
    if not model_list: #if list is empty, install llama3.2 model as default
        subprocess.run('ollama create llama3.2 -f ./Modelfile', shell=True, cwd=BASE_DIR)

    return [x['model'] for x in ollama.list()['models']]

def ollama_load_model(model_str):
    '''
    runs a chat first to load model, which lessens initial latency of chat after "loading". NOTE: unloads after 5 mins, by default.
    '''
    test = chat(
    model = model_str,
    messages = [
        {'role': 'user', 'content': 'Hello'},
             ],
    )

def llama_chat_gen(input_chat: list[dict], model: str = 'llama3.2') -> list[dict]:
    """
    returns whole chat from unaugmented chat input

    inputs:
        - input_chat: list[dict] - list form of whole chat, with 'role' and 'content' keys for each dict entry. 

    output:
        - input_chat: list[dict] - same as input but with new, generated output. Length of list output should be len(input_chat)+1
    """

    init_output = chat(
                    model = model,
                    messages = input_chat,
                    )
    response = init_output['message']['content']
    
    input_chat.append({'role': 'assistant',
                       'content': response
                      }
                     )
    return input_chat

def llama_chat_gen_streamed(input_chat: list[dict], model: str = 'llama3.2') -> list[dict]:
    """
    returns whole chat from unaugmented chat input

    inputs:
        - input_chat: list[dict] - list form of whole chat, with 'role' and 'content' keys for each dict entry. 

    output:
        - input_chat: list[dict] - same as input but with new, generated output. Length of list output should be len(input_chat)+1
    """
    init_output = chat(
                    model = model,
                    messages = input_chat,
                    stream = True,
                    )
    for item in init_output:
        yield item['message']['content']