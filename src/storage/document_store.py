from database.queries import DatabaseManager

from src.nlp.extraction.keyword_extraction import KeywordExtractor
from src.llm.groq_provider import GroqProvider
from src.core.model_loader import load_embedding_model

# Load embedding model on startup
embedding_model = load_embedding_model("miniLM")

class DocumentStore:
    def __init__(self):
        self.cursor = DatabaseManager()

        self.llmGroq = GroqProvider()
        self.embedding = embedding_model
        self.keyword_extractor = KeywordExtractor()

    def save(self, text: str):
        task_id = self.cursor.execute("""
            INSERT INTO tasks (name)
            VALUES (%s)
            RETURNING id;
        """, ("task",))
        
        task_id = task_id[0]

        vector = self.embedding.encode(text).tolist()

        self.cursor.execute("""
            INSERT INTO documents (task_id, text, embedding, source)
            VALUES (%s, %s, %s, %s);
        """, (task_id, text, vector, "upload"))

        keyword_data = self.keyword_extractor.response(text)

        self.cursor.execute("""
            INSERT INTO results (task_id, keywords, category)
            VALUES (%s, %s, %s);
        """, (
            task_id,
            keyword_data["keywords"],
            keyword_data["category"],
        ))

        return task_id

    def search(self, query: str):
        keyword_data = self.keyword_extractor.response(query)

        keywords = keyword_data["keywords"]
        category = keyword_data["category"]

        embedding = self.embedding.encode(query).tolist()

        context = self.filter(
            keywords=keywords,
            category=category,
            embedding=embedding
        )

        prompt = f"""
            You are an AI assistant.

            Use ONLY the context below.

            Context:
            {context}

            Question:
            {query}

            Answer:
        """

        result = self.llmGroq.generate(prompt)
        return result

    def filter(self, keywords=None, category=None, embedding=None):
        query = """
            SELECT d.text
            FROM documents d
            JOIN results r ON d.task_id = r.task_id
            WHERE 1=1
        """
        params = []

        if category:
            query += " AND r.category = %s"
            params.append(category)

        if keywords:
            query += " AND r.keywords && %s"
            params.append(keywords)

        if embedding is not None:
            query += " ORDER BY d.embedding <-> %s::vector"
            params.append(embedding)

        query += " LIMIT 10"

        rows = self.cursor.fetchall(query, tuple(params))
        return [r[0] for r in rows]