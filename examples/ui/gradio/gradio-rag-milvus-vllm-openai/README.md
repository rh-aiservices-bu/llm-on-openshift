# Gradio UI for RAG using vLLM Inference server and Milvus

This is a simple UI example for a RAG-based Chatbot using Gradio, vLLM Inference server, and Milvus as a vector database.

![UI](img/gradio-rag-milvus-vllm-openai.png)

You can refer to those different notebooks to get a better understanding of the flow:

- [Data Ingestion to Milvus with Langchain](../../../notebooks/langchain/Langchain-Milvus-Ingest.ipynb)
- [Milvus querying with Langchain](../../../notebooks/langchain/Langchain-Milvus-Query.ipynb)
- [Full RAG example with Milvus, vLLM and Langchain](../../../notebooks/langchain/RAG_with_sources_Langchain-vLLM-Milvus.ipynb)

## Requirements

- A vLLM Inference server with a deployed LLM. This example is based on Mistral-7B-Instruct-v0.2 but depending on your LLM you may need to adapt the prompt.
- A Milvus installation. See [here](../../../../vector-databases/milvus/README.md) for deployment instructions.
- A Database and a Collection already populated with documents. See [here](../../../notebooks/langchain/Langchain-Milvus-Ingest.ipynb) for an example.

## Deployment on OpenShift

A pre-built container image of the application is available at: `quay.io/rh-aiservices-bu/gradio-rag-milvus-vllm-openai:latest`

In the `deployment` folder, you will find the files necessary to deploy the application:

- `configmap-collections.yaml`: this ConfigMap holds the configuration for the various Milvus collections you may want to use to back your RAG. Adapt depending on the collections you have created.
- `deployment.yaml`: you must provide the various information about your inference server and vector database starting at line 52. Please feel free to modify those parameters as you see fit (see parameters below).
- `service.yaml`: creates the Service needed to access the Pod that will be created.
- `route.yaml`: Route definition to expose the Service outside of the cluster. BEWARE: don't forget to protect this Route if you don't want anyone to access your knoledge bases or the LLM.

The different parameters you can/must pass as environment variables in the deployment are:

- APP_TITLE - Optional, defaults to 'Chat with your Knowledge Base'
- INFERENCE_SERVER_URL - Mandatory
- MODEL_NAME - Mandatory
- MAX_TOKENS - Optional, defaults to 512
- TOP_P - Optional, defaults to 0.95
- TEMPERATURE - Optional, defaults to 0.01
- PRESENCE_PENALTY - Optional, defaults to 1.03
- MILVUS_HOST - Mandatory
- MILVUS_PORT - Mandatory
- MILVUS_USERNAME - Mandatory
- MILVUS_PASSWORD - Mandatory
- MILVUS_COLLECTIONS_FILE - Mandatory
- DEFAULT_COLLECTION - Mandatory

The deployment replicas is set to 0 initially to let you properly fill in those parameters. Don't forget to scale it up if you want see something 😉!
