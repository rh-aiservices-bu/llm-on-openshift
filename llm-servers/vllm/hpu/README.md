# vLLM Deployment

Example deployment of the [vLLM](https://github.com/vllm-project/vllm) server for OpenShift using Intel Gaudi HPU.

This deployment uses Habana image based on UBI9.4 defined in `Containerfile` and accessible at `intel/redhat-ai-services:llm-on-openshift_ubi9.4_1.20.0` (check for the latest version available).

This image implement the OpenAI API interface for maximum compatibility with other tools. See [here](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-compatible-server) for more information.

A notebook example using Langchain is available [here](../../examples/notebooks/langchain/Langchain-vLLM-Prompt-memory.ipynb).

The list of supported vLLM models for Intel Gaudi is provided [here](https://github.com/HabanaAI/vllm-fork/blob/habana_main/README_GAUDI.md#supported-configurations).

## Prerequisites
### Intel Gaudi Base Operator
Make sure that Intel Gaudi Base Operator is installed on your OpenShift cluster. Please find details [here](https://docs.habana.ai/en/latest/Installation_Guide/Additional_Installation/OpenShift_Installation/index.html?highlight=redhat). If it installed correctly and you have a node with Gaudi 2 or Gaudi 3 the command output below should be non empty:
```bash
$ kubectl get nodes -o json | jq -r '.items[] | select(.status.capacity["habana.ai/gaudi"]) | [.metadata.name, .status.capacity["habana.ai/gaudi"]] | @tsv'
```
### Hugging Face Access Token
As of April 18, 2024 some of the available models on Hugging Face are now gated - meaning that you will require a [user access token](https://huggingface.co/docs/hub/security-tokens) in order for these to be downloaded at pod startup. Perform these steps to implement this:

- Sign up for an account at [huggingface.co](https://huggingface.co), and login
- Navigate to your user profile, settings, Access Tokens
- Create a new access token, and copy the details

Please invoke following command and provide Hugging Face Access Token as parameter
```bash
./create_secret.sh $HUGGING_FACE_ACCESS_TOKEN
```

## Installation

The default installation deploys the [Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) model. Although on the smaller side of LLMs, it will still require a GPU to work properly in a fast enough manner. See [Advanced installation](#advanced-installation) for instructions on how to change the model as well as various settings.

### Automated Deployment

- Use the OpenShift GitOps/ArgoCD Application definition at `gitops/vllm-app.yaml`

### Manual Deployment using Kustomize

After logging in to OpenShift, run the following commands:

```bash
$ oc new-project vllm
$ kustomize build https://github.com/rh-aiservices-bu/llm-on-openshift.git/llm-servers/vllm/hpu/gitops | oc apply -f -
```

You can also replace the github.com URL in the kustomize command with a local path instead, if this repository has been locally cloned.

### Manual Deployment 

Using the contents of the [gitops folder](gitops), perform the following steps:

- Create PVC named `vllm-models-cache` with enough space to hold all the models you want to try.
- Create the Deployment using the file [deployment.yaml](gitops/deployment.yaml).
- Create the Service using file [service.yaml](gitops/service.yaml).
- If you want to expose the server outside of your OpenShift cluster, create the Route with the file [route.yaml](gitops/route.yaml)

## Post Installation Tasks

The API is now accessible at the endpoints:

- defined by your Service, accessible internally on port **8000** using http. E.g. `http://vllm.your-project.svc.cluster.local:8000/`
- defined by your Route, accessible externally through https, e.g. `https://vllm.your-project.your-cluster/`

vLLM also includes an OpenAPI web interface that can be access from a browser by adding `docs` to the path, e.g.  `https://vllm.your-project.your-cluster/docs`

## Usage

You can directly query the model using the [OpenAI API protocol](https://platform.openai.com/docs/api-reference/). The server currently hosts one model at a time, and currently implements [list models](https://platform.openai.com/docs/api-reference/models/list), [create chat completion](https://platform.openai.com/docs/api-reference/chat/completions/create), and [create completion](https://platform.openai.com/docs/api-reference/completions/create) endpoints.

Example of calling the /v1/models endpoint to list the available models:
```bash
curl http://vllm:8000/v1/models \
  -H 'accept: application/json'
```

Example of calling the /v1/completions endpoint to complete a sentence:
```bash
curl http://vllm:8000/v1/completions \
      -H "Content-Type: application/json" \
      -d '{
          "model": "mistralai/Mistral-7B-Instruct-v0.3",
          "prompt": "San Francisco is a",
          "max_tokens": 7,
          "temperature": 0
      }'
```

Example of calling the /v1/chat/completions endpoint demonstrating a conversation:
```bash
curl http://vllm:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "messages": [
              {"role": "user", "content": "What is Intel Gaudi HPU?"},
              {"role": "assistant", "content": "You are a helpful assistant."}
            ]
          }'
```

or from Python:

```bash
pip install text-generation
```

```python
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://vllm:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model="Mistral-7B-Instruct-v0.3",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]
)
print("Chat response:", chat_response)
```

You can also find a notebook example using Langchain to query vLLM in this repo [here](../../examples/notebooks/langchain/Langchain-vLLM-Prompt-memory.ipynb).

## Advanced installation

### Parameters

All the parameters to start the model are passed as arguments.

The full list of available parameters is available [here](https://docs.vllm.ai/en/latest/models/engine_args.html).

Intel Gaudi HPU supports additional setup via enviromental variables. The full list can be found [here](https://github.com/HabanaAI/vllm-fork/blob/habana_main/README_GAUDI.md#environment-variables). Please note the `gitops/deployment.yaml` disable vLLM model warmup, for production deployment it is recommended to enable it. You can find more details [here](https://github.com/HabanaAI/vllm-fork/blob/habana_main/README_GAUDI.md#warmup).
