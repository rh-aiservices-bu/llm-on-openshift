# LLM on OpenShift

In this repo you will find resources, demos, recipes... to work with LLMs on OpenShift with [OpenShift AI](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-ai) or [Open Data Hub](https://opendatahub.io/).

## Content

### Inference Servers

The following **Inference Servers** for LLMs can be deployed standalone on OpenShift:

- [vLLM](llm-servers/vllm/README.md): how to deploy [vLLM](https://docs.vllm.ai/en/latest/index.html), the "Easy, fast, and cheap LLM serving for everyone".
- [Hugging Face TGI](llm-servers/hf_tgi/README.md): how to deploy the [Text Generation Inference](https://github.com/huggingface/text-generation-inference) server from Hugging Face.
- [Caikit-TGIS-Serving](https://github.com/opendatahub-io/caikit-tgis-serving) (external): how to deploy the Caikit-TGIS-Serving stack, from OpenDataHub.
- [Ollama](llm-servers/ollama/README.md): how to deploy [Ollama](https://github.com/ollama/ollama) using CPU only for inference.
- [SBERT](llm-servers/sbert/README.md): runtime to serve [Sentence Transformers](https://huggingface.co/sentence-transformers) models.

### Serving Runtimes deployment

The following **Runtimes** can be imported in the Single-Model Serving stack of Open Data Hub or OpenShift AI.

- [vLLM Serving Runtime](serving-runtimes/vllm_runtime/README.md)
- [Hugging Face Text Generation Inference](serving-runtimes/hf_tgi_runtime/README.md)
- [SBERT](serving-runtimes/sbert_runtime/README.md)
- [Ollama](serving-runtimes/ollama_runtime/ollama-runtime.yaml)

### Vector Databases

The following **Databases** can be used as a Vector Store for Retrieval Augmented Generation (RAG) applications:

- [Milvus](vector-databases/milvus/README.md): Full recipe to deploy the Milvus vector store, in standalone or cluster mode.
- [PostgreSQL+pgvector](vector-databases/pgvector/README.md): Full recipe to create an instance of PostgreSQL with the pgvector extension, making it usable as a vector store.
- [Redis](vector-databases/redis/README.md): Full recipe to deploy Redis, create a Cluster and a suitable Database for a Vector Store.

### Inference and application examples

- [Caikit](examples/notebooks/caikit-basic-query/README.md): Basic example demonstrating how to work with Caikit+TGIS for LLM serving.
- [Langchain examples](examples/notebooks/langchain/README.md): Various notebooks demonstrating how to work with [Langchain](https://www.langchain.com/). Examples are provided for different types of LLM servers (standalone or using the Single-Model Serving stack of Open Data Hub or OpenShift AI) and different vector databases.
- [Langflow examples](examples/langflow/README.md): Various examples demonstrating how to work with Langflow.
- [UI examples](examples/ui/README.md): Various examples on how to create and deploy a UI to interact with your LLM.
