import argparse
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

app = FastAPI()


class EmbeddingRequest(BaseModel):
    input: str | List[str]
    model: str
    encoding_format: Optional[str] = "float"
    dimension: Optional[int] = None
    user: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "input": ["I am a sentence", "I am another sentence"],
                    "model": "nomic-embed-text-v1.5",
                    "encoding_format": "float",
                },
            ]
        }
    }


class EmbeddingObject(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingObject]
    model: str
    usage: Optional[Dict[str, int]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
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
            ]
        }
    }


@app.get("/health")
async def status():
    return {"status": "ok"}


@app.post("/v1/embeddings")
async def create_embeddings(request: EmbeddingRequest):
    try:
        if isinstance(request.input, str):
            request.input = [request.input]

        # Calculate token counts
        total_tokens = 0
        for text in request.input:
            tokens = tokenizer.encode(text, add_special_tokens=False)
            total_tokens += len(tokens)

        # Calculate embeddings
        embeddings = model.encode(request.input)
        embeddings_list = []
        for i, embedding in enumerate(embeddings):
            embeddings_list.append(
                EmbeddingObject(index=i, embedding=embedding.tolist())
            )
        return EmbeddingResponse(
            data=embeddings_list,
            model=request.model,
            usage={"prompt_tokens": total_tokens, "total_tokens": total_tokens},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


parser = argparse.ArgumentParser(description="Load a Sentence Transformer model.")
parser.add_argument(
    "--model-path",
    type=str,
    required=False,
    default="/mnt/models",
    help="Path to the Sentence Transformer model",
)
parser.add_argument(
    "--trust-remote-code",
    type=bool,
    required=False,
    default=False,
    help="Trust remote code (default: False)",
)
args = parser.parse_args()

model = SentenceTransformer(args.model_path, trust_remote_code=args.trust_remote_code)
tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)

# Launch the FastAPI server
if __name__ == "__main__":
    from uvicorn import run

    port = int(os.getenv("PORT", "8080"))
    workers = int(os.getenv("UVICORN_WORKERS", "1"))
    run("app:app", host="0.0.0.0", port=port, workers=workers, timeout_keep_alive=600)
