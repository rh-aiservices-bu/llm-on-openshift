# DeepSparse Deployment

This deployment can be used to serve optimized models for running on CPU, such as [these]((https://sparsezoo.neuralmagic.com/?modelSet=generative_ai&tasks=text_generation)).  
By default, it's deploying an optimized [granite-7b](https://huggingface.co/nm-testing/granite-7b-lab-pruned50-quant-ds) instruct model.

A `test_request.ipynb` example is present in the folder to test a connection to the Service once deployed.

## Installation

The default installation deploys an optimized [granite-7b](https://huggingface.co/nm-testing/granite-7b-lab-pruned50-quant-ds) instruct model. See [Advanced installation](#advanced-installation) for instructions on how to change the model as well as various settings.

Below you have a few options for how to deploy.

### Automated Deployment

- Use the OpenShift GitOps/ArgoCD Application definition at `gitops/deepsparse-app.yaml`

### Manual Deployment using Kustomize

After logging in to OpenShift, run the following commands:

```bash
$ oc new-project deepsparse-text-generation
$ kustomize build https://github.com/rh-aiservices-bu/llm-on-openshift.git/llm-servers/deepsparse/gitops | oc apply -f -
```

You can also replace the github.com URL in the kustomize command with a local path instead, if this repository has been locally cloned.

### Manual Deployment 

Using the contents of the [gitops folder](gitops), perform the following steps:

- Create PVC named `models-volume` with enough space to hold all the models you want to try.
- Create the Deployment using the file [deployment.yaml](gitops/deployment.yaml).
- Create the Service using file [service.yaml](gitops/service.yaml).
- If you want to expose the server outside of your OpenShift cluster, create the Route with the file [route.yaml](gitops/route.yaml)

## Post Installation Tasks

As of April 18, 2024 some of the available models on Hugging Face are now gated - meaning that you will require a [user access token](https://huggingface.co/docs/hub/security-tokens) in order for these to be downloaded at pod startup. Perform these steps to implement this:

- Sign up for an account at [huggingface.co](https://huggingface.co), and login
- Navigate to your user profile, settings, Access Tokens
- Create a new access token, and copy the details
- In OpenShift web console, navigate to the deployment, vllm, environment variables
- Add your token value to the `HUGGING_FACE_HUB_TOKEN` environment variable.
- Restart the deployment to roll out an updated pod.



The API is now accessible at the endpoints:

- defined by your Service, accessible internally on port **8080** using http. E.g. `http://deepsparse-text-generation.your-project.svc.cluster.local:8080/`
- defined by your Route, accessible externally through https, e.g. `https://deepsparse-text-generation.your-project.your-cluster/`

It also includes an OpenAPI web interface that can be accessed from a browser by adding `docs` to the path, e.g.  `https://deepsparse-text-generation.your-project.your-cluster/docs`

## Advanced installation

### Parameters

All the parameters to start the model are passed as arguments (see L52 in the Deployment file).

The full list of available parameters is available [here](https://github.com/neuralmagic/deepsparse/tree/main/src/deepsparse/server) and [here](https://github.com/neuralmagic/deepsparse/blob/main/src/deepsparse/server/cli.py).

## Optimize specific models

If you wish to use a model that's not present in the model zoo, you can try to optimize that model.  
Pipelines and examples are provided in this [repository](https://github.com/luis5tb/neural-magic-poc).