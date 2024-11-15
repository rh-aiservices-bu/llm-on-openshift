# Docling

![Docling](https://github.com/DS4SD/docling/raw/main/docs/assets/docling_processing.png)

[Docling](https://github.com/DS4SD/docling) parses documents and exports them to the desired format with ease and speed.

**Docling-server** is a container image of Docling installed behind an API server. It provides endpoints to process documents from URLs or uploaded files, leveraging the powerful Docling library for document conversion.

This allows for an easy deployment of Docling as a shared central instance that can be used by different applications or code, like a microservice.

The deployment can be a standard one in OpenShift, or leverage the Model Serving capabilities of OpenShift AI for ease of use.

## Deployment

Two pre-built images are available:

- CUDA enabled: acceleration of the EasyOCR module and Docling itself. NVidia GPU required. Image name: `docling-server:cuda-x.y.z`
- CPU only: standard image not requiring any GPU. Image name: `docling-server:cpu-x.y.z`

Both images are available at [https://quay.io/repository/rh-aiservices-bu/docling-server?tab=tags](https://quay.io/repository/rh-aiservices-bu/docling-server?tab=tags).

Those deployment examples are using the CUDA version of image. Adapt to use the CPU-only version.

### As a standalone deployment

In the [standalone-deployment](./standalone-deployment/) folder, you will find an example of Deployment, Service and Route files. You can use them to deploy **docling-server** and make it available.

This is an example only! Adapt the files, and especially the Deployment to your context (CPU, RAM, GPU, toleration,...).

### Locally

The container images, although quite big, can be used locally with Podman, using GPU acceleration or not. You must simply open the port 8080.

`podman run --rm -it -p 8080:8080 --device nvidia.com/gpu=all localhost/docling-server:cuda-0.0.4`

### As a "Model Server" in OpenShift AI

In the [serving-runtime](./serving-runtime/) folder, you will find an example of a ServingRuntime and InferenceService YAML that will allow you to deploy **docling-server** using OpenShift AI Model Serving.

NOTE: this is a "hack" of OpenShift AI Model Serving. The image does not need any model (they are all included), but the Data Connection is required and the model path cannot be empty. So the trick is simply to put an empty file (or whatever file you want) at the location you define through the data connection and path. Model Serving is happy!

## Usage Instructions

### Endpoint: `/process_url`

This endpoint processes documents from provided URLs.

**Method:** `POST`

**Parameters:**

Parameters are the same as the Docling CLI, plus the source:

- `source` (Union[List[str], str]): Source(s) to process. Can be a single URL string, a List of URL strings, or a single string with comma-separated URs.
- `from_format` (Optional[Union[List[str], str]]): Input format(s) to convert from. Allowed values: `docx`, `pptx`, `html`, `image`, `pdf`, `asciidoc`, `md`. Defaults to all formats.
- `to_format` (Optional[Union[List[str], str]]): Output format(s) to convert to. Allowed values: `md`, `json`, `text`, `doctags`. Defaults to Markdown.
- `ocr` (Optional[bool]): If enabled, the bitmap content will be processed using OCR. Defaults to true.
- `force_ocr` (Optional[bool]): If enabled, replace any existing text with OCR-generated text over the full content. Defaults to false.
- `ocr_engine` (Optional[str]): OCR engine to use. Allowed values: `easyocr`, `tesseract_cli`, `tesseract`. Defaults to `easyocr`.
- `pdf_backend` (Optional[str]): PDF backend to use. Allowed values: `pypdfium2`, `dlparse_v1`, `dlparse_v2`. Defaults to `dlparse_v1`.
- `table_mode` (Optional[str]): Table mode to use. Allowed values: `fast`, `accurate`. Defaults to `fast`.
- `abort_on_error` (Optional[bool]): If enabled, abort on error. Defaults to false.
- `return_as_file` (Optional[bool]): If enabled, return the output as a file. Defaults to false.

**Example Request:**

```json
{
  "source": "https://arxiv.org/pdf/2206.01062",
  "from_format": ["pdf"],
  "to_format": ["md"],
  "ocr": true,
  "force_ocr": false
}
```

### Endpoint: `/process_file`

This endpoint processes uploaded files.

**Method:** `POST`

**Parameters:**

- files (form parameter): File(s) to upload.
- The other parameters are the same as the ones for the url endpoint.

Example Request:

```bash
curl -X POST "http://localhost:8080/process_file" -F "files=@/path/to/file.pdf" -F "params={\"from_format\": [\"pdf\"], \"to_format\": [\"md\"], \"ocr\": true, \"force_ocr\": false}"
```

### Swagger UI

You can interact with the API endpoints using the Swagger UI available at `/docs`. This provides a user-friendly interface to test the endpoints and view the available parameters.

## Container image

This is a simple Python container image, with Docling installed with all its dependencies, FastAPI server to expose the API, and the models pre-downloaded.
