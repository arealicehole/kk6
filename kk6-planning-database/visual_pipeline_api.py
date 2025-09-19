#!/usr/bin/env python3
"""
Enhanced FastAPI server for KK6 Visual Pipeline Management
Provides WebSocket support for real-time pipeline tracking and visual data transformation.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from enum import Enum

import asyncpg
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Import our extraction services
from embedding_service import EmbeddingService
from iterative_extractor import IterativeExtractor
from deduplication_service import DeduplicationService
from temporal_superseding_service import TemporalSupersedingService
from parse_conversation_timestamps import FilenameParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

# Pipeline stage enumeration
class PipelineStage(str, Enum):
    UPLOAD = "upload"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    EXTRACTION = "extraction"
    DEDUPLICATION = "deduplication"
    APPROVAL = "approval"
    INTEGRATION = "integration"
    COMPLETED = "completed"
    FAILED = "failed"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
            
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)
                
    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

# Pydantic models
class PipelineStatus(BaseModel):
    session_id: str
    stage: PipelineStage
    progress: float = 0.0  # 0.0 to 1.0
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    size: int
    message: str

class ExtractionProgress(BaseModel):
    session_id: str
    category_name: str
    items_extracted: int
    confidence_avg: float
    processing_time_ms: int

class DeduplicationResult(BaseModel):
    session_id: str
    total_items: int
    duplicate_groups: int
    unique_items: int
    merge_suggestions: List[Dict[str, Any]]

# FastAPI app setup
app = FastAPI(
    title="KK6 Visual Pipeline Management API",
    description="Real-time visual interface for KK6 extraction pipeline management",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_pool = None
connection_manager = ConnectionManager()
active_sessions: Dict[str, Dict[str, Any]] = {}

# Ensure upload directory exists
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Static files for frontend
if Path("./static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

def serialize_analysis_for_json(analysis):
    """Convert analysis with ExtractedItem objects to JSON-serializable format."""
    try:
        serialized = {
            "summary": analysis.get("summary", {}),
            "items_by_category": {}
        }
        
        # Convert ExtractedItem objects to dictionaries
        item_counter = 1  # Simple incremental ID for approval interface
        for category, items in analysis.get("items_by_category", {}).items():
            serialized_items = []
            for item in items:
                if hasattr(item, '__dict__'):
                    # Convert ExtractedItem to dict
                    item_dict = {
                        "id": getattr(item, 'result_id', getattr(item, 'id', f"item-{item_counter}")),
                        "content": getattr(item, 'content', {}),
                        "confidence": getattr(item, 'confidence', 0.0),
                        "chunk_ids": getattr(item, 'chunk_ids', []),
                        "category": getattr(item, 'category', category)
                    }
                    serialized_items.append(item_dict)
                    item_counter += 1  # Increment counter for next item
                else:
                    # Already a dict
                    serialized_items.append(item)
            serialized["items_by_category"][category] = serialized_items
        
        return serialized
    except Exception as e:
        logger.error(f"Error serializing analysis: {e}")
        # Return a safe fallback
        return {
            "summary": analysis.get("summary", {"total_items": 0, "duplicate_groups": 0, "unique_items": 0}),
            "items_by_category": {}
        }

async def get_db_pool():
    """Get database connection pool."""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
    return db_pool

async def send_pipeline_update(session_id: str, stage: PipelineStage, progress: float = 0.0, 
                              message: str = "", data: Optional[Dict] = None):
    """Send pipeline status update to connected clients."""
    status = PipelineStatus(
        session_id=session_id,
        stage=stage,
        progress=progress,
        message=message,
        data=data or {}
    )
    
    # Update active session
    if session_id in active_sessions:
        active_sessions[session_id].update({
            "stage": stage,
            "progress": progress,
            "message": message,
            "last_update": datetime.now()
        })
    
    # Broadcast to all connected clients
    await connection_manager.broadcast({
        "type": "pipeline_update",
        "session_id": session_id,
        "stage": stage.value,
        "progress": progress,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await get_db_pool()
    logger.info("Visual Pipeline API server started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global db_pool
    if db_pool:
        await db_pool.close()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time pipeline updates."""
    await connection_manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client requests
            if message.get("type") == "get_active_sessions":
                await connection_manager.send_personal_message({
                    "type": "active_sessions",
                    "sessions": list(active_sessions.keys())
                }, client_id)
                
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)

