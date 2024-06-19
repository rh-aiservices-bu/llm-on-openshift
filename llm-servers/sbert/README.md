# SBert Serving

This custom runtime can be used to serve [Sentence-Transformers](https://huggingface.co/sentence-transformers) models.

The runtime uses a UBI9 image defined in `Containerfile` (two flavours are available, with or without GPU support, in their respective folders). Images are accessible at:

- GPU-enabled image: `quay.io/rh-aiservices-bu/sbert-runtime:1.0.0` (check for the latest version available).
- CPU-only image: `quay.io/rh-aiservices-bu/sbert-runtime-cpu:1.0.0` (check for the latest version available).

Note: the GPU image will also work without GPU, it's just bigger for nothing...

A `test_service.ipynb` example is present in the folder to test a connection to the Service once deployed.
