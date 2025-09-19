-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create transcripts table with vector embeddings
CREATE TABLE IF NOT EXISTS transcripts (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    mentions_kickback BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT,
    analysis_notes TEXT,
    embedding vector(768),   -- For nomic-embed-text embeddings
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_transcripts_embedding ON transcripts 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for kickback mentions
CREATE INDEX IF NOT EXISTS idx_mentions_kickback ON transcripts(mentions_kickback);

-- Create index for filename
CREATE INDEX IF NOT EXISTS idx_filename ON transcripts(filename);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_transcripts_updated_at BEFORE UPDATE
    ON transcripts FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();