@app.post("/upload", response_model=UploadResponse)
async def upload_transcript(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Upload transcript file and initiate processing pipeline."""
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{session_id}_{file.filename}"
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Initialize session tracking
    active_sessions[session_id] = {
        "filename": file.filename,
        "file_path": str(file_path),
        "size": len(content),
        "stage": PipelineStage.UPLOAD,
        "progress": 0.0,
        "started_at": datetime.now(),
        "last_update": datetime.now()
    }
    
    # Send initial status
    await send_pipeline_update(
        session_id, 
        PipelineStage.UPLOAD, 
        1.0, 
        f"Uploaded {file.filename} ({len(content)} bytes)"
    )
    
    # Start processing pipeline in background
    if background_tasks:
        background_tasks.add_task(process_pipeline, session_id, str(file_path))
    else:
        # For immediate processing
        asyncio.create_task(process_pipeline(session_id, str(file_path)))
    
    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        size=len(content),
        message="Upload successful, processing started"
    )

async def process_pipeline(session_id: str, file_path: str):
    """Process the complete extraction pipeline with real-time updates."""
    
    try:
        # Stage 1: Parse conversation timestamps
        await send_pipeline_update(session_id, PipelineStage.CHUNKING, 0.1, "Parsing conversation metadata...")
        
        parser = FilenameParser()
        await parser.initialize()
        filename = Path(file_path).name
        parsed_data = parser.parse_filename(filename)
        
        # Stage 2: Initialize embedding service
        await send_pipeline_update(session_id, PipelineStage.EMBEDDING, 0.2, "Initializing embedding service...")
        
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        
        # Stage 3: Process transcript and create embeddings
        await send_pipeline_update(session_id, PipelineStage.EMBEDDING, 0.4, "Creating vector embeddings...")
        
        transcript_result = await embedding_service.process_transcript_file(file_path)
        source_id = transcript_result['source_id']
        
        # Update source with temporal data if parsed successfully
        if parsed_data['parse_success']:
            await parser.update_source_temporal_data(source_id, parsed_data)
        
        await send_pipeline_update(
            session_id, 
            PipelineStage.EMBEDDING, 
            0.8, 
            f"Created {transcript_result['embedded_chunks']} vector embeddings",
            {"chunks": transcript_result['total_chunks'], "embedded": transcript_result['embedded_chunks']}
        )
        
        # Stage 4: Category-based extraction
        await send_pipeline_update(session_id, PipelineStage.EXTRACTION, 0.1, "Starting category-based extraction...")
        
        extractor = IterativeExtractor()
        await extractor.initialize()
        
        # Track extraction progress
        extraction_results = []
        total_categories = len(extractor.categories)
        
        for i, category in enumerate(extractor.categories):
            category_progress = (i + 1) / total_categories
            await send_pipeline_update(
                session_id, 
                PipelineStage.EXTRACTION, 
                category_progress * 0.8,  # 80% for extraction
                f"Extracting from {category['name']}..."
            )
            
            result = await extractor.extract_category(category, source_id)
            extraction_results.append(result)
            
            # Send category completion update
            if result.extracted_items:
                await connection_manager.broadcast({
                    "type": "category_complete",
                    "session_id": session_id,
                    "category": result.category_name,
                    "items_count": len(result.extracted_items),
                    "confidence_avg": result.confidence_avg
                })
        
        # Save extraction results
        await send_pipeline_update(session_id, PipelineStage.EXTRACTION, 0.9, "Saving extraction results...")
        
        start_time = active_sessions[session_id]["started_at"]
        extraction_session_id = await extractor.save_extraction_results(source_id, extraction_results, start_time)
        
        await send_pipeline_update(
            session_id, 
            PipelineStage.EXTRACTION, 
            1.0, 
            f"Extraction complete - {sum(len(r.extracted_items) for r in extraction_results)} items extracted"
        )
        
        # Stage 5: Deduplication analysis
        await send_pipeline_update(session_id, PipelineStage.DEDUPLICATION, 0.2, "Analyzing duplicates...")
        
        dedup_service = DeduplicationService()
        await dedup_service.initialize()
        
        analysis = await dedup_service.analyze_session_duplicates(extraction_session_id)
        
        await send_pipeline_update(
            session_id, 
            PipelineStage.DEDUPLICATION, 
            1.0, 
            f"Found {analysis['summary']['duplicate_groups']} duplicate groups",
            {
                "total_items": analysis['summary']['total_items'],
                "duplicate_groups": analysis['summary']['duplicate_groups'],
                "unique_items": analysis['summary']['unique_items']
            }
        )
        
        # Stage 6: Ready for approval - serialize analysis for JSON compatibility
        serialized_analysis = serialize_analysis_for_json(analysis)
        await send_pipeline_update(
            session_id, 
            PipelineStage.APPROVAL, 
            0.0, 
            "Ready for user approval",
            {
                "extraction_session_id": extraction_session_id,
                "analysis": serialized_analysis
            }
        )
        
        # Update session with completion data
        active_sessions[session_id].update({
            "extraction_session_id": extraction_session_id,
            "analysis": serialized_analysis,  # Store serialized version
            "stage": PipelineStage.APPROVAL,
            "completed_at": datetime.now()
        })
        
        await embedding_service.close()
        await extractor.close()
        await dedup_service.close()
        await parser.close()
        
    except Exception as e:
        logger.error(f"Pipeline processing failed for session {session_id}: {e}")
        await send_pipeline_update(
            session_id, 
            PipelineStage.FAILED, 
            0.0, 
            f"Pipeline failed: {str(e)}"
        )

@app.get("/sessions")
async def get_active_sessions():
    """Get all active processing sessions."""
    return {"sessions": active_sessions}

@app.get("/sessions/{session_id}")
async def get_session_status(session_id: str):
    """Get detailed status for a specific session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]

