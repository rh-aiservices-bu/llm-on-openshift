# Ollama Runtime

The [Ollama](https://github.com/ollama/ollama) runtime can be used with Open Data Hub and OpenShift AI Single-Model Serving stack to serve Large Language Models (LLMs) as an alternative to Caikit+TGIS or standalone TGIS. Currently supported models are listed [here](https://ollama.com/library).

Note that as this runtime is specifically built for CPU only (even with a GPU it won't use it).

## Installation

You must first make sure that you have properly installed the necessary component of the Single-Model Serving stack, as documented [here](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed/2-latest/html/serving_models/serving-large-models_serving-large-models).

Once the stack is installed, adding the runtime is pretty straightforward:

- As an admin, in the OpenShift AI Dashboard, open the menu `Settings -> Serving runtimes`.
- Click on `Add serving runtime`.
- For the type of model serving platforms this runtime supports, select `Single model serving platform`.
- Upload the file `ollama-runtime.yaml` from the current folder, or click `Start from scratch` and copy/paste its content.

The runtime is now available when deploying a model.

## Model Deployment

This runtime can be used in almost the same way as the out of the box ones. A small adjustment is necessary because Ollama downloads the models directly when instructed to (populating the models on the object storage would be cumbersome and not really necessary). But as KServer will try to copy a model from object storage anyway, we have to trick it a little bit...

- Copy the file `emptyfile` to an object store bucket. In fact it can be any file, as long as the "folder" in the bucket is not empty...
- Deploy the "model" from the Dashboard. Make sure you have enough RAM/CPU to run the model(s) you want.
- At this stage, what is deployed is only the Ollama server itself, and you get an endpoint address.
- Download the model you want by querying the endpoint (replace the address with the one from your endpoint, as well as the model name):

    ```bash
    curl https://your-endpoint/api/pull \
        -k \
        -H "Content-Type: application/json" \
        -d '{"name": "mistral"}'
    ```

## Usage

You can now query the model using curl like this:

```yaml
curl https://your-endpoint/api/generate \
    -k \
    -H "Content-Type: application/json" \
    -d '{
    "model": "mistral",
    "prompt":"Why is the sky blue?"
    }'
```

You can also use the notebook example [here](../../examples/notebooks/langchain/Langchain-Ollama-Prompt-memory.ipynb). Beware, you will have adaptations to do if you're using self-signed certificates, which is the default for Single Stack Serving. More information [here](https://ai-on-openshift.io/odh-rhoai/single-stack-serving-certificate/)
