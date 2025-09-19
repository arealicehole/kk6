-- Enhanced KK6 Planning Database Schema with Vector Support
-- Adds embedding capabilities for semantic search and improved extraction

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS planning_items CASCADE;
DROP TABLE IF EXISTS transcript_chunks CASCADE;
DROP TABLE IF EXISTS extraction_results CASCADE;
DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS extraction_sessions CASCADE;

-- Categories table: Hierarchical structure for organizing planning items
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT,
    embedding vector(768),              -- Nomic embedding for semantic category matching
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sources table: Track all information sources (transcripts, manual entry, screenshots, etc.)
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,           -- 'transcript', 'manual_entry', 'screenshot', 'document'
    reference VARCHAR(255) NOT NULL,     -- filename, session_id, document_name
    metadata JSONB DEFAULT '{}',         -- flexible metadata about the source
    processed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transcript chunks: Segmented pieces of transcripts with embeddings
CREATE TABLE transcript_chunks (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    chunk_index INTEGER NOT NULL,        -- order within the transcript
    content TEXT NOT NULL,               -- actual text content of chunk
    embedding vector(768),               -- Nomic embedding for semantic search
    word_count INTEGER,
    start_position INTEGER,              -- character position in original transcript
    end_position INTEGER,
    metadata JSONB DEFAULT '{}',         -- speaker info, timestamps, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_id, chunk_index)
);

-- Extraction sessions: Track when data was extracted and processed
CREATE TABLE extraction_sessions (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    extraction_method VARCHAR(100),      -- 'manual', 'category_iterative', 'vector_enhanced'
    extracted_by VARCHAR(100),           -- user/system identifier
    session_notes TEXT,
    categories_processed TEXT[],         -- which categories were processed
    chunks_used INTEGER[],               -- which chunk IDs were used
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_progress' -- 'in_progress', 'completed', 'failed'
);

-- Extraction results: Raw results from each category extraction (before deduplication)
CREATE TABLE extraction_results (
    id SERIAL PRIMARY KEY,
    extraction_session_id INTEGER REFERENCES extraction_sessions(id),
    category_id INTEGER REFERENCES categories(id),
    chunk_ids INTEGER[],                 -- which chunks contributed to this extraction
    raw_result JSONB NOT NULL,          -- full extracted item data
    confidence_score DECIMAL(3,2),      -- 0.00 to 1.00
    relevance_score DECIMAL(3,2),       -- how relevant chunks were to category
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Planning items: Core table for all planning information (deduplicated and approved)
CREATE TABLE planning_items (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    item_key VARCHAR(100),               -- unique identifier within category
    title VARCHAR(255) NOT NULL,        -- human readable summary
    content TEXT,                        -- full description/details
    embedding vector(768),               -- embedding of full content for similarity
    
    -- Multi-type value storage
    value_text VARCHAR(500),
    value_numeric DECIMAL,
    value_date DATE,
    value_boolean BOOLEAN,
    value_json JSONB,
    
    -- Quality and tracking
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 10),
    priority_level INTEGER DEFAULT 3,   -- 1=highest, 5=lowest priority
    
    -- Source tracking
    source_id INTEGER REFERENCES sources(id),
    extraction_session_id INTEGER REFERENCES extraction_sessions(id),
    extraction_result_ids INTEGER[],     -- which raw extractions contributed
    
    -- Deduplication and versioning
    superseded_by INTEGER REFERENCES planning_items(id),
    supersedes INTEGER[],                -- array of item IDs this replaces
    merge_source_ids INTEGER[],          -- if this item was merged from multiple extractions
    
    -- Status and organization
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'active'
    tags TEXT[],
    user_approved BOOLEAN DEFAULT FALSE,
    user_edited BOOLEAN DEFAULT FALSE,
    user_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_categories_embedding ON categories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_transcript_chunks_embedding ON transcript_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_transcript_chunks_source ON transcript_chunks(source_id, chunk_index);
CREATE INDEX idx_planning_items_embedding ON planning_items USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_planning_items_category ON planning_items(category_id);
CREATE INDEX idx_planning_items_status ON planning_items(status);
CREATE INDEX idx_extraction_results_session ON extraction_results(extraction_session_id);

-- Functions for similarity search
CREATE OR REPLACE FUNCTION find_similar_chunks(
    query_embedding vector(768),
    source_id_filter INTEGER DEFAULT NULL,
    limit_count INTEGER DEFAULT 10
) RETURNS TABLE (
    id INTEGER,
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tc.id,
        tc.content,
        1 - (tc.embedding <=> query_embedding) as similarity
    FROM transcript_chunks tc
    WHERE (source_id_filter IS NULL OR tc.source_id = source_id_filter)
        AND tc.embedding IS NOT NULL
    ORDER BY tc.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to find category-relevant chunks
CREATE OR REPLACE FUNCTION find_category_chunks(
    category_id_param INTEGER,
    source_id_param INTEGER,
    limit_count INTEGER DEFAULT 5
) RETURNS TABLE (
    chunk_id INTEGER,
    content TEXT,
    relevance_score FLOAT
) AS $$
DECLARE
    category_embedding vector(768);
BEGIN
    -- Get category embedding
    SELECT embedding INTO category_embedding 
    FROM categories 
    WHERE id = category_id_param;
    
    IF category_embedding IS NULL THEN
        RAISE EXCEPTION 'Category % has no embedding', category_id_param;
    END IF;
    
    -- Find most relevant chunks
    RETURN QUERY
    SELECT 
        tc.id,
        tc.content,
        1 - (tc.embedding <=> category_embedding) as relevance_score
    FROM transcript_chunks tc
    WHERE tc.source_id = source_id_param
        AND tc.embedding IS NOT NULL
    ORDER BY tc.embedding <=> category_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;