import os
import random
import time
from collections.abc import Generator
from queue import Empty, Queue
from threading import Thread
from typing import Optional
from text_generation import Client
import gradio as gr
from prometheus_client import start_http_server, Counter
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import HuggingFaceTextGenInference
from langchain.prompts import PromptTemplate
from langchain.vectorstores.redis import Redis
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import requests

load_dotenv()

# Parameters

APP_TITLE = os.getenv('APP_TITLE', 'Talk with your documentation')

INFERENCE_SERVER_URL = os.getenv('INFERENCE_SERVER_URL')
MAX_NEW_TOKENS = int(os.getenv('MAX_NEW_TOKENS', 100))
TOP_K = int(os.getenv('TOP_K', 10))
TOP_P = float(os.getenv('TOP_P', 0.95))
TYPICAL_P = float(os.getenv('TYPICAL_P', 0.95))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.01))
REPETITION_PENALTY = float(os.getenv('REPETITION_PENALTY', 1.03))

REDIS_URL = os.getenv('REDIS_URL')
REDIS_INDEX = os.getenv('REDIS_INDEX')
TIMEOUT = int(os.getenv('TIMEOUT', 30))
# Start Prometheus metrics server
start_http_server(8000)

# Create metric
FEEDBACK_COUNTER = Counter("feedback_stars", "Number of feedbacks by stars", ["stars", "model_id"])
MODEL_USAGE_COUNTER = Counter('model_usage', 'Number of times a model was used', ['model_id'])
REQUEST_TIME = Gauge('request_duration_seconds', 'Time spent processing a request', ['model_id'])
SATISFACTION = Gauge('satisfaction_rating', 'User satisfaction rating', ['rating'])
TIMEOUTS = Counter('timeouts_total', 'Total number of request timeouts', ['model_id'])

model_id = ""

client = Client(base_url=INFERENCE_SERVER_URL,timeout=TIMEOUT)

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

def get_model_info():
    response = requests.get(INFERENCE_SERVER_URL + "/info")
    json_response = response.json()
    print(json_response)
    model_id = json_response['model_id']  # Extract the model_id
    print("Model ID:", model_id)  # Print the model_id
    return model_id  # Return the model_id instead of the whole JSON


def stream(input_text) -> Generator:

    global model_id
    # Create a Queue
    job_done = object()

    # Create a function to call - this will run in a thread
    def task():
        resp = qa_chain({"query": input_text})
        sources = remove_source_duplicates(resp['source_documents'])  
        input = str(input_text)
        start_time = time.perf_counter() # start and end time to get the precise timing of the request
        
        try:
            # response = client.generate(input, max_new_tokens=MAX_NEW_TOKENS)
            model_id = get_model_info()
            end_time = time.perf_counter()
            # Record successful request time
            REQUEST_TIME.labels(model_id=model_id).set(end_time - start_time)
        except TimeoutError:  # or whatever exception your client throws on timeout
            end_time = time.perf_counter()
            TIMEOUTS.info({'model_id': model_id, 'timeout_duration': str(end_time - start_time), 'input_text': input})

        q.put({"model_id": model_id})
        # q.put({"generated_text": resp.generated_text})
        print("MODEL ID IS:",model_id)
        print("Question:",input)
        if len(sources) != 0:
            q.put("\n*Sources:* \n")
            for source in sources:
                q.put("* " + str(source) + "\n")
        q.put(job_done)
        print("Saving it...")

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
            if isinstance(next_token, dict) and 'model_id' in next_token:
                model_id = next_token['model_id']
                MODEL_USAGE_COUNTER.labels(model_id=model_id).inc()
            # if isinstance(next_token, dict) and 'generated_text' in next_token:
            #     generated_text = next_token['generated_text']    
            elif isinstance(next_token, str):
                content += next_token     
                yield next_token, content, model_id
        except Empty:
            continue

# A Queue is needed for Streaming implementation
q = Queue()

############################
# LLM chain implementation #
############################

# Document store: Redis vector store
embeddings = HuggingFaceEmbeddings()
rds = Redis.from_existing_index(
    embeddings,
    redis_url=REDIS_URL,
    index_name=REDIS_INDEX,
    schema="redis_schema.yaml"
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
You are a helpful, respectful and honest assistant named HatBot answering questions about OpenShift Data Science, aka RHODS.
You will be given a question you need to answer, and a context to provide you with information. You must answer the question based as much as possible on this context.
Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

Question: {question}
Context: {context} [/INST]
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=rds.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4, "distance_threshold": 0.5}),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    return_source_documents=True
    )
        
def ask_llm(message, history):
    for next_token, content, model_id in stream(message):  
        print(model_id) 
        model_id_box.update(value=model_id)
        yield f"{content}\n\nModel ID: {model_id}"


# Gradio implementation
with gr.Blocks(title="HatBot", css="footer {visibility: hidden}") as demo:    

    input_box = gr.Textbox(label="Your Question")
    output_answer = gr.Textbox(label="Answer", readonly=True)
    model_id_box = gr.Textbox(visible=False)  # will hold the model_id

    gr.Interface(
        fn=ask_llm,
        inputs=[input_box],
        outputs=[output_answer],
        clear_btn=None,
        retry_btn=None,
        undo_btn=None,
        stop_btn=None,
        description=APP_TITLE
        )    
    
    radio = gr.Radio(["1", "2", "3", "4", "5"], label="Star Rating")
    output = gr.Textbox(label="Output Box")

    @radio.input(inputs=radio, outputs=output)
    def get_feedback(star):
        print("Rating: " + star)
        # Increment the counter based on the star rating received
        FEEDBACK_COUNTER.labels(stars=str(star), model_id=model_id).inc()
        SATISFACTION.labels(rating=star).set(1)

        return f"Received {star} star feedback. Thank you!"


if __name__ == "__main__":
    demo.queue().launch(
        server_name='0.0.0.0',
        share=False,
        favicon_path='./assets/robot-head.ico'
        )