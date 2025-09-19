# KK6 Advanced Planning Database & Extraction System

A comprehensive AI-powered planning database system for Kanna Kickback 6 event management with advanced temporal tracking, vector-based semantic search, and intelligent extraction capabilities.

## 🚀 System Overview

The KK6 Planning Database has evolved into a sophisticated system that combines:
- **Vector-based semantic search** using pgvector and Ollama embeddings
- **Temporal tracking** with conversation chronology and item evolution
- **Advanced AI extraction** with category-specific professional prompts
- **Interactive approval workflows** with deduplication detection
- **Cross-conversation temporal superseding** for planning evolution

## ✨ Key Features

### 🧠 Advanced AI Extraction Pipeline
- **Vector Embeddings**: Nomic-embed-text via Ollama for semantic chunk similarity
- **Category-Specific Prompts**: 31 professional domain expert prompts
- **Iterative Processing**: Category-by-category extraction from ALL relevant chunks
- **OpenRouter Integration**: Structured JSON outputs with sonoma-sky-alpha model
- **Deduplication Engine**: Automatic detection and merging of similar items

### ⏰ Temporal Tracking & Evolution
- **Conversation Chronology**: Parse timestamps from filenames, track sequences
- **Item Lifecycle**: Track when items first mentioned, last updated, status changes
- **Temporal Superseding**: Automatically link newer items that supersede older ones
- **Cross-Conversation Linking**: Evolution tracking across multiple conversations

### 🎯 Interactive Approval System
- **User Review Interface**: Rich terminal UI for reviewing extracted items
- **Edit-in-Place**: Modify extracted content before approval
- **Confidence Scoring**: AI confidence levels with manual override
- **Batch Operations**: Approve, edit, decline, or skip items efficiently

### 🗄️ Enhanced Database Schema
- **pgvector Extension**: Vector similarity search capabilities
- **31 Planning Categories**: Comprehensive event planning taxonomy
- **Audit Trail**: Complete source tracking and extraction sessions
- **Migration System**: Schema evolution with backward compatibility

## 🏗️ Architecture

```
kk6-planning-database/
├── 🧠 Core Extraction Engine
│   ├── iterative_extractor.py          # Main extraction pipeline
│   ├── embedding_service.py            # Vector embeddings with Ollama
│   ├── category_prompts.py             # Professional domain prompts
│   └── complete_extraction_pipeline.py # End-to-end processing
│
├── ⏰ Temporal Tracking System
│   ├── temporal_superseding_service.py # Cross-conversation item linking
│   ├── parse_conversation_timestamps.py # Timestamp extraction
│   └── migrations/
│       ├── add_lifecycle_tracking_fields.sql
│       └── add_conversation_temporal_fields.sql
│
├── 🎯 User Interaction
│   ├── approval_interface.py           # Interactive review system
│   ├── deduplication_service.py        # Duplicate detection & merging
│   └── kk6_planning_api.py            # FastAPI server with web UI
│
├── 🗄️ Database & Setup
│   ├── setup_enhanced_db.py           # Enhanced schema with pgvector
│   ├── kk6_planning_db_schema.sql     # Base schema
│   └── check_database.py             # Database health checks
│
└── 📊 Legacy & Testing
    ├── simple_extractor.py           # Original simple extraction
    ├── test_*.py                     # Various test scripts
    └── debug_*.py                    # Debugging utilities
```

## 🚀 Quick Start

### Prerequisites
- **PostgreSQL 12+** with pgvector extension
- **Ollama** running with nomic-embed-text model
- **OpenRouter API key** for sonoma-sky-alpha model
- **Python 3.9+** with required packages

### 1. Environment Setup
```bash
# Install dependencies
pip install asyncpg fastapi uvicorn httpx numpy pydantic rich

# Setup environment variables
cat > .env << EOF
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openrouter/sonoma-sky-alpha
OLLAMA_HOST=http://localhost:11434
EOF
```

