# SBERT Runtime

This custom runtime can be used to serve [Sentence-Transformers](https://huggingface.co/sentence-transformers) models.

It provides an OpenAI-compatible API, so you can call the model at `your-endpoint/v1/embeddings`.

The request format is:

```json
{
  "encoding_format": "float",
  "input": [
    "I am a sentence",
    "I am another sentence"
  ],
  "model": "model_name"
}
```

- "input" can be a string or an array of string.
- "model" can be any string, even empty, as the runtime serves only one model. It is there for OpenAI API compatibility.
- "encoding_format" is optional and defaults to "float".

Finally, a Swagger documentation and test interface is available at `your-endpoint/docs`.

## Installation

You must first make sure that you have properly installed the necessary component of the Single-Model Serving stack, as documented [here](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed/2-latest/html/serving_models/serving-large-models_serving-large-models).

Once the stack is installed, adding the runtime is pretty straightforward:

- As an OpenShift AI admin, in the OpenShift AI Dashboard, open the menu `Settings -> Serving runtimes`.
- Click on `Add serving runtime`.
- For the type of model serving platforms this runtime supports, select `Single model serving platform`.
- Upload the file `sbert-runtime.yaml` from the current folder, or click `Start from scratch` and copy/paste its content. A CPU-only version of the runtime is also available in the corresponding file.

Two arguments are available in the runtime definition:

- `--model_path`: indicates where the model is stored. Defaults to `/mnt/models` for compatibility with OpenShift AI Model Serving.
- `--trust_remote_code`: may be needed to be set to true for some models. Defaults to `false`.

The runtime is now available when deploying a model.

## Model Deployment

This runtime can be used in the exact same way as the out of the box ones:

- Copy your model files in an object store bucket.
- Deploy the model from the Dashboard.
- Once the model is loaded, you can access the inference endpoint provided through the dashboard.

## Usage

A notebook example is available [here](../../llm-servers/sbert/test_service.ipynb).
