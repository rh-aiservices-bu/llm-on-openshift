import argparse
import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from uvicorn import run

app = FastAPI()

class StringArray(BaseModel):
    strings: List[str]

class Embeddings(BaseModel):
    embeddings: List[List[float]]

@app.get("/status")
async def status():
    return {"status": "ok"}

@app.post("/")
async def process_strings(input_array: StringArray):
    try:
        embeddings = model.encode(input_array.strings)
        embeddings_list = embeddings.tolist() if not isinstance(embeddings, list) else embeddings
        return {"embeddings": embeddings_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

parser = argparse.ArgumentParser(description='Load a Sentence Transformer model.')
parser.add_argument('--model_path', type=str, required=False, default='/mnt/models', help='Path to the Sentence Transformer model')
args = parser.parse_args()

model = SentenceTransformer(args.model_path)

# Launch the FastAPI server
if __name__ == "__main__":
    port = int(os.getenv('PORT', '8080'))
    run(app, host="0.0.0.0", port=port)
