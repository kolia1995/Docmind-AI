from database.queries import DatabaseManager

from src.nlp.keyphrase import Keyberts
from src.llm.groq_provider import GroqProvider
from src.core.logging import logger
from src.core.model_loader import load_embedding_model

# Load embedding model on startup
embedding_model = load_embedding_model("miniLM")

class DocumentStore:
    def __init__(self):
        logger.info("Initializing DocumentStore")
        self.cursor = DatabaseManager()

        self.llmGroq = GroqProvider()
        self.embedding = embedding_model
        self.keyberts = Keyberts()
        logger.info("DocumentStore initialized successfully")

    def save(self, text: str):
        logger.info(f"Saving document (length: {len(text)})")
        task_id = self.cursor.execute("""
            INSERT INTO tasks (name)
            VALUES (%s)
            RETURNING id;
        """, ("task",))
        
        task_id = task_id[0]
        logger.debug(f"Task created with ID: {task_id}")

        logger.debug("Generating embedding")
        vector = self.embedding.encode(text).tolist()

        self.cursor.execute("""
            INSERT INTO documents (task_id, text, embedding, source)
            VALUES (%s, %s, %s, %s);
        """, (task_id, text, vector, "upload"))
        logger.debug("Document inserted")

        logger.info("Extracting keywords and classification")
        keyword_data = self.keyberts.response(text)

        self.cursor.execute("""
            INSERT INTO results (task_id, keywords, category)
            VALUES (%s, %s, %s);
        """, (
            task_id,
            keyword_data["keywords"],
            keyword_data["category"],
        ))
        logger.info(f"Document saved successfully. Category: {keyword_data['category']}, Keywords: {len(keyword_data['keywords'])}")

        return task_id

    def search(self, query: str):
        logger.info(f"Searching for: {query}")
        keyword_data = self.keyberts.response(query)

        keywords = keyword_data["keywords"]
        category = keyword_data["category"]
        logger.debug(f"Query keywords: {keywords}, category: {category}")

        embedding = self.embedding.encode(query).tolist()

        context = self.filter(
            keywords=keywords,
            category=category,
            embedding=embedding
        )
        logger.debug(f"Found {len(context) if context else 0} relevant documents")

        prompt = f"""
            You are an AI assistant.

            Use ONLY the context below.

            Context:
            {context}

            Question:
            {query}

            Answ
        """

        logger.info("Generating response using LLM")
        result = self.llmGroq.generate(prompt)
        logger.info("Response generated successfully")
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