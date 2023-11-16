# LLM on OpenShift

In this repo you will find resources, demos, recipes,... to work with LLMs on OpenShift with OpenShift Data Science or Open Data Hub.

## Content

### Inference Servers deployment

Two different Inference Servers deployment instructions are available:

- [Caikit-TGIS-Serving](https://github.com/opendatahub-io/caikit-tgis-serving) (external): How to deploy the Caikit-TGIS-Serving stack, from OpenDataHub.
- [Hugging Face Text Generation Inference](hf_tgis_deployment/README.md): How to deploy the Text Generation Inference server from Hugging Face.

### Vector Databases deployment

Deployments of different databases that can be used as a Vector Store are available:

- [PostgreSQL+pgvector](pgvector_deployment/README.md): Full recipe to create an instance of PostgreSQL with the pgvector extension, making it usable as a vector store.
- [Redis](redis_deployment/README.md): Full recipe to deploy Redis, create a Cluster and a suitable Database for a Vector Store.

### Inference and application examples

- [Caikit](examples/notebooks/caikit-basic-query/README.md): Basic example demonstrating how to work with Caikit+TGIS for LLM serving.
- [Langchain examples](examples/notebooks/langchain/README.md): Various notebooks demonstrating how to work with [Langchain](https://www.langchain.com/). Examples include both HFTGI and Caikit+TGIS Serving.
- [Langflow examples](examples/langflow/README.md): Various examples demonstrating how to work with Langflow.
- [UI examples](examples/ui/README.md): Various examples on how to create and deploy a UI to interact with your LLM.
