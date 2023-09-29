# Working with Langchain

## Requirements

To work with those examples you will need a Hugging Face Text Generation Inference server deployed, and a model served.

You can either install Langchain and its dependencies in your workbench (`pip install langchain`), or you can directly use a pre-built custom Workbench image that comes with everything needed: `quay.io/opendatahub-contrib/workbench-images:cuda-jupyter-langchain-c9s-py311_2023c_latest`.

*[Ref: How to import a custom notebook image](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_science/1/html/managing_users_and_user_resources/managing_notebook_servers#configuring-a-custom-notebook-image_user-mgmt)*

If you want to create your own custom image, with a different IDE like VSCode for example, you will find instructions [here](https://github.com/opendatahub-io-contrib/workbench-images#building-an-image).

## Content

- `Langchain-HFTGI-Basic.ipynb`: Basic example on using Langchain to query an LLM served through Hugging Face TGI.
- `Langchain-HFTGI-Prompt-memory.ipynb`: More advanced example with custom prompt and conversation memory buffer.
