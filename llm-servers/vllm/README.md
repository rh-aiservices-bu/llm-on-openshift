# vLLM Deployment

Example deployment of the [vLLM](https://github.com/vllm-project/vllm) server for OpenShift.

This deployment uses a UBI9 image defined in `Containerfile` and accessible at `quay.io/rh-aiservices-bu/vllm-openai-ubi9` (check for the latest version available).

This image implement the OpenAI API interface for maximum compatibility with other tools. See [here](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-compatible-server) for more information.

A notebook example using Langchain is available [here](../../examples/notebooks/langchain/Langchain-vLLM-Prompt-memory.ipynb).

## Installation

The default installation deploys the [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) model. Although on the smaller side of LLMs, it will still require a GPU to work properly in a fast enough manner. See [Advanced installation](#advanced-installation) for instructions on how to change the model as well as various settings.

Automated Deployment:

- Use the OpenShift GitOps/ArgoCD Application definition at `gitops/vllm-app.yaml`

Manual Deployment (from the `gitops` folder):

- Create PVC named `vllm-models-cache` with enough space to hold all the models you want to try.
- Create the Deployment using the file [deployment.yaml](gitops/deployment.yaml).
- Create the Service using file [service.yaml](gitops/service.yaml).
- If you want to expose the server outside of your OpenShift cluster, create the Route with the file [route.yaml](gitops/route.yaml)

The API is now accessible at the endpoints:

- defined by your Service, accessible internally on port **8000** using http. E.g. `http://vllm.your-project.svc.cluster.local:8000/`
- defined by your Route, accessible externally through https, e.g. `https://vllm.your-project.your-cluster/`

## Usage

You can directly query the model using either the /v1/completions or /v1/completions endpoints:

```bash
curl http://service:8000/v1/completions \
      -H "Content-Type: application/json" \
      -d '{
          "model": "Mistral-7B-Instruct-v0.2",
          "prompt": "San Francisco is a",
          "max_tokens": 7,
          "temperature": 0
      }'
```

```bash
curl http://service:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
          "model": "Mistral-7B-Instruct-v0.2",
          "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Who won the world series in 2020?"}
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
openai_api_base = "http://service:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model="Mistral-7B-Instruct-v0.2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]
)
print("Chat response:", chat_response)
```

## Advanced installation

### Parameters

All the parameters to start the model are passed as arguments (see L52 in the Deployment file).

The full list of available parameters is available [here](https://docs.vllm.ai/en/latest/models/engine_args.html).

### Node affinity

As an inference server is something that will run more or less permanently, you may want to dedicate a node to it, or at least set some affinity so that the Pod is scheduled on the right node. To do that, you can modify the default deployment with some taints and affinities, like in the following config. In this example, dedicated nodes are tainted with the key `shared-tgi`. In case of multiple nodes matching this taint, you can also set an affinity to be sure of being scheduled on the right node in the group.

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  ...
spec:
  ...
  template:
    metadata:
      labels:
        ...
        placement: a10g
    spec:
      restartPolicy: Always
      schedulerName: default-scheduler
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: nvidia.com/gpu.product
                    operator: In
                    values:
                      - NVIDIA-A10G-SHARED
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: placement
                      operator: In
                      values:
                        - a10g
                topologyKey: kubernetes.io/hostname
      ...
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
        - key: shared-tgi
          operator: Exists
          effect: NoSchedule
```
