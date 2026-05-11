import re
from transformers import pipeline

class IntentClassifier:

    def __init__(self):

        self.model = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

        self.labels = [
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

    def split_text(self, text, max_chars=800):

        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current = ""

        for sentence in sentences:

            if len(current) + len(sentence) < max_chars:
                current += " " + sentence
            else:
                chunk = current.strip()
                if chunk:
                    chunks.append(chunk)
                current = sentence

        if current:
            chunk = current.strip()
            if chunk:
                chunks.append(chunk)

        return chunks

    def classify_chunk(self, chunk):
        
        if not chunk or not chunk.strip():
            return {"labels": [], "scores": []}

        result = self.model(
            chunk,
            candidate_labels=self.labels
        )

        return {
            "labels": result["labels"],
            "scores": result["scores"]
        }

    def classify(self, text):

        chunks = self.split_text(text)
        
        if not chunks:
            return "other"

        scores = {}

        for chunk in chunks:

            result = self.classify_chunk(chunk)

            for label, score in zip(result["labels"], result["scores"]):

                scores[label] = scores.get(label, 0) + score
        
        if not scores:
            return "other"

        final_class = max(scores, key=scores.get)

        return final_class