### 2. Database Initialization
```bash
# Setup enhanced database with pgvector
python setup_enhanced_db.py

# Apply temporal tracking migrations (if needed)
python apply_conversation_temporal_migration.py
python apply_lifecycle_migration.py
```

### 3. Ollama Setup
```bash
# Pull the embedding model
ollama pull nomic-embed-text

# Verify Ollama is accessible
curl http://localhost:11434/api/tags
```

### 4. Process Transcripts
```bash
# Place transcript files in ./ingest/ folder
mkdir -p ingest/
# Copy your .txt transcript files here

# Run complete extraction pipeline
python iterative_extractor.py

# Or run with approval interface
python complete_extraction_pipeline.py
```

### 5. Review & Approve Results
```bash
# Launch interactive approval interface
python approval_interface.py

# Or start web interface
python kk6_planning_api.py
# Visit: http://localhost:8090/web
```

## 🧠 Advanced Extraction Pipeline

### Vector-Based Semantic Search
The system uses **Ollama with nomic-embed-text** to create 768-dimensional embeddings for:
- **Transcript chunks**: Intelligently segmented conversation pieces
- **Category descriptions**: 31 planning categories with semantic understanding
- **Planning items**: For deduplication and superseding detection

### Category-Specific Professional Prompts
Each of the 31 categories has a specialized prompt written from a domain expert's perspective:

```python
# Example: Food & Catering prompt
"You are a professional CATERING MANAGER reviewing this Kanna Kickback 6 
planning discussion. Your expertise is in food service, beverage planning, 
and event dining logistics..."
```

**Specialized Personas Include:**
- 🏢 **Venue Management**: Venue coordinator analyzing space requirements
- 🍽️ **Food & Catering**: Catering manager for menu and service planning  
- 🌿 **Cannabis Supply**: Cannabis procurement specialist for product needs
- 💰 **Budget & Finance**: Financial planner for costs and revenue analysis
- 👥 **Staffing**: HR coordinator for personnel and scheduling needs
- ⚖️ **Legal & Compliance**: Legal advisor for regulations and permits
- 📢 **Marketing**: Marketing director for promotional strategies
- 🔒 **Security & Safety**: Security manager for crowd control and safety

### Iterative Category Processing
1. **Vector Search**: Find ALL semantically relevant chunks (no 5-chunk limit)
2. **Professional Prompting**: Apply category-specific expert prompts
3. **Structured Extraction**: OpenRouter JSON schema for reliable parsing
4. **Quality Assessment**: Confidence scoring and relevance filtering

## ⏰ Temporal Tracking System

### Conversation Chronology
```sql
-- Sources table now includes temporal fields
ALTER TABLE sources ADD COLUMN conversation_date TIMESTAMP;
ALTER TABLE sources ADD COLUMN conversation_sequence INTEGER;
ALTER TABLE sources ADD COLUMN participants TEXT[];
ALTER TABLE sources ADD COLUMN communication_method VARCHAR(50);
```

### Planning Item Lifecycle
```sql
-- Planning items track their evolution over time
ALTER TABLE planning_items ADD COLUMN first_mentioned_date TIMESTAMP;
ALTER TABLE planning_items ADD COLUMN last_updated_conversation_id INTEGER;
ALTER TABLE planning_items ADD COLUMN status_history JSONB DEFAULT '[]'::jsonb;
```

### Temporal Superseding Logic
The system automatically detects when newer conversations supersede older planning items:

```python
# Vector similarity + temporal proximity = superseding confidence
async def find_superseding_candidates(
    newer_session_id: int,
    similarity_threshold: float = 0.7,
    max_temporal_gap_days: int = 30
) -> List[SupersedingCandidate]
```

**Superseding Rules:**
- ✅ Same category items with >70% semantic similarity
- ✅ Newer conversation must be chronologically later
- ✅ Temporal gap must be reasonable (≤30 days default)
- ✅ Confidence scoring based on similarity + temporal factors

## 🎯 Interactive Approval System

### Rich Terminal Interface
The approval system provides a comprehensive review experience:

