# UI Examples

Different example of Chat UIs.

## Using Gradio

[Gradio](https://www.gradio.app/) is a Python SDK that can be used to easily create Web UIs for Machine Learning models.

- [Simple Chat with memory using HFTGI](gradio/gradio-hftgi-memory/README.md)
- [Chatbot+HFTGI+Redis](gradio/gradio-hftgi-rag-redis/README.md): Chat with your documentation using HFTGI for LLM serving and Redis for Vector Store.
- [Chatbot+Caikit/TGIS+Redis](gradio/gradio-caikit-rag-redis/README.md): Chat with your documentation using Caikit+TGIS for LLM serving and Redis for Vector Store.
- [Chatbot backed by a knowledge base](gradio/gradio-rag-milvus-vllm-openai/README.md): Chat with multiple different knowledge bases using vLLM for LLM Serving and Milvus for Vector Store.
