# HuggingFace text-generation runtime

The [HuggingFace text-generation-inference](https://github.com/huggingface/text-generation-inference) (HF TGI) runtime can be used with Open Data Hub and OpenShift AI Single-Model Serving stack to serve Large Language Models (LLMs) as an alternative to Caikit+TGIS or standalone TGIS. Currently supported models are listed [here](https://huggingface.co/docs/text-generation-inference/supported_models).

## Installation

You must first make sure that you have properly installed the necessary component of the Single-Model Serving stack, as documented [here](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed/2-latest/html/serving_models/serving-large-models_serving-large-models).

Once the stack is installed, adding the runtime is pretty straightforward:

- As an admin, in the OpenShift AI Dashboard, open the menu `Settings -> Serving runtimes`.
- Click on `Add serving runtime`.
- For the type of model serving platforms this runtime supports, select `Single model serving platform`.
- Upload the file `hf-tgi-runtime.yaml` from the current folder, or click `Start from scratch` and copy/paste its content.

The runtime is now available when deploying a model.

## Model Deployment

This runtime can be used in the exact same way as the out of the box ones:

- Copy your model files in an object store bucket.
- Deploy the model from the Dashboard.
- Make sure you have added a GPU to your GPU configuration, that you have enough VRAM (GPU memory) to load the model, and that you have enough standard memory (RAM). Although the model loads into the GPU, RAM is still used for the pre-loading operations.
- Once the model is loaded, you can access the inference endpoint provided through the dashboard.

Note: Model files must contain the model weights in `.safetensors` format. Normally HF TGI will convert .bin to `.safetensors` at runtime if they are unavailable, but because the /mnt/models directory is not writeable this will fail. You can do this conversion offline before copying your model files to the object store.

## Usage

Curl, Python, and GUI  examples are provided [here](https://huggingface.co/docs/text-generation-inference/basic_tutorials/consuming_tgi).
