CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    text TEXT,
    category TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