```bash
📊 Extraction Summary
┌─────────────────────────┬────────┐
│ Metric                  │ Value  │
├─────────────────────────┼────────┤
│ Total Items            │ 47     │
│ Categories with Results │ 12     │
│ Duplicate Groups       │ 3      │
│ Unique Items           │ 44     │
└─────────────────────────┴────────┘

📋 Food Catering (8 items)
┌──────────────────────────────────────┬──────────────────────────────────────┬────────┬──────────────┐
│ Title                                │ Content                              │ Conf.  │ Tags         │
├──────────────────────────────────────┼──────────────────────────────────────┼────────┼──────────────┤
│ Sushi catering partnership          │ Restaurant partnership for sushi... │ 8.5/10 │ food,sushi   │
│ Happy hour pricing strategy         │ Discounted drink prices during...   │ 7.2/10 │ drinks,bar   │
└──────────────────────────────────────┴──────────────────────────────────────┴────────┴──────────────┘
```

### User Actions
For each extracted item:
- **Approve** 🟢 - Accept as-is
- **Edit** ✏️ - Modify content, confidence, or tags before approval
- **Decline** ❌ - Reject with optional reason
- **Skip** ⏭️ - Come back later

### Deduplication Detection
Automatically identifies and suggests merges for similar items:
```
🔄 Duplicate Groups Found

Duplicate Group 1
┌─────────┬─────────────────┬─────────────────────────────────┬────────────┐
│ Type    │ Category        │ Title                           │ Similarity │
├─────────┼─────────────────┼─────────────────────────────────┼────────────┤
│ PRIMARY │ legal_compliance│ Age verification requirements   │ 100%       │
│ DUP #1  │ legal_compliance│ ID checking for alcohol sales  │ 87.3%      │
└─────────┴─────────────────┴─────────────────────────────────┴────────────┘

🔧 Merge Suggestion
┌──────────────────────────────────────────────────────────────────────────────┐
│ Suggested Merge:                                                             │
│ Title: Comprehensive age verification and ID checking procedures             │
│ Categories: legal_compliance                                                 │
│ Content: Combined requirements for both age verification...                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Schema

### Core Tables (Enhanced)
```sql
-- Categories with vector embeddings
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    embedding vector(768)  -- pgvector for semantic search
);

-- Sources with temporal tracking
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    reference VARCHAR(255) NOT NULL,
    conversation_date TIMESTAMP,           -- When conversation occurred
    conversation_sequence INTEGER,         -- Chronological order
    participants TEXT[],                   -- Who was involved
    communication_method VARCHAR(50),      -- phone, video, in-person
    metadata JSONB
);

-- Transcript chunks with embeddings
CREATE TABLE transcript_chunks (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),                 -- Semantic search capability
    word_count INTEGER,
    metadata JSONB,
    UNIQUE(source_id, chunk_index)
);

-- Planning items with lifecycle tracking
CREATE TABLE planning_items (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    value_text TEXT,
    value_numeric DECIMAL,
    value_date DATE,
    value_boolean BOOLEAN,
    value_json JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 5),
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 10),
    assigned_to VARCHAR(100),
    estimated_cost DECIMAL,
    notes TEXT,
    tags TEXT[],
    source_reference VARCHAR(255),
    extracted_from TEXT,
    extraction_confidence DECIMAL,
    superseded_by INTEGER REFERENCES planning_items(id),
    first_mentioned_date TIMESTAMP,         -- Lifecycle tracking
    last_updated_conversation_id INTEGER REFERENCES sources(id),
    status_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extraction sessions with proper timestamps
