from keybert import KeyBERT
from src.nlp.classification.intent_classifier import IntentClassifier
from src.core.model_loader import load_embedding_model

class KeywordExtractor:
    def __init__(
        self,
        model_name: str = "miniLM",
        top_n: int = 15,
        ngram_range: tuple = (1, 1),
        use_mmr: bool = False,
        diversity: float = 0.5,
    ):
        self.embedding_model = load_embedding_model(model_name)
        self.kw_model = KeyBERT(model=self.embedding_model)

        self.classifier = IntentClassifier()

        self.top_n = top_n
        self.ngram_range = ngram_range
        self.use_mmr = use_mmr
        self.diversity = diversity

    def extract(self, text: str):
        if not text or not text.strip():
            return []
        return self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=self.ngram_range,
            top_n=self.top_n,
            use_mmr=self.use_mmr,
            diversity=self.diversity,
        )

    def response(self, text: str):
        keywords_raw = self.extract(text)
        keywords = [kw[0] for kw in keywords_raw if kw and kw[0]]

        classification_input = text + " " + " ".join(keywords)

        result = self.classifier.classify(classification_input)

        return {
            "keywords": keywords,
            "category": result.get("label"),
            "confidence": result.get("score"),
        }
