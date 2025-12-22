from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Union

from do_embed import embed_texts

app = FastAPI()

class EmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]


@app.post("/v1/embeddings")
async def create_embedding(request: EmbeddingRequest):
    try:
        # Ensure keys exist
        input_data = request.input
        model = request.model

        # Coerce to list if needed
        if isinstance(input_data, str):
            input_data = [input_data]
        if not isinstance(input_data, list):
            raise HTTPException(status_code=422, detail="'input' must be a string or list of strings")
            
        vectors = embed_texts(input_data, request.model)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    data = [
        {"object": "embedding", "index": i, "embedding": vec}
        for i, vec in enumerate(vectors)
    ]

    return {
        "object": "list",
        "data": data,
        "model": request.model,
        "usage": {
            "prompt_tokens": sum(len(text.split()) for text in request.input),
            "total_tokens": sum(len(text.split()) for text in request.input),
        }
    }
@app.post("/api/embed")
async def create_ollama_embedding(request: Request):
    body = await request.json()
    print(body)

    # Ensure keys exist
    input_data = body.get("prompt") or body.get("input")
    model = body.get("model")

    if not input_data:
        raise HTTPException(status_code=422, detail="Missing 'prompt' or 'input' field")
    
    if not model:
        raise HTTPException(status_code=422, detail="Missing 'model' field")

    # Coerce to list if needed
    if isinstance(input_data, str):
        input_data = [input_data]
    if not isinstance(input_data, list):
        raise HTTPException(status_code=422, detail="'input' must be a string or list of strings")

    try:
        vectors = embed_texts(input_data, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    data = [
        {"object": "embedding", "index": i, "embedding": vec}
        for i, vec in enumerate(vectors)
    ]

    response = {
        "embeddings": vectors  # Must be plural and a list of vectors
    }
    print(f"Returning {len(vectors)} embeddings")
    return response