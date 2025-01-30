# SBert Serving

This custom runtime can be used to serve [Sentence-Transformers](https://huggingface.co/sentence-transformers) models.

It provides an OpenAI-compatible API, so you can call the model at `your-endpoint/v1/embeddings`.

The request format is:

```json
{
  "encoding_format": "float",
  "input": [
    "I am a sentence",
    "I am another sentence"
  ],
  "model": "model_name"
}
```

- "input" can be a string or an array of string.
- "model" can be any string, even empty, as the runtime serves only one model. It is there for OpenAI API compatibility.
- "encoding_format" is optional and defaults to "float".

The answer will be in the following format:

```json
{
  "object": "list",
  "model": "nomic-embed-text-v1.5",
  "data": [
      {
          "index": 0,
          "embedding": [0.1, 0.2, 0.3],
          "object": "embedding",
      },
      {
          "index": 1,
          "embedding": [0.2, 0.5, 0.7],
          "object": "embedding",
      },
  ],
  "usage": {"prompt_tokens": 5, "total_tokens": 5},
}
```

Finally, a Swagger documentation and test interface is available at `your-endpoint/docs`.

## Container images

The runtime uses a UBI9 image defined in `Containerfile` (two flavours are available, with or without GPU support, in their respective folders). Images are accessible at:

- GPU-enabled image: `quay.io/rh-aiservices-bu/sbert-runtime:1.2.0` (check for the latest version available).
- CPU-only image: `quay.io/rh-aiservices-bu/sbert-runtime-cpu:1.2.0` (check for the latest version available).

Note: the GPU image will also work without GPU, it's just bigger for nothing...

A `test_service.ipynb` example is present in the folder to test a connection to the Service once deployed.

Two arguments are available when launching the container:

- `--model-path`: indicates where the model is stored. Defaults to `/mnt/models` for compatibility with OpenShift AI Model Serving.
- `--trust-remote_code`: may be needed to be set to true for some models. Defaults to `false`.

The environment variable `UVICORN_WORKERS` can also be set to have multiple workers spawned simultaneously (default 1). Useful when you want to maximize the usage of the GPU that will be assigned to a single Pod as the different workers will be able to share the GPU.
