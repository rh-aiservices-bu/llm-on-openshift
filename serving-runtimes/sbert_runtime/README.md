# SBERT Runtime

This custom runtime can be used to serve [Sentence-Transformers](https://huggingface.co/sentence-transformers) models.

## Installation

You must first make sure that you have properly installed the necessary component of the Single-Model Serving stack, as documented [here](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed/2-latest/html/serving_models/serving-large-models_serving-large-models).

Once the stack is installed, adding the runtime is pretty straightforward:

- As an admin, in the OpenShift AI Dashboard, open the menu `Settings -> Serving runtimes`.
- Click on `Add serving runtime`.
- For the type of model serving platforms this runtime supports, select `Single model serving platform`.
- Upload the file `sbert-runtime.yaml` from the current folder, or click `Start from scratch` and copy/paste its content. A CPU-only version of the runtime is also available in the relevant file.

The runtime is now available when deploying a model.

## Model Deployment

This runtime can be used in the exact same way as the out of the box ones:

- Copy your model files in an object store bucket.
- Deploy the model from the Dashboard.
- Once the model is loaded, you can access the inference endpoint provided through the dashboard.

## Usage

A notebook example is available [here](../../llm-servers/sbert/test_service.ipynb).
