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
from langchain.chains import ConversationChain
from langchain.llms import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

load_dotenv()

# Parameters
INFERENCE_SERVER_URL = os.getenv('INFERENCE_SERVER_URL')
MAX_NEW_TOKENS = int(os.getenv('MAX_NEW_TOKENS', 512))
TOP_K = int(os.getenv('TOP_K', 10))
TOP_P = float(os.getenv('TOP_P', 0.95))
TYPICAL_P = float(os.getenv('TYPICAL_P', 0.95))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.01))
REPETITION_PENALTY = float(os.getenv('REPETITION_PENALTY', 1.03))

# Streaming implementation
class QueueCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""

    def __init__(self, q):
        self.q = q

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        self.q.put(token)

    def on_llm_end(self, *args, **kwargs: any) -> None:
        return self.q.empty()


def stream(input_text) -> Generator:
    # Create a Queue
    #q = Queue()
    job_done = object()

    # Create a function to call - this will run in a thread
    def task():
        resp = conversation.run(input_text)
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

# LLM chain implementation   
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

template="""<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant name HatBot. Always be as helpful as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

Current conversation:
{history}
Human: {input}
AI:
[/INST]
"""
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

memory=ConversationBufferMemory()

conversation = ConversationChain(llm=llm,
                                prompt=PROMPT,
                                verbose=False,
                                memory=memory,
                                )

# Gradio implementation
def ask_llm(message, history):
    for next_token, content in stream(message):
        yield(content)

with gr.Blocks() as demo:
    clear_btn = gr.Button("Clear memory and start a new conversation", render=False)
    clear_btn.click(lambda : memory.clear(), None, None)
    chatbot = gr.Chatbot(show_label=False, avatar_images=(None,'assets/robot-head.svg'), render=False)
    gr.ChatInterface(ask_llm, chatbot=chatbot, clear_btn=clear_btn, undo_btn=None, stop_btn=None, description="Simple conversation with memory chatbot")

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0")
