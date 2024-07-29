# DeepSparse Runtime

The [DeepSparse](https://docs.neuralmagic.com/products/deepsparse/) runtime can be used with Open Data Hub and OpenShift AI Single-Model Serving stack to serve Large Language Models (LLMs). Models can be found [here](https://sparsezoo.neuralmagic.com/?modelSet=generative_ai&tasks=text_generation) and there is an optimized Granite 7B model on HuggingFace [here](https://huggingface.co/nm-testing/granite-7b-lab-pruned50-quant-ds).

The DeepSparse runtime is optimized to be able to run efficiently on **CPU**. That being said, it's always good to consider the scale of a use case before attempting to deploy CPU-based LLMs into production.

## Installation

You must first make sure that you have properly installed the necessary component of the Single-Model Serving stack, as documented [here](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed/2-latest/html/serving_models/serving-large-models_serving-large-models).

Once the stack is installed, adding the runtime is pretty straightforward:

- As an admin, in the OpenShift AI Dashboard, open the menu `Settings -> Serving runtimes`.
- Click on `Add serving runtime`.
- For the type of model serving platforms this runtime supports, select `Single model serving platform`.
- Upload the file `deepsparse-runtime.yaml` from the current folder, or click `Start from scratch` and copy/paste its content.
- Create a PVC in your project called **models-volume** (yaml [here](../../llm-servers/deepsparse/gitops/pvc.yaml)), this will be used in the serving runtime because DeepSparse serving overwrites the existing model to create one with correct input sizes, and therefore needs write access to the storage.

The runtime is now available when deploying a model.

## Model Deployment

This runtime can be used in the exact same way as the out of the box ones:

- Copy your model files in an object store bucket.
- Deploy the model from the Dashboard. Make sure you have enough RAM/CPU to run the model(s) you want.
- Once the model is loaded, you can access the inference endpoint provided through the dashboard.

## Usage

This implementation of the runtime provides an **OpenAI compatible API**. So any tool or library that can connect to OpenAI services will be able to consume the endpoint.

Note that because of the trick we are doing with saving the model to the second volume, the model will be called `/mnt/models-aux`.

Python and Curl examples are provided [here](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#using-openai-completions-api-with-vllm).

You can also find a notebook example using Langchain to query vLLM in this repo [here](../../examples/notebooks/langchain/Langchain-vLLM-Prompt-memory.ipynb).

Also, vLLM provides a full Swagger UI where you can get the full documentation of the API (methods, parameters), and try it directly without any coding,... It is accessible at the address `https://your-endpoint-address/docs`.
