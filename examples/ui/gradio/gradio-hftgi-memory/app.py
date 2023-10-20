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
PROMPT_TEMPLATE="""<s>[INST]
You are a helpful, respectful and honest assistant named HatBot. Always be as helpful as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
I will ask you a QUESTION and give you an AUDIENCE PERSONA, and you will respond with an ANSWER easily understandable by the AUDIENCE PERSONA.
If a QUESTION does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a QUESTION, please don't share false information.

### AUDIENCE PERSONA:
Adults with reasonable technical understanding

### PREVIOUS CONVERSATION:
{history}

### QUESTION:
{input}

### ANSWER:
[/INST]
"""

# Class to handle parameters for easy update
class ConfigManager:
    def __init__(self, INFERENCE_SERVER_URL, MAX_NEW_TOKENS, TOP_K, TOP_P, TYPICAL_P, TEMPERATURE, REPETITION_PENALTY, PROMPT_TEMPLATE):
        self.INFERENCE_SERVER_URL = INFERENCE_SERVER_URL
        self.MAX_NEW_TOKENS = MAX_NEW_TOKENS
        self.TOP_K = TOP_K
        self.TOP_P = TOP_P
        self.TYPICAL_P = TYPICAL_P
        self.TEMPERATURE = TEMPERATURE
        self.REPETITION_PENALTY = REPETITION_PENALTY
        self.PROMPT_TEMPLATE = PROMPT_TEMPLATE

    def reset_prompt(self):
        self.PROMPT_TEMPLATE = PROMPT_TEMPLATE
        prompt.template = PROMPT_TEMPLATE
        conversation.prompt = prompt
        gr.Info('Prompt reset!')
        return PROMPT_TEMPLATE

    def reset_parameters(self):
        self.MAX_NEW_TOKENS = MAX_NEW_TOKENS
        llm.max_new_tokens = self.MAX_NEW_TOKENS
        self.TOP_K = TOP_K
        llm.top_k = self.TOP_K
        self.TOP_P = TOP_P
        llm.top_p = self.TOP_P
        self.TYPICAL_P = TYPICAL_P
        llm.typical_p = self.TYPICAL_P
        self.TEMPERATURE = TEMPERATURE
        llm.temperature = self.TEMPERATURE
        self.REPETITION_PENALTY = REPETITION_PENALTY
        llm.repetition_penalty = self.REPETITION_PENALTY
        gr.Info('Parameters reset!')
        return TEMPERATURE, MAX_NEW_TOKENS, TOP_P, TOP_K, TYPICAL_P, REPETITION_PENALTY

    def update_inference_server_url(self, new_url):
        self.INFERENCE_SERVER_URL = new_url

    def update_max_new_tokens(self, new_max_tokens):
        self.MAX_NEW_TOKENS = new_max_tokens
        llm.max_new_tokens = self.MAX_NEW_TOKENS
        gr.Info('Max tokens updated!')

    def update_top_k(self, new_top_k):
        self.TOP_K = new_top_k
        llm.top_k = self.TOP_K
        gr.Info('Top_k updated!')

    def update_top_p(self, new_top_p):
        self.TOP_P = new_top_p
        llm.top_p = self.TOP_P
        gr.Info('Top_p updated!')

    def update_typical_p(self, new_typical_p):
        self.TYPICAL_P = new_typical_p
        llm.typical_p = self.TYPICAL_P
        gr.Info('Typical_p updated!')

    def update_temperature(self, new_temperature):
        if new_temperature == 0:
            new_temperature = None
        self.TEMPERATURE = new_temperature
        llm.temperature = self.TEMPERATURE
        gr.Info('Temperature updated!')

    def update_repetition_penalty(self, new_repetition_penalty):
        self.REPETITION_PENALTY = new_repetition_penalty
        llm.repetition_penalty = self.REPETITION_PENALTY
        gr.Info('Repetition penalty updated!')
    
    def update_prompt_template(self, new_prompt_template):
        self.PROMPT_TEMPLATE = new_prompt_template
        prompt.template = new_prompt_template
        conversation.prompt = prompt
        gr.Info('Prompt updated!')

    def get_config(self):
        return {
            'INFERENCE_SERVER_URL': self.INFERENCE_SERVER_URL,
            'MAX_NEW_TOKENS': self.MAX_NEW_TOKENS,
            'TOP_K': self.TOP_K,
            'TOP_P': self.TOP_P,
            'TYPICAL_P': self.TYPICAL_P,
            'TEMPERATURE': self.TEMPERATURE,
            'REPETITION_PENALTY': self.REPETITION_PENALTY
        }


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
    job_done = object()

    # Create a function to call - this will run in a thread
    def task():
        resp = conversation.run({"input": input_text})
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

# Initialize the config
config = ConfigManager(INFERENCE_SERVER_URL, MAX_NEW_TOKENS, TOP_K, TOP_P, TYPICAL_P, TEMPERATURE, REPETITION_PENALTY, PROMPT_TEMPLATE)

# A Queue is needed for Streaming implementation
q = Queue()