CREATE TABLE extraction_sessions (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    extraction_method VARCHAR(100) NOT NULL,
    extracted_by VARCHAR(100),
    session_notes TEXT,
    categories_processed TEXT[],
    started_at TIMESTAMP NOT NULL,          -- Fixed timestamp tracking
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Raw extraction results before approval
CREATE TABLE extraction_results (
    id SERIAL PRIMARY KEY,
    extraction_session_id INTEGER REFERENCES extraction_sessions(id),
    category_id INTEGER REFERENCES categories(id),
    chunk_ids INTEGER[],
    raw_result JSONB NOT NULL,
    confidence_score DECIMAL,
    relevance_score DECIMAL,
    processing_time_ms INTEGER
);
```

### Vector Search Functions
```sql
-- Find relevant chunks for category using threshold
CREATE OR REPLACE FUNCTION find_category_chunks_by_threshold(
    category_id_param INTEGER,
    source_id_param INTEGER,
    threshold_param DECIMAL DEFAULT 0.4
) RETURNS TABLE(
    chunk_id INTEGER,
    content TEXT,
    relevance_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tc.id,
        tc.content,
        (1 - (c.embedding <=> tc.embedding)) as relevance_score
    FROM transcript_chunks tc
    CROSS JOIN categories c
    WHERE tc.source_id = source_id_param
    AND c.id = category_id_param
    AND tc.embedding IS NOT NULL
    AND c.embedding IS NOT NULL
    AND (1 - (c.embedding <=> tc.embedding)) >= threshold_param
    ORDER BY relevance_score DESC;
END;
$$ LANGUAGE plpgsql;
```

## 📊 31 Planning Categories

The system organizes information into 31 comprehensive planning categories:

### Core Event Planning
1. **venue_management** - Space, layout, capacity, policies
2. **food_catering** - Menu, beverages, service, dietary needs
3. **cannabis_supply** - Products, compliance, consumption areas
4. **budget_finance** - Costs, revenue, payment processing
5. **staffing_volunteers** - Roles, scheduling, compensation

### Legal & Operations  
6. **legal_compliance** - Permits, regulations, insurance
7. **security_safety** - Crowd control, emergency procedures
8. **risk_management** - Contingencies, liability, mitigation
9. **permits_licensing** - Government approvals, documentation

### Marketing & Experience
10. **marketing_promotion** - Advertising, social media, outreach
11. **attendee_management** - Registration, check-in, guest services
12. **entertainment_activities** - Programming, performers, activities
13. **photography_media** - Documentation, content creation

### Logistics & Support
14. **logistics_coordination** - Timeline, task management, workflows
15. **equipment_supplies** - Rentals, materials, setup needs
16. **transportation_parking** - Access, vehicle management
17. **technology_av** - Sound, lighting, technical needs
18. **waste_management** - Cleanup, disposal, sustainability

### Strategic Planning
19. **partnerships_sponsors** - Vendor relationships, collaborations
20. **charity_component** - Toy drive, community giving
21. **communication_coordination** - Team communication, updates
22. **date_scheduling** - Timeline, milestones, deadlines
23. **capacity_attendance** - Expected numbers, space planning

### Contingency & Quality
24. **weather_contingency** - Outdoor planning, backup plans
25. **registration_ticketing** - Admission, pricing, access control
26. **accessibility_accommodation** - Inclusive design, special needs
27. **vendor_management** - Supplier coordination, contracts
28. **quality_control** - Standards, inspection, compliance
29. **post_event_analysis** - Review, feedback, lessons learned
30. **emergency_procedures** - Crisis response, safety protocols
31. **miscellaneous** - Uncategorized planning items

## 🔧 Migration & Schema Evolution

### Database Migrations
The system includes migration scripts for schema evolution:

```bash
# Apply conversation temporal fields
python apply_conversation_temporal_migration.py

# Apply planning item lifecycle tracking  
python apply_lifecycle_migration.py

# Check migration status
python check_database.py
```

### Migration Files
- `migrations/add_conversation_temporal_fields.sql` - Conversation chronology
- `migrations/add_lifecycle_tracking_fields.sql` - Item lifecycle
- `migrations/setup_pgvector.sql` - Vector search capabilities

## 🎯 Usage Examples

### Complete Extraction Pipeline
```python
# Run full extraction with approval
from complete_extraction_pipeline import main as run_pipeline
await run_pipeline()
```

### Interactive Approval
```python
from approval_interface import ApprovalInterface

interface = ApprovalInterface()
await interface.initialize()

# Review latest extraction session
session_id = 123
results = await interface.run_approval_session(session_id)
print(f"Approved {results['approved_count']} items")
```

### Temporal Superseding
```python
from temporal_superseding_service import TemporalSupersedingService

service = TemporalSupersedingService()
await service.initialize()

# Find items superseded by newer session
candidates = await service.find_superseding_candidates(
    newer_session_id=456,
    similarity_threshold=0.7
)
```

### Vector Similarity Search
```python
from embedding_service import EmbeddingService

service = EmbeddingService()
await service.initialize()

# Find relevant chunks for category
chunks = await service.find_relevant_chunks_for_category(
    category_id=4,  # food_catering
    source_id=2,
    threshold=0.4
)
```

## 🔍 API Endpoints

### Enhanced Planning Items API
```bash
# Get items with temporal information
GET /planning-items?include_lifecycle=true

# Get superseding relationships
GET /planning-items/{id}/superseding-info

# Get conversation timeline
GET /conversations/timeline

# Trigger superseding analysis
POST /planning-items/analyze-superseding
```

### Extraction Management
```bash
# List extraction sessions
GET /extraction-sessions

# Get session results with deduplication
GET /extraction-sessions/{id}/results?include_duplicates=true

# Approve/reject extraction results
POST /extraction-sessions/{id}/approve
```

## 🚀 Performance & Scale

### Vector Search Optimization
- **pgvector indexes** on embedding columns for fast similarity search
- **Chunked processing** to handle large transcripts efficiently
- **Configurable thresholds** for relevance filtering
- **Batch embedding generation** for improved throughput

### Memory Management
- **Streaming processing** for large transcript files
- **Connection pooling** for database efficiency
- **Async operations** throughout the pipeline
- **Configurable chunk sizes** based on available memory

## 🛠️ Development & Debugging

### Debug Scripts
```bash
# Check database health
python check_database.py

# Debug vector similarity calculations
python debug_similarity.py

# Test temporal superseding logic
python test_temporal_superseding.py

# Debug extraction pipeline
python debug_superseding_query.py
```

### Development Environment
```bash
# Start development PostgreSQL
docker run -d --name kk6-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 55432:5432 \
  ankane/pgvector

# Start Ollama service
ollama serve

# Run in development mode
python -m uvicorn kk6_planning_api:app --reload --port 8090
```

## 📈 Current System Status

As of the latest extraction runs:
- **Vector embeddings**: 768-dimensional Nomic embeddings for semantic search
- **Temporal tracking**: Conversation chronology and item lifecycle history
- **Professional prompts**: 31 category-specific domain expert personas
- **Interactive approval**: Rich terminal UI with deduplication detection
- **Schema evolution**: Multiple migrations applied for advanced features
- **Production ready**: Full error handling, logging, and monitoring

## 🔮 Architecture Philosophy

This system represents a evolution from simple LLM extraction to a sophisticated, temporally-aware planning intelligence system:

1. **Semantic Understanding** - Vector embeddings enable true comprehension
2. **Professional Expertise** - Category-specific prompts leverage domain knowledge  
3. **Temporal Intelligence** - Cross-conversation evolution and superseding
4. **Human-AI Collaboration** - Interactive approval with AI assistance
5. **Data Integrity** - Complete audit trails and migration capabilities

The KK6 Planning Database demonstrates how AI-powered extraction can evolve beyond simple text processing into intelligent, context-aware planning assistance.

---

**System Requirements**: PostgreSQL 12+ with pgvector, Ollama with nomic-embed-text, OpenRouter API access, Python 3.9+

**Key Dependencies**: `asyncpg`, `fastapi`, `httpx`, `numpy`, `pydantic`, `rich`, `pgvector`

**API Documentation**: Available at `/docs` when running the FastAPI server

**Web Interface**: Available at `/web` for interactive data management