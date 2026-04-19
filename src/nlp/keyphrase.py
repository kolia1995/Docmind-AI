from keybert import KeyBERT
from src.nlp.classifier import Classifier
from src.core.logging import logger
from src.core.model_loader import load_embedding_model

class Keyberts:
    def __init__(
        self,
        model_name: str = "miniLM",
        top_n: int = 15,
        ngram_range: tuple = (1, 1),
        use_mmr: bool = False,
        diversity: float = 0.5,
    ):
        logger.info(f"Initializing Keyberts with embedding model: {model_name}")
        self.embedding_model = load_embedding_model(model_name)
        self.kw_model = KeyBERT(model=self.embedding_model)

        self.classifier = Classifier()

        self.top_n = top_n
        self.ngram_range = ngram_range
        self.use_mmr = use_mmr
        self.diversity = diversity

    def extract(self, text: str):
        if not text or not text.strip():
            logger.warning("Empty text received for keyword extraction")
            return []

        logger.debug(f"Extracting keywords from text (length: {len(text)})")
        return self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=self.ngram_range,
            top_n=self.top_n,
            use_mmr=self.use_mmr,
            diversity=self.diversity,
        )

    def response(self, text: str):
        logger.info("Processing text for keywords and classification")
        keywords_raw = self.extract(text)
        keywords = [kw[0] for kw in keywords_raw if kw and kw[0]]
        logger.debug(f"Extracted {len(keywords)} keywords")

        classification_input = text + " " + " ".join(keywords)

        result = self.classifier.classify(classification_input)
        logger.debug(f"Classification result: {result.get('label')} ({result.get('score')})")

        return {
            "keywords": keywords,
            "category": result.get("label"),
            "confidence": result.get("score"),
        }