# Gradio UI for RAG using vLLM Inference server and PostgreSQL+pgvector

This is a simple UI example for a RAG-based Chatbot using Gradio, vLLM server, and PostgreSQL+pgvector as a vector database.

You can refer to those different notebooks to get a better understanding of the flow:

- [Data Ingestion to PostgreSQL+pgvector with Langchain](../../../notebooks/langchain/Langchain-PgVector-Ingest.ipynb)
- [PostgreSQL+pgvector querying with Langchain](../../../notebooks/langchain/Langchain-PgVector-Query.ipynb)
- [Full RAG example with PostgreSQL+pgvector and Langchain](../../../notebooks/langchain/RAG_with_sources_Langchain-HFTGI-PgVector.ipynb)

## Requirements

- A vLLM Inference server with a deployed LLM. This example is based on Mistral-7b-Instruct but depending on your LLM you may need to adapt the prompt.
- A PostgreSQL+pgvector installation. See [here](../../../../pgvector/README.md) for deployment instructions.
- A Database and a Collection already populated with documents. See [here](../../../notebooks/langchain/Langchain-PgVector-Ingest.ipynb) for an example.

## Deployment on OpenShift

A pre-built container image of the application is available at: `quay.io/rh-aiservices-bu/gradio-vllm-rag-pgvector:latest`

In the `deployment` folder, you will find the files necessary to deploy the application:

- `deployment.yaml`: you must provide the URL of your inference server in the placeholder on L54 and pgvector information on L56 and L58. Please feel free to modify other parameters as you see fit.
- `service.yaml`
- `route.yaml`

The different parameters you can/must pass as environment variables in the deployment are:

- INFERENCE_SERVER_URL - mandatory
- DB_CONNECTION_STRING - mandatory
- DB_COLLECTION_NAME - mandatory
- MODEL_NAME - mandatory, default: mistralai/Mistral-7B-Instruct-v0.2
- MAX_TOKENS - mandatory, default: 1024
- PRESENCE_PENALTY, default: 1.03
- TOP_K - optional, default: 10
- TOP_P - optional, default: 0.95
- TYPICAL_P - optional, default: 0.95
- TEMPERATURE - optional, default: 0.01

The deployment replicas is set to 0 initially to let you properly fill in those parameters. Don't forget to scale it up if you want see something 😉!
