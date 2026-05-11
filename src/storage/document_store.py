import ast
import numpy as np

from database.queries import DatabaseManager
from src.llm.groq_provider import GroqProvider
from src.core.model_loader import load_embedding_model
from src.nlp.classification.intent_classifier import IntentClassifier


embedding_model = load_embedding_model("miniLM")

class DocumentStore:
    def __init__(self):
        self.db = DatabaseManager()
        self.llmGroq = GroqProvider()
        self.classifier = IntentClassifier()
        self.embedding = embedding_model


    def save(self, text: str):
        vector = np.array(self.embedding.encode(text), dtype="float32").tolist()
        category = self.classifier.classify(text)

        self.db.execute("""
            INSERT INTO documents (text, category, embedding)
            VALUES (%s, %s, %s);
        """, (text, category, vector))

        return True

    def search(self, text: str):
        query_vector = np.array(self.embedding.encode(text), dtype="float32")
        category = self.classifier.classify(text)

        rows = self.db.fetchall("""
            SELECT text, embedding
            FROM documents
            WHERE category = %s
            LIMIT 5;
        """, (category,))

        best_text = ""
        best_score = -1

        for db_text, embedding in rows:

            if isinstance(embedding, str):
                embedding = ast.literal_eval(embedding)

            db_vector = np.array(embedding, dtype="float32")

            score = np.dot(query_vector, db_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(db_vector)
            )

            if score > best_score:
                best_score = score
                best_text = db_text

        return best_text