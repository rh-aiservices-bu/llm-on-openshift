# Gradio UI for Hugging Face Text Generation Inference server, with conversation memory

This is a simple UI example for a Chatbot using Gradio. The LLM backend must be a Hugging Face Text Generation Inference server.

The different parameters you can pass as environment variables are:

- INFERENCE_SERVER_URL - mandatory
- MAX_NEW_TOKENS - optional, default: 512
- TOP_K - optional, default: 10
- TOP_P - optional, default: 0.95
- TYPICAL_P - optional, default: 0.95
- TEMPERATURE - optional, default: 0.01
- REPETITION_PENALTY - optional, default: 1.03

## Deployment on OpenShift

A pre-built container image of the application is available at: `quay.io/rh-aiservices-bu/gradio-hftgi-memory:1.0.0`

In the `deployment` folder, you will find the files necessary to deploy the application:

- `deployment.yaml`: you must provide the URL of your inference server in the placeholder on L53. Please feel free to modify other parameters as you see fit.
- `service.yaml`
- `route.yaml`

## Development

- The best is to create a virtual environment using the provided `Pipfile` or `requirements.txt`.
- When you install the development section of the packages you can start coding with auto-reload on saves by launching `startdev.sh`. Gradio natively has auto-reload capabilities, but it's currently broken by other needed libraries... The Watchdog approach is universal!
