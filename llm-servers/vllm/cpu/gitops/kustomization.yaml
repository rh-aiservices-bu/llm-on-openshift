---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

commonLabels:
  component: vllm

resources:
# wave 0
- pvc.yaml
# wave 1
- deployment.yaml
- service.yaml