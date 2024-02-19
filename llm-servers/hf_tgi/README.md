# Hugging Face Text Generation Inference Deployment

Example deployment of the [Text Generation Inference](https://github.com/huggingface/text-generation-inference) server from Hugging Face for OpenShift.

The server goes in pair with the [text-generation](https://pypi.org/project/text-generation/) library to easily consume the service.

A notebook example using Langchain is available [here](../../examples/notebooks/langchain/Langchain-HFTGI-Prompt-memory.ipynb).

## Basic Installation

The basic installation deploys the [Flan-t5-XL](https://huggingface.co/google/flan-t5-xl) model, using quantization. Although on the smaller side of LLMs, it will still require a GPU to work properly in a fast enough manner. See [Advanced installation](#advanced-installation) for instructions on how to change the model as well as various settings.

Deployment:

- Create PVC named `models-cache` with enough space to hold all the models you want to try.
- Create the Deployment using the file [deployment.yaml](deployment.yaml).
- Create the Service using file [service.yaml](service.yaml).
- If you want to expose the server outside of your OpenShift cluster, create the Route with the file [route.yaml](route.yaml)

Your model is now accessible at the endpoints:

- defined by your Service, accessible internally on port **3000 for http** and **8033 for gRPC**. E.g. `http://hf-text-generation-inference-server.your-project.svc.cluster.local:3000/`
- defined by your Route, accessible externally through https, e.g. `https://hf-text-generation-inference-server.your-project.your-cluster/`

Full API documentation (with live testing) is available under the /docs url, e.g. `https://hf-text-generation-inference-server.your-project.your-cluster/docs`

## Usage

You can directly query the model using either the /generate or /generate_stream routes:

```bash
curl 127.0.0.1:8080/generate \
    -X POST \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}' \
    -H 'Content-Type: application/json'
curl 127.0.0.1:8080/generate_stream \
    -X POST \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}' \
    -H 'Content-Type: application/json'
```

or from Python:

```bash
pip install text-generation
```

```python
from text_generation import Client

client = Client("http://127.0.0.1:8080")
print(client.generate("What is Deep Learning?", max_new_tokens=20).generated_text)

text = ""
for response in client.generate_stream("What is Deep Learning?", max_new_tokens=20):
    if not response.token.special:
        text += response.token.text
print(text)
```

## Advanced installation

### Parameters

Different environment variables are available in the Deployment so that you can tweak the way the model is deployed:

- MODEL_ID: the name of the model hosted on HuggingFace to use, e.g. `google/flan-t5-xl`.
- MAX_INPUT_LENGTH: maximum number of tokens that can be sent to the inference endpoint.
- MAX_TOTAL_TOKENS: maximum number of tokens (so MAX_INPUT + tokens generated).
- QUANTIZE: if you want your model to be quantized. Possible values `bitsandbytes`, `bitsandbytes-nf4` and `bitsandbytes-fp4`.
- HUGGINGFACE_HUB_CACHE: where the models are cached. Default value for the Deployment is `/models-cache`, where the PVC you created for this purpose is mounted.
- HUGGING_FACE_HUB_TOKEN: if you model requires an authorization to be downloaded (e.g. **Llama2**), use this parameter to enter you Hugging Face API token. The best is to load it from a secret.

Please refer to the documentation for other parameters you can modify.

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
