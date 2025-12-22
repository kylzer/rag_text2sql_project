from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
import torch
import torch._dynamo
torch._dynamo.config.suppress_errors = True

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_model_cache: Dict[str, SentenceTransformer] = {}

def get_model(model_name: str) -> SentenceTransformer:
    if model_name not in _model_cache:
        logger.info(f"Loading model: {model_name}")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")

        model = SentenceTransformer(model_name, trust_remote_code=True)
        model.to(device)

        _model_cache[model_name] = model
    return _model_cache[model_name]

def embed_texts(texts: List[str], model_name: str) -> List[List[float]]:
    model = get_model(model_name)
    if not texts:
        logger.warning("Received empty input to embed_texts")
        return []
    logger.info("Do Encode!")
    with torch.no_grad():
        embeddings = model.encode(texts, batch_size=16, convert_to_numpy=True, normalize_embeddings=False)
    if embeddings.shape[0] == 0:
        logger.warning("Model returned 0 vectors!")

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    return embeddings.tolist()