# LLM chain implementation   
llm = HuggingFaceTextGenInference(
    inference_server_url=config.INFERENCE_SERVER_URL,
    max_new_tokens=config.MAX_NEW_TOKENS,
    top_k=config.TOP_K,
    top_p=config.TOP_P,
    typical_p=config.TYPICAL_P,
    temperature=config.TEMPERATURE,
    repetition_penalty=config.REPETITION_PENALTY,
    streaming=True,
    verbose=False,
    callbacks=[QueueCallback(q)]
)

prompt = PromptTemplate(
    input_variables=["input", "history"],
    template=PROMPT_TEMPLATE
    )


memory=ConversationBufferMemory()

conversation = ConversationChain(
    llm=llm,
    prompt=prompt,
    verbose=False,
    memory=memory,
    )

# Gradio implementation
def ask_llm(message, history):
    for next_token, content in stream(message):
        yield(content)

with gr.Blocks(title="HatBot", css="footer {visibility: hidden}") as demo:
    clear_btn = gr.Button("Clear memory and start a new conversation", render=False)
    clear_btn.click(lambda : memory.clear(), None, None)
    chatbot = gr.Chatbot(
        show_label=False,
        avatar_images=(None,'assets/robot-head.svg'),
        render=False,
        show_copy_button=True
        )
    gr.ChatInterface(
        ask_llm,
        chatbot=chatbot,
        clear_btn=clear_btn,
        undo_btn=None,
        stop_btn=None,
        description="Simple conversation with memory chatbot"
        )
    with gr.Accordion("Advanced Settings", open=False):
        with gr.Tab("Prompt"):
            prompt_box = gr.Textbox(label="", container=False, lines=15, interactive=True, value=config.PROMPT_TEMPLATE)
            with gr.Row():
                save_prompt_btn = gr.Button("Save your Changes")
                save_prompt_btn.click(config.update_prompt_template, inputs=prompt_box)
                reset_prompt = gr.Button("Reset the Prompt")
                reset_prompt.click(config.reset_prompt, inputs=None, outputs=[prompt_box])
        with gr.Tab("Parameters"):
            with gr.Group():
                with gr.Row():
                    temperature_slider = gr.Slider(0, 5, value=config.TEMPERATURE, label='Temperature', step=0.01, scale=4)
                    temperature_slider.release(config.update_temperature, inputs=[temperature_slider])
                    gr.Textbox(show_label=False, container=False, scale=2, value='Think of it as a "chaos" dial. If you turn up the temperature, you will get more random and unexpected responses. If you turn it down, the responses will be more predictable and focused.')
            with gr.Group():
                with gr.Row():
                    max_new_tokens_slider = gr.Slider(10, 1000, value=config.MAX_NEW_TOKENS, label='Max New Tokens', step=5, scale=4)
                    max_new_tokens_slider.release(config.update_max_new_tokens, inputs=[max_new_tokens_slider])
                    gr.Textbox(show_label=False, container=False, scale=2, value='The maximum number of tokens (words or parts of words) you want the model to generate')
            with gr.Group():
                with gr.Row():
                    top_p_slider = gr.Slider(0.01, 0.99, value=config.TOP_P, label='Top_p', step=0.01, scale=4)
                    top_p_slider.release(config.update_top_p, inputs=[top_p_slider])
                    gr.Textbox(show_label=False, container=False, scale=2, value='This is like setting a rule that the AI can only choose from the best possible options. If you set top_p to 0.1, it is like telling the AI, "You can only pick from the top 10% of your \'best guesses\'."')
            with gr.Group():
                with gr.Row():
                    top_k_slider = gr.Slider(1, 50, value=config.TOP_K, label='Top_k', step=0.01, scale=4)
                    top_k_slider.release(config.update_top_k, inputs=[top_k_slider])
                    gr.Textbox(show_label=False, container=False, scale=2, value='This one is similar to top_p but with a fixed number. If top_k is set to 10, it is like telling the AI, "You have 50 guesses. Choose the best one."')
            with gr.Group():
                with gr.Row():
                    typical_p_slider = gr.Slider(0.01, 0.99, value=config.TYPICAL_P, label='Typical_p', step=0.01, scale=4)
                    typical_p_slider.release(config.update_typical_p, inputs=[typical_p_slider])
                    gr.Textbox(show_label=False, container=False, scale=2, value='This is a parameter in the language model that you can adjust to control how closely the generated text aligns with what\'s typical or expected in the context. A low value makes the text more random, while a high value makes it more typical.')
            with gr.Group():
                with gr.Row():
                    repetition_penalty_slider = gr.Slider(0.01, 5, value=config.REPETITION_PENALTY, label='Repetition_penalty', step=0.01, scale=4)
                    repetition_penalty_slider.release(config.update_repetition_penalty, inputs=[repetition_penalty_slider])
                    gr.Textbox(show_label=False, container=False, scale=2, value='When you set a lower repetition_penalty, it encourages the model to use different words and phrases to avoid repeating itself too often. When you set a higher repetition_penalty, it allows the model to use the same words or phrases more frequently.')
            reset_parameters_btn = gr.Button("Reset the Parameters")
            reset_parameters_btn.click(config.reset_parameters, inputs=None, outputs=[temperature_slider,max_new_tokens_slider, top_p_slider, top_k_slider, typical_p_slider, repetition_penalty_slider])

if __name__ == "__main__":
    demo.queue().launch(
        server_name='0.0.0.0',
        share=False,
        favicon_path='./assets/robot-head.ico'
        )