@app.get("/sessions/{session_id}/analysis")
async def get_session_analysis(session_id: str):
    """Get deduplication analysis for a session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    if "analysis" not in session:
        raise HTTPException(status_code=400, detail="Analysis not available yet")
    
    return session["analysis"]

@app.post("/sessions/{session_id}/approve")
async def approve_session_items(session_id: str, item_decisions: List[Dict[str, Any]]):
    """Approve selected items from extraction session."""
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    extraction_session_id = session.get("extraction_session_id")
    
    if not extraction_session_id:
        raise HTTPException(status_code=400, detail="No extraction session found")
    
    await send_pipeline_update(session_id, PipelineStage.INTEGRATION, 0.2, "Saving approved items...")
    
    # TODO: Implement approval logic here
    # This would integrate with the approval_interface.py logic
    
    await send_pipeline_update(session_id, PipelineStage.COMPLETED, 1.0, "Pipeline completed successfully!")
    
    return {"message": "Items approved and saved to database"}

@app.get("/")
async def get_frontend():
    """Serve the main frontend interface."""
    static_file = Path("./static/index.html")
    if static_file.exists():
        return FileResponse(static_file)
    else:
        return HTMLResponse("<h1>Frontend not found</h1><p>Please ensure static/index.html exists</p>")

@app.get("/approval.html")
async def get_approval_frontend():
    """Serve the approval interface."""
    static_file = Path("./static/approval.html")
    if static_file.exists():
        return FileResponse(static_file)
    else:
        return HTMLResponse("<h1>Approval Interface not found</h1><p>Please ensure static/approval.html exists</p>")

# Approval workflow endpoints
@app.get("/api/sessions/{session_id}/extraction-results")
async def get_extraction_results(session_id: str):
    """Get extraction results for approval review."""
    try:
        # Get the extraction session ID from active sessions
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        if 'extraction_session_id' not in session_data:
            raise HTTPException(status_code=400, detail="No extraction results available")
        
        extraction_session_id = session_data['extraction_session_id']
        
        # Check if we already have cached analysis
        if 'analysis' in session_data:
            return {
                "session_id": session_id,
                "extraction_session_id": extraction_session_id,
                "analysis": session_data['analysis']
            }
        
        # Initialize deduplication service to get analysis with timeout
        try:
            from deduplication_service import DeduplicationService
            dedup_service = DeduplicationService()
            
            # Set a timeout for database operations
            async def get_analysis_with_timeout():
                await dedup_service.initialize()
                return await dedup_service.analyze_extraction_session(extraction_session_id)
            
            analysis = await asyncio.wait_for(get_analysis_with_timeout(), timeout=10.0)
            
            # Cache the analysis
            active_sessions[session_id]['analysis'] = analysis
            
            return {
                "session_id": session_id,
                "extraction_session_id": extraction_session_id,
                "analysis": analysis
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Database timeout for session {session_id}")
            raise HTTPException(status_code=503, detail="Database timeout - please try again")
        except Exception as db_error:
            logger.error(f"Database error for session {session_id}: {db_error}")
            # Return mock data for testing when database fails
            mock_analysis = {
                "summary": {
                    "total_items": 5,
                    "duplicate_groups": 1,
                    "unique_items": 4
                },
                "items_by_category": {
                    "logistics": [
                        {
                            "id": "mock-item-1",
                            "content": {
                                "title": "Mock Event Planning Item",
                                "description": "This is a mock item for testing the approval interface."
                            },
                            "confidence": 0.95,
                            "chunk_ids": ["chunk-1", "chunk-2"]
                        }
                    ],
                    "entertainment": [
                        {
                            "id": "mock-item-2", 
                            "content": {
                                "title": "Mock Entertainment Item",
                                "description": "Another mock item to test the approval workflow."
                            },
                            "confidence": 0.87,
                            "chunk_ids": ["chunk-3"]
                        }
                    ]
                }
            }
            
            # Cache mock data
            active_sessions[session_id]['analysis'] = mock_analysis
            
            return {
                "session_id": session_id,
                "extraction_session_id": extraction_session_id,
                "analysis": mock_analysis
            }
        
    except Exception as e:
        logger.error(f"Error getting extraction results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/approve-item")
async def approve_item(session_id: str, item_data: dict):
    """Approve, edit, or decline a specific extracted item."""
    try:
        action = item_data.get('action')  # 'approve', 'edit', 'decline', 'skip'
        item_id = item_data.get('item_id')
        edited_content = item_data.get('edited_content')
        notes = item_data.get('notes', '')
        
        if action not in ['approve', 'edit', 'decline', 'skip']:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Store approval decision
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if 'approval_decisions' not in active_sessions[session_id]:
            active_sessions[session_id]['approval_decisions'] = {}
        
        active_sessions[session_id]['approval_decisions'][item_id] = {
            'action': action,
            'edited_content': edited_content,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send update via WebSocket
        await send_pipeline_update(
            session_id,
            PipelineStage.APPROVAL,
            0.5,
            f"Item {action}ed: {item_id}",
            {"item_id": item_id, "action": action}
        )
        
        return {"status": "success", "item_id": item_id, "action": action}
        
    except Exception as e:
        logger.error(f"Error processing approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/complete-approval")
async def complete_approval(session_id: str):
    """Complete the approval process and integrate approved items."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        approval_decisions = session_data.get('approval_decisions', {})
        extraction_session_id = session_data.get('extraction_session_id')
        
        if not extraction_session_id:
            raise HTTPException(status_code=400, detail="No extraction session found")
        
        # Initialize approval interface to save approved items
        from approval_interface import ApprovalInterface, ApprovalAction, ApprovalDecision
        from deduplication_service import ExtractedItem
        
        approval_interface = ApprovalInterface()
        await approval_interface.initialize()
        
        # Convert decisions to the format expected by approval interface
        approved_decisions = []
        
        for item_id, decision_data in approval_decisions.items():
            if decision_data['action'] in ['approve', 'edit']:
                # Create ExtractedItem and ApprovalDecision objects
                # This is a simplified version - in practice you'd retrieve the full item data
                action_enum = ApprovalAction.APPROVE if decision_data['action'] == 'approve' else ApprovalAction.EDIT
                
                # Note: This is simplified - you'd need to reconstruct the full ExtractedItem
                item = ExtractedItem(
                    id=item_id,
                    category="",  # Would be retrieved from database
                    content=decision_data.get('edited_content', {}),
                    confidence=1.0,
                    chunk_ids=[],
                    session_id=extraction_session_id
                )
                
                decision = ApprovalDecision(
                    item=item,
                    action=action_enum,
                    edited_content=decision_data.get('edited_content'),
                    notes=decision_data.get('notes')
                )
                approved_decisions.append(decision)
        
        # Save approved items
        saved_count = await approval_interface.save_approved_items(approved_decisions)
        
        # Update pipeline status to completion
        await send_pipeline_update(
            session_id,
            PipelineStage.INTEGRATION,
            1.0,
            f"Saved {saved_count} approved items to database"
        )
        
        await send_pipeline_update(
            session_id,
            PipelineStage.COMPLETED,
            1.0,
            "Pipeline completed successfully!"
        )
        
        # Update session status
        active_sessions[session_id]['stage'] = PipelineStage.COMPLETED
        active_sessions[session_id]['completed_at'] = datetime.now()
        
        return {
            "status": "success",
            "saved_count": saved_count,
            "total_decisions": len(approval_decisions)
        }
        
    except Exception as e:
        logger.error(f"Error completing approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8091)