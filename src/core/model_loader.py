import os
from src.core.logging import logger
from sentence_transformers import SentenceTransformer
from transformers import pipeline

_model_cache = {}

def get_model_source(model_name: str) -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    local_path = os.path.join(project_root, "models", model_name)

    return local_path if os.path.exists(local_path) else model_name

def load_model(model_name: str, model_type: str):
    cache_key = f"{model_type}_{model_name}"

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    source = get_model_source(model_name)

    if model_type == "embedding":
        model = SentenceTransformer(source)

    elif model_type == "classifier":
        model = pipeline("zero-shot-classification", model=source, tokenizer=source)

    else:
        raise ValueError("Invalid model type")

    _model_cache[cache_key] = model
    return model