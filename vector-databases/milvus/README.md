# Milvus

[Milvus](https://milvus.io/) is Vector database built for scalable similarity search. It is "Open-source, highly scalable, and blazing fast".

As Milvus supports meany features, the easiest way to understand what it can do is to head to the relevant [documentation](https://milvus.io/docs/overview.md).

Milvus also provides great documentation, starting with a full description of its architecture.

![Architecture](https://milvus.io/docs/v2.4.x/assets/milvus_architecture.png)

## Deployment

### Requirements

- Access to the OpenShift cluster.
- A default StorageClass must be configured.

### Deployment Options

The following recipes will deploy a default installation of Milvus, either standalone or in cluster mode, with authentication enabled. However, many things can be modified in this configuration, through the provided `openshift-values.yaml` file.

- The default Milvus deployment leverages Minio to store logs and index files. This can be replaced by another S3 storage system
- Default configuration uses Pulsar for managing logs of recent changes, outputting stream logs, and providing log subscriptions. This can be replaced by Kafka

To modify those components, as well many other configuration parameters, please refer to the [configuration documentation](https://milvus.io/docs/deploy_s3.md) and modify the values file according to your needs.

### Deployment procedure

Milvus can be deployed in Standalone or Cluster mode. Cluster mode, leveraging Pulsar, etcd and Minio for data persistency, will bring redundancy, as well as easy scale up and down of the different components.

Although Milvus features an operator to easily deploy it in a Kubernetes environment, this method has not been tested yet, while waiting for the different corrections to be made to the deployment code for OpenShift specificities.

Instead, this deployment method is based on the [Offline installation](https://milvus.io/docs/install_offline-helm.md) that purely rely on Helm Charts.

- Log into your OpenShift cluster, and create a new project to host your Milvus installation:

  ```bash
  oc new-project milvus
  ```

- Add and update Milvus Helm repository locally:

  ```bash
  helm repo add milvus https://zilliztech.github.io/milvus-helm/
  helm repo update
  ```

- Fetch the file [`openshift-values.yaml`](openshift-values.yaml) from this repo. This file is really important as it sets specific values for OpenShift compatibility. You can also modify some of the values in this file to adapt the deployment to your requirements, notably modify the Minio admin user and password.

    ```bash
    wget https://raw.githubusercontent.com/rh-aiservices-bu/llm-on-openshift/main/vector-databases/milvus/openshift-values.yaml
    ```

- Create the manifest:
  - For Milvus standalone:

    ```bash
    helm template -f openshift-values.yaml vectordb --set cluster.enabled=false --set etcd.replicaCount=1 --set minio.mode=standalone --set pulsar.enabled=false milvus/milvus > milvus_manifest_standalone.yaml
    ```

  - For Milvus cluster:

    ```bash
    helm template -f openshift-values.yaml vectordb milvus/milvus > milvus_manifest_cluster.yaml
    ```

- **VERY IMPORTANT**: you must patch the generated manifest, as some settings are incompatible with OpenShift. Those commands are using the **[yq tool](https://mikefarah.gitbook.io/yq/)** (beware, the real one, not the Python version):
  - For Milvus Standalone:
  
    ```bash
    yq '(select(.kind == "StatefulSet" and .metadata.name == "vectordb-etcd") | .spec.template.spec.securityContext) = {}' -i milvus_manifest_standalone.yaml
    yq '(select(.kind == "StatefulSet" and .metadata.name == "vectordb-etcd") | .spec.template.spec.containers[0].securityContext) = {"capabilities": {"drop": ["ALL"]}, "runAsNonRoot": true, "allowPrivilegeEscalation": false}' -i milvus_manifest_standalone.yaml
    yq '(select(.kind == "Deployment" and .metadata.name == "vectordb-minio") | .spec.template.spec.containers[0].securityContext) = {"capabilities": {"drop": ["ALL"]}, "runAsNonRoot": true, "allowPrivilegeEscalation": false, "seccompProfile": {"type": "RuntimeDefault"} }' -i milvus_manifest_standalone.yaml
    yq '(select(.kind == "Deployment" and .metadata.name == "vectordb-minio") | .spec.template.spec.securityContext) = {}' -i milvus_manifest_standalone.yaml
    ```

  - For Milvus Cluster:
  
    ```bash
    yq '(select(.kind == "StatefulSet" and .metadata.name == "vectordb-etcd") | .spec.template.spec.securityContext) = {}' -i milvus_manifest_cluster.yaml
    yq '(select(.kind == "StatefulSet" and .metadata.name == "vectordb-etcd") | .spec.template.spec.containers[0].securityContext) = {"capabilities": {"drop": ["ALL"]}, "runAsNonRoot": true, "allowPrivilegeEscalation": false}' -i milvus_manifest_cluster.yaml
    yq '(select(.kind == "StatefulSet" and .metadata.name == "vectordb-minio") | .spec.template.spec.securityContext) = {"capabilities": {"drop": ["ALL"]}, "runAsNonRoot": true, "allowPrivilegeEscalation": false}' -i milvus_manifest_cluster.yaml
    ```

- Deploy Milvus (eventually change the name of the manifest)!

  - For Milvus Standalone:
  
    ```bash
    oc apply -f milvus_manifest_standalone.yaml
    ```

  - For Milvus Cluster:
  
    ```bash
    oc apply -f milvus_manifest_cluster.yaml
    ```

- To deploy the management UI for Milvus, called Attu, apply the file [attu-deployment.yaml](attu-deployment.yaml):

  ```bash
  oc apply -f https://raw.githubusercontent.com/rh-aiservices-bu/llm-on-openshift/main/vector-databases/milvus/attu-deployment.yaml
  ```

NOTE: Attu deployment could have been done through the Helm chart, but this would not properly create the access Route.

Milvus is now deployed, with authentication enabled. The default and only admin user is `root`, with the default password `Milvus`. Please see the following section to modify this root access and create the necessary users and roles.

## Day-2 operations

Milvus implements a full RBAC system to control access to its databases and collections. It is recommended to:

- Change the default password
- Create collections
- Create users and roles to give read/write or read access to the different collections

All of this can be done either using the PyMilvus library, or the Attu UI deployed in the last step.

Milvus features an [awesome documentation](https://milvus.io/docs), detailing all the configuration, maintenance, and operations procedure. This is a must-read to grasp all aspects of its architecture and usage.

## Usage

Several example notebooks are available to show how to use Milvus:

- Collection creation and document ingestion using Langchain: [Langchain-Milvus-Ingest.ipynb](../../examples/notebooks/langchain/Langchain-Milvus-Ingest.ipynb)
- Collection creation and document ingestion using Langchain with Nomic AI Embeddings: [Langchain-Milvus-Ingest-nomic.ipynb](../../examples/notebooks/langchain/Langchain-Milvus-Ingest-nomic.ipynb)
- Query a collection using Langchain: [Langchain-Milvus-Query.ipynb](../../examples/notebooks/langchain/Langchain-Milvus-Query.ipynb)
- Query a collection using Langchain with Nomic AI Embeddings: [Langchain-Milvus-Query-nomic.ipynb](../../examples/notebooks/langchain/Langchain-Milvus-Query-nomic.ipynb)
