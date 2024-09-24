# Ollama Deployment

Example deployment of the [Ollama](https://github.com/ollama/ollama) server for OpenShift.

This deployment uses a UBI9 image defined in `Containerfile` and accessible at `quay.io/rh-aiservices-bu/ollama-ubi9` (check for the latest version available). The image is compiled for the **avx2** instruction set (so all Intel and AMD processors post-2016). However this image **does not support GPU acceleration** to reduce its size. It is meant to be used as a simple LLM server for tests when you don't have access to GPUs.

A notebook example using Langchain is available [here](../../examples/notebooks/langchain/Langchain-vLLM-Prompt-memory.ipynb).

## Installation

The default installation deploys the [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model, of course in its quantized Ollama version. See [Advanced installation](#advanced-installation) for instructions on how to change the model as well as various settings.

Automated Deployment:

- Use the OpenShift GitOps/ArgoCD Application definition at `gitops/ollama-app.yaml`

Manual Deployment (from the `gitops` folder):

- Create the PVC named using the file [pvc.yaml](gitops/pvc.yaml) to hold the models cache.
- Create the Deployment using the file [deployment.yaml](gitops/deployment.yaml).
- Create the Service using file [service.yaml](gitops/service.yaml).
- If you want to expose the server outside of your OpenShift cluster, create the Route with the file [route.yaml](gitops/route.yaml)

The API is now accessible at the endpoints:

- defined by your Service, accessible internally on port **11434** using http. E.g. `http://ollama.your-project.svc.cluster.local:11434/`
- defined by your Route, accessible externally through https, e.g. `https://vllm.your-project.your-cluster/`

## Usage

You can directly query the model using either the /api/generate endpoint:

```bash
curl http://service:11434/api/generate \
      -H "Content-Type: application/json" \
      -d '{
        "model": "mistral",
        "prompt":"Why is the sky blue?"
      }'
```

or from Python:

```bash
pip install ollama
```

```python
import ollama

client = ollama.Client(host='http://service:11434')

stream = client.chat(
  model='mistral',
  messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
  stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
```

You can also find a notebook example using Langchain to query Ollama in this repo [here](../../examples/notebooks/langchain/Langchain-Ollama-Prompt-memory.ipynb).
