import json
import os
import random
import time
from collections.abc import Generator
from queue import Empty, Queue
from threading import Thread
from typing import Optional

import gradio as gr
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceTextGenInference
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Milvus

load_dotenv()

# Parameters

APP_TITLE = os.getenv('APP_TITLE', 'Talk with your documentation')

INFERENCE_SERVER_URL = os.getenv('INFERENCE_SERVER_URL')
MAX_NEW_TOKENS = int(os.getenv('MAX_NEW_TOKENS', 512))
TOP_K = int(os.getenv('TOP_K', 10))
TOP_P = float(os.getenv('TOP_P', 0.95))
TYPICAL_P = float(os.getenv('TYPICAL_P', 0.95))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.01))
REPETITION_PENALTY = float(os.getenv('REPETITION_PENALTY', 1.03))

MILVUS_HOST = os.getenv('MILVUS_HOST')
MILVUS_PORT = os.getenv('MILVUS_PORT')
MILVUS_USERNAME = os.getenv('MILVUS_USERNAME')
MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD')
MILVUS_COLLECTIONS_FILE = os.getenv('MILVUS_COLLECTIONS_FILE')

SELECTED_COLLECTION = 'red_hat_openshift_ai_self_managed_2_6'

# Load array of objects from JSON file
with open(MILVUS_COLLECTIONS_FILE, 'r') as file:
    collections_data = json.load(file)

#MILVUS_COLLECTION = "red_hat_openshift_ai_self_managed_2_6"

# Streaming implementation
class QueueCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""

    def __init__(self, q):
        self.q = q

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        self.q.put(token)

    def on_llm_end(self, *args, **kwargs: any) -> None:
        return self.q.empty()

def remove_source_duplicates(input_list):
    unique_list = []
    for item in input_list:
        if item.metadata['source'] not in unique_list:
            unique_list.append(item.metadata['source'])
    return unique_list

def stream(input_text) -> Generator:
    # Create a Queue
    job_done = object()

    # Create a function to call - this will run in a thread
    def task():
        resp = qa_chain[SELECTED_COLLECTION].invoke({"query": input_text})
        sources = remove_source_duplicates(resp['source_documents'])
        if len(sources) != 0:
            q.put("\n*Sources:* \n")
            for source in sources:
                q.put("* " + str(source) + "\n")
        q.put(job_done)

    # Create a thread and start the function
    t = Thread(target=task)
    t.start()

    content = ""

    # Get each new token from the queue and yield for our generator
    while True:
        try:
            next_token = q.get(True, timeout=1)
            if next_token is job_done:
                break
            if isinstance(next_token, str):
                content += next_token
                yield next_token, content
        except Empty:
            continue

# A Queue is needed for Streaming implementation
q = Queue()

############################
# LLM chain implementation #
############################

# Document store: Milvus
model_kwargs = {'trust_remote_code': True}
embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1",
    model_kwargs=model_kwargs,
    show_progress=False
)

stores = {}
for collection in collections_data:
    stores[collection['name']] = Milvus(
        embedding_function=embeddings,
        connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT, "user": MILVUS_USERNAME, "password": MILVUS_PASSWORD},
        collection_name=collection['name'],
        metadata_field="metadata",
        text_field="page_content",
        drop_old=False
        )

# LLM
llm = HuggingFaceTextGenInference(
    inference_server_url=INFERENCE_SERVER_URL,
    max_new_tokens=MAX_NEW_TOKENS,
    top_k=TOP_K,
    top_p=TOP_P,
    typical_p=TYPICAL_P,
    temperature=TEMPERATURE,
    repetition_penalty=REPETITION_PENALTY,
    streaming=True,
    verbose=False,
    callbacks=[QueueCallback(q)]
)

# Prompt
template="""<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant named HatBot answering questions.
You will be given a question you need to answer, and a context to provide you with information. You must answer the question based as much as possible on this context.
Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

Context: 
{context}

Question: {question} [/INST]
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)


qa_chain = {}
for collection in collections_data:
    qa_chain[collection['name']] = RetrievalQA.from_chain_type(
        llm,
        retriever = stores[collection['name']].as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
        ),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=True
        )

# Gradio implementation
def ask_llm(message, history):
    for next_token, content in stream(message):
        yield(content)

with gr.Blocks(title="Red Hat Documentation Chatbot", css="footer {visibility: hidden}") as demo:
    with gr.Row():
        gr.Markdown(f"## {APP_TITLE}")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(f"This chatbot is ...")
            gr.Dropdown(
            ["cat", "dog", "bird"], label="Animal", info="Will add more animals later!"
            ),
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                show_label=False,
                avatar_images=(None,'assets/robot-head.svg'),
                render=False
                )
            gr.ChatInterface(
                ask_llm,
                chatbot=chatbot,
                clear_btn=None,
                retry_btn=None,
                undo_btn=None,
                stop_btn=None,
                description=None
                )

if __name__ == "__main__":
    demo.queue().launch(
        server_name='0.0.0.0',
        share=False,
        favicon_path='./assets/robot-head.ico'
        )
