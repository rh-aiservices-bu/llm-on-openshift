# Working with Langchain

## Requirements

To work with those examples you will need a Hugging Face Text Generation Inference server deployed, and a model served.

You can either install Langchain and its dependencies in your workbench (`pip install langchain`), or you can directly use a pre-built custom Workbench image that comes with everything needed: `quay.io/opendatahub-contrib/workbench-images:cuda-jupyter-langchain-c9s-py311_2023c_latest`.

*[Ref: How to import a custom notebook image](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_science/1/html/managing_users_and_user_resources/managing_notebook_servers#configuring-a-custom-notebook-image_user-mgmt)*

If you want to create your own custom image, with a different IDE like VSCode for example, you will find instructions [here](https://github.com/opendatahub-io-contrib/workbench-images#building-an-image).

## Content

- [Langchain-Caikit-Basic.ipynb](Langchain-Caikit-Basic.ipynb): Basic example on using Langchain to query Llama2 served through Caikit+TGIS.
- [Langchain-Caikit-Prompt-memory.ipynb](Langchain-Caikit-Prompt-memory.ipynb): More advanced example on using Langchain to query Llama2 served through Caikit+TGIS, with custom prompt and conversation memory buffer.
- [Langchain-HFTGI-Basic.ipynb](Langchain-HFTGI-Basic.ipynb): Basic example on using Langchain to query Llama2 served through Hugging Face TGI.
- [Langchain-HFTGI-Prompt-memory.ipynb](Langchain-HFTGI-Prompt-memory.ipynb): More advanced example on using Langchain to query Llama2 served through Hugging Face TGI, with custom prompt and conversation memory buffer.
- [RAG_with_sources_Langchain-HFTGI.ipynb](RAG_with_sources_Langchain-HFTGI.ipynb): Retrieval Augmented Generation (ask questions about documents) using Langchain with Llama2 served through Hugging Face TGI.
- [RAG_with_sources_Langchain-Caikit.ipynb](RAG_with_sources_Langchain-Caikit.ipynb): Retrieval Augmented Generation (ask questions about documents) using Langchain with Llama2 served through Caikit+TGIS.
