import os

def start():
    os.system('python -m vllm.entrypoints.openai.api_server --model mistralai/Mistral-7B-Instruct')
