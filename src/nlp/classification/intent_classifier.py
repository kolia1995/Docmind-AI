from src.core.model_loader import load_classifier_model

class IntentClassifier:
    def __init__(
        self,
        model_name: str = "bart-mnli",
        labels: list = None,
    ):
        self.pipeline = load_classifier_model(model_name)

        self.labels = labels or [
            "technology",
            "business",
            "sports",
            "politics",
            "science",
            "health",
            "entertainment",
            "education",
            "finance",
            "animals",
            "travel",
            "food",
            "lifestyle",
            "environment",
            "culture",
            "other"
        ]

    def classify(self, text: str):
        if not text or not text.strip():
            return {"label": "other", "score": 0.0}

        try:
            result = self.pipeline(
                text,
                candidate_labels=self.labels
            )

            labels = result.get("labels", [])
            scores = result.get("scores", [])

            if not labels or not scores:
                return {"label": "other", "score": 0.0}

            return {
                "label": labels[0],
                "score": float(scores[0])
            }

        except Exception as e:
            return {"label": "other", "score": 0.0}
