import logging
import tempfile
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from docling_serve.settings import docling_serve_settings

# Set enable_ui to True
docling_serve_settings.enable_ui = True

# Set up custom logging as we'll be intermixes with FastAPI/Uvicorn's logging
class ColoredLogFormatter(logging.Formatter):
    COLOR_CODES = {
        logging.DEBUG: "\033[94m",  # Blue
        logging.INFO: "\033[92m",  # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.CRITICAL: "\033[95m",  # Magenta
    }
    RESET_CODE = "\033[0m"

    def format(self, record):
        color = self.COLOR_CODES.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{self.RESET_CODE}"
        return super().format(record)


logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(levelname)s:\t%(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

# Override the formatter with the custom ColoredLogFormatter
root_logger = logging.getLogger()  # Get the root logger
for handler in root_logger.handlers:  # Iterate through existing handlers
    if handler.formatter:
        handler.setFormatter(ColoredLogFormatter(handler.formatter._fmt))

_log = logging.getLogger(__name__)

##################################
# App creation and configuration #
##################################

def update_last_activity():
    # Update the last activity timestamp
    docling_serve_settings.last_activity = datetime.now()

def get_last_activity():
    return docling_serve_settings.last_activity

def create_app():
    app = FastAPI(
        title="Docling Serve",
        # lifespan=lifespan,
    )

    origins = ["*"]
    methods = ["*"]
    headers = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=methods,
        allow_headers=headers,
    )

    # Mount the Gradio app
    if docling_serve_settings.enable_ui:
        print("importing gradio")

        import gradio as gr
        from docling_serve.gradio_ui import ui as gradio_ui

        tmp_output_dir = Path(tempfile.mkdtemp())
        gradio_ui.gradio_output_dir = tmp_output_dir
        app = gr.mount_gradio_app(
            app,
            gradio_ui,
            path="/ui",
            allowed_paths=["./logo.png", tmp_output_dir],
            root_path="/ui",
        )

    # Initialize the last activity timestamp
    update_last_activity()

    #############################
    # API Endpoints definitions #
    #############################

    # Favicon
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        response = RedirectResponse(
            url="https://ds4sd.github.io/docling/assets/logo.png"
        )
        return response

    # Status
    class HealthCheckResponse(BaseModel):
        status: str = "ok"

    # Kernel response model for OpenShift AI compatibility
    class KernelResponse(BaseModel):
        id: str
        name: str
        last_activity: str
        execution_state: str
        connections: int

    @app.get("/")
    async def root():
        print("entering root")
        return RedirectResponse(url="/ui")

    @app.get("/health")
    def health() -> HealthCheckResponse:
        return HealthCheckResponse()
  
    # Enhanced OpenShift AI Workbench compatibility endpoints
    nb_prefix = os.environ.get("NB_PREFIX", "")
         
    # Basic API health check
    @app.get(f"{nb_prefix}/api", include_in_schema=False)
    @app.get(f"{nb_prefix}/api/", include_in_schema=False)
    def api_check() -> HealthCheckResponse:
        return HealthCheckResponse()
    
    # Kernels and Terminals check for OpenShift AI
    @app.get(f"{nb_prefix}/api/kernels", include_in_schema=False)
    @app.get(f"{nb_prefix}/api/kernels/", include_in_schema=False)
    def api_kernels():
        return []
    
    @app.get(f"{nb_prefix}/api/terminals", include_in_schema=False)
    @app.get(f"{nb_prefix}/api/terminals/", include_in_schema=False)
    def api_terminals():
        return [{"name": "1", "last_activity": get_last_activity()}]
    
    if nb_prefix != "":
        # Redirect all other prefixed requests to ui
        @app.get(f"{nb_prefix}/{{path:path}}", include_in_schema=False)
        async def redirect(path: str):
            if path and not (path.startswith("api") or path == "health"):
                return RedirectResponse(url="/ui")
                
        @app.get(f"{nb_prefix}", include_in_schema=False)
        async def root_redirect():
            return RedirectResponse(url="/ui")

    return app