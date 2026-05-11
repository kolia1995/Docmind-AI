import os
from sentence_transformers import SentenceTransformer
from transformers import pipeline

_model_cache = {}

def load_model(model_name: str, model_type: str):
    cache_key = f"{model_type}_{model_name}"

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    # 🔥 FIX: тільки правильні HF моделі
    HF_MODELS = {
        "embedding": "sentence-transformers/all-MiniLM-L6-v2",
        "classifier": "facebook/bart-large-mnli"
    }

    if model_type == "embedding":
        source = HF_MODELS["embedding"]
        model = SentenceTransformer(source)

    elif model_type == "classifier":
        source = HF_MODELS["classifier"]
        model = pipeline("zero-shot-classification", model=source)

    else:
        raise ValueError("Invalid model type")

    _model_cache[cache_key] = model
    return model

def load_embedding_model(model_name: str = None):
    return load_model(model_name or "default", "embedding")

def load_classifier_model(model_name: str = None):
    return load_model(model_name or "default", "classifier")