# Docling Serve Client Workbench

Custom Workbench image you can use in OpenDataHub or OpenShift AI to connect to a remote [Docling Serve](https://github.com/DS4SD/docling-serve) API.

The code is a variation of the UI that comes with Docling Service, with the ability to connect to a remote server.

## Usage

Pre-build images are available at [quay.io/rh-aiservices-bu/docling-workbench](quay.io/rh-aiservices-bu/docling-workbench).

You can set your Docling Serve endpoint configuration with the following environment variables:

- `HOST`: the URL of the endpoint. Example: `https://docling-serve.mydomain.com:443`
- `AUTH_TOKEN`: the API key or Authorization token to access the endpoint.
