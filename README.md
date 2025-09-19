# KK6 - Kanna Kickback 6 Complete Planning System

🎉 **Complete visual pipeline management system** for Kanna Kickback 6 charity event planning with advanced AI-powered transcript processing and interactive approval workflows.

## 🚀 System Overview

The KK6 system is a **comprehensive event planning intelligence platform** that transforms raw conversation transcripts into organized, actionable planning data through an advanced extraction pipeline with full visual management interface.

## ✨ Major Features Implemented

### 🖥️ **Visual Pipeline Management Interface**
- **Drag-and-Drop Upload**: Modern web UI (`localhost:8091`) with real-time file upload progress
- **Live Pipeline Status**: WebSocket-based real-time updates during transcript processing  
- **Interactive Approval Workflow**: Inline approve/edit/decline interface with category organization
- **Session Management**: Track multiple processing sessions with persistence across restarts
- **Visual Progress Indicators**: Real-time chunk processing and extraction progress display

### 🧠 **Advanced AI Extraction Pipeline**
- **Vector Embeddings**: Ollama nomic-embed-text for semantic chunk similarity (768-dimensional)
- **Category-Specific Prompts**: 31 professional domain expert prompts for specialized extraction
- **Iterative Processing**: Category-by-category extraction from ALL relevant chunks (unlimited)
- **OpenRouter Integration**: Structured JSON outputs with sonoma-sky-alpha model
- **LLM-Powered Deduplication**: Intelligent detection and merging of similar planning items
- **Confidence Scoring**: AI confidence levels with manual override capabilities

### ⏰ **Temporal Tracking & Evolution**
- **Conversation Chronology**: Parse timestamps from filenames, track conversation sequences
- **Item Lifecycle**: Track when items first mentioned, last updated, status changes over time
- **Temporal Superseding**: Automatically link newer items that supersede older planning decisions
- **Cross-Conversation Evolution**: Track planning evolution across multiple conversation sessions

### 🎛️ **Interactive Approval System**
- **Rich Web Interface**: Modern approval interface with category-based organization
- **Edit-in-Place**: Modify extracted content, confidence scores, and tags before approval
- **Batch Operations**: Efficiently approve, edit, decline, or skip multiple items
- **Duplicate Detection**: Visual highlighting and merging suggestions for similar items
- **Real-time Updates**: Live status updates during approval workflow

## 🏗️ Project Structure

### 🎯 [kk6-planning-database/](./kk6-planning-database/)
**Complete Visual Pipeline Management System**
- **Visual Pipeline API** (`visual_pipeline_api.py`) - FastAPI server with WebSocket real-time updates
- **Advanced AI Extraction** (`iterative_extractor.py`) - Vector search with professional prompts  
- **Interactive Approval** - Web interface with inline editing and batch operations
- **Database with pgvector** - Vector similarity search and temporal tracking
- **31 Planning Categories** - Comprehensive event planning taxonomy
- **🔴 Status**: Production-ready with full visual interface

### 📝 [kk6-transcript-synthesis/](./kk6-transcript-synthesis/)
**Reusable Transcript Processing Tool**
- Vector database for semantic search
- Chat interface for querying transcripts
- Processes Gilbert's phone transcripts
- AI-powered analysis using OpenRouter/Ollama
- **Status**: 62 transcripts processed, 5 mention Kanna Kickback

## 🚀 Quick Start

### Visual Pipeline System (Primary Interface)
```bash
cd kk6-planning-database/
python visual_pipeline_api.py
# Access: http://localhost:8091 - Full visual interface
# Features: Drag-and-drop upload, real-time progress, inline approval
```

### Transcript Chat System
```bash
cd kk6-transcript-synthesis/
uv run python chat_server.py
# Access: http://localhost:8080 - Query historical transcripts
```

## 🎯 Complete Feature Set

### Visual Pipeline System
- ✅ **Drag-and-drop file uploads** with progress indicators
- ✅ **Real-time processing status** via WebSocket updates
- ✅ **31 professional AI extraction prompts** for comprehensive planning
- ✅ **Vector semantic search** with Ollama embeddings
- ✅ **Interactive approval workflow** with inline editing
- ✅ **Duplicate detection and merging** with LLM assistance
- ✅ **Temporal tracking** and superseding logic
- ✅ **Complete audit trails** and session persistence
- ✅ **Category-based organization** with confidence scoring
- ✅ **Batch approval operations** for efficiency

### Database & Architecture
- ✅ **PostgreSQL with pgvector** for semantic similarity search
- ✅ **31 hierarchical planning categories** with embeddings
- ✅ **Temporal schema** for conversation chronology and item lifecycle
- ✅ **Migration system** for schema evolution
- ✅ **Complete source tracking** and extraction session management

## 📊 Current System Status

