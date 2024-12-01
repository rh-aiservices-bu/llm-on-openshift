import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Annotated, List, Optional, Union

from docling.cli.main import convert as docling_convert
from dotenv import dotenv_values, load_dotenv
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from uvicorn import run

# Load local env vars if present
load_dotenv()

# App creation
app = FastAPI()

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


# Define the input options for the API
class DoclingBaseParameters(BaseModel):
    from_format: Optional[Union[List[str], str]] = Field(
        ["pdf", "docx", "pptx", "html", "image", "asciidoc", "md"],
        description="Input format(s) to convert from. String or list of strings. Allowed values: docx, pptx, html, image, pdf, asciidoc, md. Optional, defaults to all formats.",
        examples=[["pdf", "docx"]],
    )
    to_format: Optional[Union[List[str], str]] = Field(
        ["md"],
        description="Output format(s) to convert to. String or list of strings. Allowed values: md, json, text, doctags. Optional, defaults to Markdown.",
        examples=["md"],
    )
    ocr: Optional[bool] = Field(
        True,
        description="If enabled, the bitmap content will be processed using OCR. Boolean. Optional, defaults to true",
        examples=[True],
    )
    force_ocr: Optional[bool] = Field(
        False,
        description="If enabled, replace any existing text with OCR-generated text over the full content. Boolean. Optional, defaults to false.",
        examples=[False],
    )
    ocr_engine: Optional[str] = Field(
        "easyocr",
        description="The OCR engine to use. String. Allowed values: easyocr, tesseract_cli, tesseract. Optional, defaults to easyocr.",
        examples=["easyocr"],
        pattern="easyocr|tesseract_cli|tesseract",
    )
    pdf_backend: Optional[str] = Field(
        "dlparse_v1",
        description="The PDF backend to use. String. Allowed values: pypdfium2, dlparse_v1, dlparse_v2. Optional, defaults to dlparse_v1.",
        examples=["dlparse_v1"],
        pattern="pypdfium2|dlparse_v1|dlparse_v2",
    )
    table_mode: Optional[str] = Field(
        "fast",
        description="Mode to use for table structure, String. Allowed values: fast, accurate. Optional, defaults to fast.",
        examples=["fast"],
        pattern="fast|accurate",
    )
    abort_on_error: Optional[bool] = Field(
        False,
        description="Abort on error if enabled. Boolean. Optional, defaults to false.",
        examples=[False],
    )
    return_as_file: Optional[bool] = Field(
        False,
        description="Return the output as a zip file (will happen anyway if multiple files are generated). Boolean. Optional, defaults to false.",
        examples=[False],
    )


class DoclingParameters(DoclingBaseParameters):
    source: Union[List[str], str] = Field(
        ...,
        description="Source(s) to process.",
        examples=["https://arxiv.org/pdf/2206.01062"],
    )


