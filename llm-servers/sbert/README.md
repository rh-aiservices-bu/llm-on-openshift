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

Finally, a Swagger documentation and test interface is available at `your-endpoint/docs`.

## Container images

The runtime uses a UBI9 image defined in `Containerfile` (two flavours are available, with or without GPU support, in their respective folders). Images are accessible at:

- GPU-enabled image: `quay.io/rh-aiservices-bu/sbert-runtime:1.1.0` (check for the latest version available).
- CPU-only image: `quay.io/rh-aiservices-bu/sbert-runtime-cpu:1.1.0` (check for the latest version available).

Note: the GPU image will also work without GPU, it's just bigger for nothing...

A `test_service.ipynb` example is present in the folder to test a connection to the Service once deployed.

Two arguments are available when launching the container:

- `--model_path`: indicates where the model is stored. Defaults to `/mnt/models` for compatibility with OpenShift AI Model Serving.
- `--trust_remote_code`: may be needed to be set to true for some models. Defaults to `false`.