### Production-Ready Features
- **Visual Interface**: Complete drag-and-drop pipeline at `localhost:8091`
- **AI Extraction**: Full vector search with professional domain prompts
- **Approval Workflow**: Interactive web interface with real-time updates
- **Database**: Enhanced schema with temporal tracking and vector search
- **Documentation**: Comprehensive README and API documentation
- **Testing**: Selenium automation for end-to-end validation

### Key Planning Data Extracted
- **200+ expected attendance** with venue capacity planning
- **Restaurant partnership** (10% revenue sharing agreement)
- **INSA partnership confirmed** for cannabis supply
- **Sushi chef requirement** by December deadline
- **Charity component** for Sojourner Center toy drive
- **Budget planning** with cost estimation and revenue projections

## 🏗️ Technical Architecture

```
sixback/ (KK6 Complete Planning System)
├── kk6-planning-database/                    # Visual Pipeline Management System
│   ├── visual_pipeline_api.py              # 🖥️ Main FastAPI server with WebSocket updates
│   ├── static/
│   │   ├── index.html                       # 🎯 Drag-and-drop upload interface
│   │   └── approval.html                    # ✅ Interactive approval workflow
│   ├── iterative_extractor.py               # 🧠 Advanced AI extraction engine
│   ├── category_prompts.py                  # 👨‍💼 31 professional domain expert prompts
│   ├── deduplication_service.py             # 🔄 LLM-powered duplicate detection
│   ├── embedding_service.py                 # 🔍 Vector embeddings with Ollama
│   ├── temporal_superseding_service.py      # ⏰ Cross-conversation evolution tracking
│   ├── approval_interface.py                # 🎛️ Interactive terminal approval system
│   ├── setup_enhanced_db.py                 # 🗄️ Database setup with pgvector
│   └── README.md                            # 📚 Comprehensive documentation
│
├── kk6-transcript-synthesis/                 # Transcript Chat System
│   ├── chat_server.py                       # 💬 Web chat interface
│   ├── add_embeddings.py                    # 🔍 Vector embedding system
│   ├── gilbert-transcripts/                 # 📁 Source transcript files
│   └── README.md                            # 📚 System documentation
│
├── CLAUDE.md                                # 🤖 AI development guidelines
├── .env                                     # 🔑 Environment configuration
└── README.md                               # 📖 This comprehensive overview
```

## 🛠️ Development Philosophy

### Production-Ready Design
- **Visual-First Interface**: Complete drag-and-drop pipeline management
- **Real-time Updates**: WebSocket communication for live progress tracking
- **Professional AI Prompts**: 31 domain expert personas for specialized extraction
- **Interactive Workflows**: Inline editing and batch approval operations
- **Robust Architecture**: Error handling, logging, and monitoring

### System Integration
- **Visual Pipeline** → Primary interface for transcript processing and approval
- **Chat System** → Query and analyze historical transcript data
- **Database** → Unified storage with temporal tracking and vector search
- **Clear Data Flow** → Raw transcripts → AI extraction → Interactive approval → Planning data

## 🔧 Dependencies & Requirements

### Core Infrastructure
- **PostgreSQL 12+** with pgvector extension (port 55432)
- **Ollama** with nomic-embed-text model for embeddings
- **OpenRouter API** for sonoma-sky-alpha LLM
- **Python 3.9+** with FastAPI, asyncpg, httpx, pydantic

### Key Libraries
- **pgvector**: Vector similarity search
- **FastAPI**: Web API with WebSocket support
- **Rich**: Beautiful terminal interfaces
- **asyncpg**: Async PostgreSQL driver
- **httpx**: Async HTTP client

## 🌟 Achievements & Innovation

### Technical Innovations
- ✅ **Real-time visual pipeline** with drag-and-drop upload
- ✅ **Professional AI extraction** using domain expert prompts  
- ✅ **Vector semantic search** for unlimited chunk processing
- ✅ **Interactive approval workflow** with inline editing
- ✅ **Temporal evolution tracking** across conversations
- ✅ **LLM-powered deduplication** with merge suggestions
- ✅ **Session persistence** and complete audit trails

### Event Planning Coverage
- ✅ **31 comprehensive categories** covering all event aspects
- ✅ **Charity component integration** (Sojourner Center toy drive)
- ✅ **Vendor relationships** (restaurant partnerships, INSA)
- ✅ **Budget and attendance planning** (200+ expected)
- ✅ **Timeline and logistics** with confidence scoring

## 🚀 Future Enhancements

### Planned Features
- **Mobile-responsive interface** for on-the-go planning
- **Email integration** for automatic source detection
- **Screenshot/image processing** capabilities
- **Advanced analytics** and reporting dashboards
- **Integration with external planning tools** (calendars, payment systems)
- **Automated deadline tracking** and notifications
- **Multi-event support** for Kanna Kickback series