def docling_processing(
    docling_params: DoclingParameters, tmp_input_dir: Optional[str] = None
):
    # Create a temporary directory to store the output
    tmp_output_dir = Path(tempfile.mkdtemp())

    # Get worker pid to use in file identification
    worker_pid = os.getpid()

    try:
        docling_convert(
            input_sources=docling_params.source,
            from_formats=docling_params.from_format,
            to_formats=docling_params.to_format,
            ocr=docling_params.ocr,
            force_ocr=docling_params.force_ocr,
            ocr_engine=docling_params.ocr_engine,
            pdf_backend=docling_params.pdf_backend,
            table_mode=docling_params.table_mode,
            abort_on_error=docling_params.abort_on_error,
            output=Path(tmp_output_dir),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing docling: {str(e)}"
        )

    # Check if there is a single file in the output directory
    files = os.listdir(tmp_output_dir)
    try:
        background_tasks = BackgroundTasks()
        # Determine the file to return
        if len(files) == 1:
            file_path = f"{tmp_output_dir}/{files[0]}"
        elif len(files) > 1:
            file_path = f"/tmp/{worker_pid}converted_docs.zip"
            shutil.make_archive(
                base_name=f"/tmp/{worker_pid}converted_docs",
                format="zip",
                root_dir=tmp_output_dir,
            )
            docling_params.return_as_file = True  # Force return as a file

        # Schedule cleanups after the response is sent
        # Cleanup the output directory
        background_tasks.add_task(shutil.rmtree, tmp_output_dir, ignore_errors=True)
        # Cleanup any Docling temporary directories
        for dir_name in os.listdir("/tmp"):
            dir_path = os.path.join("/tmp", dir_name)
            if os.path.isdir(dir_path) and dir_name.startswith("tmp"):
                dir_mtime = os.path.getmtime(dir_path)
                # Only remove dirs older than 10 minutes
                if (time.time() - dir_mtime) > 600:
                    background_tasks.add_task(
                        shutil.rmtree, dir_path, ignore_errors=True
                    )
        # Cleanup the existing /tmp/converted_docs.zip if it exists
        if os.path.exists(f"/tmp/{worker_pid}converted_docs.zip"):
            background_tasks.add_task(os.remove, f"/tmp/{worker_pid}converted_docs.zip")
        # Cleanup the temporary input directory
        if tmp_input_dir:
            background_tasks.add_task(shutil.rmtree, tmp_input_dir, ignore_errors=True)

        if docling_params.return_as_file:
            # Detect the file type and set the appropriate media type
            if file_path.endswith(".md"):
                media_type = "text/markdown"
            elif file_path.endswith(".json"):
                media_type = "application/json"
            elif file_path.endswith(".txt"):
                media_type = "text/plain"
            elif file_path.endswith(".zip"):
                media_type = "application/zip"
            else:
                media_type = "application/octet-stream"
            # Remove {worker_pid} from the filename if present
            filename = os.path.basename(file_path).replace(f"{worker_pid}", "")
            response = FileResponse(file_path, filename=filename, media_type=media_type)
        else:
            response = FileResponse(file_path)

        # Attach the cleanup background tasks
        response.background = background_tasks

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing output: {str(e)}"
        )


#############################
# API Endpoints definitions #
#############################


# Status
@app.get("/health")
async def health():
    """Basic status"""
    return {"message": "Status:OK"}


@app.post("/process_url")
def process_url(docling_params: DoclingParameters):
    # Explode the source list in case a single string is provided with comma-separated URLs
    # This will also directly convert single str to List[str]
    if isinstance(docling_params.source, str):
        docling_params.source = docling_params.source.split(",")

    return docling_processing(docling_params)


@app.post("/process_file")
def process_file(
    files: List[UploadFile] = File(...), params: DoclingBaseParameters = Depends()
):
    # Create a temporary directory to store the file(s)
    tmp_input_dir = Path(tempfile.mkdtemp())

    # Save the uploaded files to the temporary directory
    file_paths = []
    for file in files:
        file_location = tmp_input_dir / file.filename
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(str(file_location))

    # Explode the from_format and to_format to lists
    if isinstance(params.from_format[0], str):
        params.from_format = params.from_format[0].split(",")
    if isinstance(params.to_format[0], str):
        params.to_format = params.to_format[0].split(",")

    # Set the arrays to None if they are empty
    if params.from_format == [""]:
        params.from_format = None
    if params.to_format == [""]:
        params.to_format = None

    # Process the files
    docling_params = DoclingParameters(
        source=file_paths,
        from_format=params.from_format,
        to_format=params.to_format,
        ocr=params.ocr,
        force_ocr=params.force_ocr,
        ocr_engine=params.ocr_engine,
        pdf_backend=params.pdf_backend,
        table_mode=params.table_mode,
        abort_on_error=params.abort_on_error,
        return_as_file=params.return_as_file,
    )

    return docling_processing(docling_params, tmp_input_dir=tmp_input_dir)


# Launch the FastAPI server
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    workers = int(os.getenv("UVICORN_WORKERS", "1"))
    run("app:app", host="0.0.0.0", port=port, workers=workers, timeout_keep_alive=600)
