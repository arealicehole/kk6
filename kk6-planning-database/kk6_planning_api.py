#!/usr/bin/env python3
"""FastAPI server for KK6 Planning Database management."""

import json
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any, Union

import asyncpg
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ConfigDict
from pydantic.json import pydantic_encoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings
DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

app = FastAPI(
    title="KK6 Planning API",
    description="API for managing Kanna Kickback 6 event planning information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database connection pool
db_pool = None

async def get_db_pool():
    """Get database connection pool."""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
    return db_pool

# Pydantic models
class CategoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SourceModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    type: str
    reference: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class ExtractionSessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    source_id: Optional[int] = None
    extraction_method: str
    extracted_by: str
    session_notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "in_progress"

class PlanningItemModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    category_id: int
    item_key: Optional[str] = None
    title: str
    content: Optional[str] = None
    value_text: Optional[str] = None
    value_numeric: Optional[Decimal] = None
    value_date: Optional[date] = None
    value_boolean: Optional[bool] = None
    value_json: Optional[Dict[str, Any]] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    priority_level: int = Field(3, ge=1, le=5)
    source_id: Optional[int] = None
    extraction_session_id: Optional[int] = None
    superseded_by: Optional[int] = None
    status: str = "active"
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PlanningItemCreate(BaseModel):
    category_id: int
    item_key: Optional[str] = None
    title: str
    content: Optional[str] = None
    value_text: Optional[str] = None
    value_numeric: Optional[Decimal] = None
    value_date: Optional[date] = None
    value_boolean: Optional[bool] = None
    value_json: Optional[Dict[str, Any]] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    priority_level: int = Field(3, ge=1, le=5)
    source_id: Optional[int] = None
    extraction_session_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool."""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool."""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")

# Custom JSON encoder for Decimal and other types
def custom_json_encoder(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return pydantic_encoder(obj)

# Root endpoint with basic info
@app.get("/")
async def root():
    """API information."""
    return {
        "title": "KK6 Planning API",
        "description": "API for managing Kanna Kickback 6 event planning information",
        "version": "1.0.0",
        "endpoints": {
            "categories": "/categories",
            "sources": "/sources", 
            "planning_items": "/planning-items",
            "extraction_sessions": "/extraction-sessions",
            "dashboard": "/dashboard"
        }
    }

# Categories endpoints
@app.get("/categories", response_model=List[CategoryModel])
async def get_categories(parent_id: Optional[int] = Query(None)):
    """Get all categories, optionally filtered by parent."""
    pool = await get_db_pool()
    
    if parent_id is not None:
        query = "SELECT * FROM categories WHERE parent_id = $1 ORDER BY sort_order"
        rows = await pool.fetch(query, parent_id)
    else:
        query = "SELECT * FROM categories ORDER BY sort_order"
        rows = await pool.fetch(query)
    
    return [CategoryModel(**dict(row)) for row in rows]

@app.post("/categories", response_model=CategoryModel)
async def create_category(category: CategoryModel):
    """Create a new category."""
    pool = await get_db_pool()
    
    query = """
        INSERT INTO categories (name, parent_id, description, sort_order)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """
    
    row = await pool.fetchrow(
        query, category.name, category.parent_id, 
        category.description, category.sort_order
    )
    
    return CategoryModel(**dict(row))

# Sources endpoints
@app.get("/sources", response_model=List[SourceModel])
async def get_sources(source_type: Optional[str] = Query(None)):
    """Get all sources, optionally filtered by type."""
    pool = await get_db_pool()
    
    if source_type:
        query = "SELECT * FROM sources WHERE type = $1 ORDER BY created_at DESC"
        rows = await pool.fetch(query, source_type)
    else:
        query = "SELECT * FROM sources ORDER BY created_at DESC"
        rows = await pool.fetch(query)
    
    return [SourceModel(**dict(row)) for row in rows]

@app.post("/sources", response_model=SourceModel)
async def create_source(source: SourceModel):
    """Create a new source."""
    pool = await get_db_pool()
    
    query = """
        INSERT INTO sources (type, reference, metadata)
        VALUES ($1, $2, $3)
        RETURNING *
    """
    
    row = await pool.fetchrow(
        query, source.type, source.reference, 
        json.dumps(source.metadata)
    )
    
    return SourceModel(**dict(row))

# Planning items endpoints
@app.get("/planning-items", response_model=List[PlanningItemModel])
async def get_planning_items(
    category_id: Optional[int] = Query(None),
    status: str = Query("active"),
    item_key: Optional[str] = Query(None)
):
    """Get planning items with optional filters."""
    pool = await get_db_pool()
    
    conditions = ["status = $1"]
    params = [status]
    param_count = 1
    
    if category_id:
        param_count += 1
        conditions.append(f"category_id = ${param_count}")
        params.append(category_id)
    
    if item_key:
        param_count += 1
        conditions.append(f"item_key = ${param_count}")
        params.append(item_key)
    
    query = f"""
        SELECT * FROM planning_items 
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
    """
    
    rows = await pool.fetch(query, *params)
    return [PlanningItemModel(**dict(row)) for row in rows]

@app.post("/planning-items", response_model=PlanningItemModel)
async def create_planning_item(item: PlanningItemCreate):
    """Create a new planning item."""
    pool = await get_db_pool()
    
    query = """
        INSERT INTO planning_items (
            category_id, item_key, title, content, value_text, value_numeric,
            value_date, value_boolean, value_json, confidence_level, priority_level,
            source_id, extraction_session_id, tags
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING *
    """
    
    row = await pool.fetchrow(
        query, item.category_id, item.item_key, item.title, item.content,
        item.value_text, item.value_numeric, item.value_date, item.value_boolean,
        json.dumps(item.value_json) if item.value_json else None,
        item.confidence_level, item.priority_level, item.source_id,
        item.extraction_session_id, item.tags
    )
    
    return PlanningItemModel(**dict(row))

@app.put("/planning-items/{item_id}", response_model=PlanningItemModel)
async def update_planning_item(item_id: int, item: PlanningItemCreate):
    """Update an existing planning item."""
    pool = await get_db_pool()
    
    query = """
        UPDATE planning_items SET
            category_id = $2, item_key = $3, title = $4, content = $5,
            value_text = $6, value_numeric = $7, value_date = $8, value_boolean = $9,
            value_json = $10, confidence_level = $11, priority_level = $12,
            source_id = $13, extraction_session_id = $14, tags = $15,
            updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    
    row = await pool.fetchrow(
        query, item_id, item.category_id, item.item_key, item.title, item.content,
        item.value_text, item.value_numeric, item.value_date, item.value_boolean,
        json.dumps(item.value_json) if item.value_json else None,
        item.confidence_level, item.priority_level, item.source_id,
        item.extraction_session_id, item.tags
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="Planning item not found")
    
    return PlanningItemModel(**dict(row))

@app.delete("/planning-items/{item_id}")
async def delete_planning_item(item_id: int):
    """Delete a planning item."""
    pool = await get_db_pool()
    
    query = "DELETE FROM planning_items WHERE id = $1"
    result = await pool.execute(query, item_id)
    
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Planning item not found")
    
    return {"message": "Planning item deleted successfully"}

@app.post("/planning-items/{old_item_id}/supersede/{new_item_id}")
async def supersede_planning_item(old_item_id: int, new_item_id: int):
    """Mark an item as superseded by another item."""
    pool = await get_db_pool()
    
    query = "SELECT supersede_planning_item($1, $2)"
    await pool.execute(query, old_item_id, new_item_id)
    
    return {"message": f"Item {old_item_id} superseded by item {new_item_id}"}

# Dashboard and summary endpoints
@app.get("/dashboard")
async def get_dashboard():
    """Get dashboard summary data."""
    pool = await get_db_pool()
    
    # Get planning summary
    summary_query = """
        SELECT 
            c.name as category,
            COUNT(pi.id) as total_items,
            COUNT(CASE WHEN pi.status = 'active' THEN 1 END) as active_items,
            COUNT(CASE WHEN pi.status = 'needs_verification' THEN 1 END) as needs_verification,
            ROUND(AVG(pi.confidence_level), 1) as avg_confidence
        FROM categories c
        LEFT JOIN planning_items pi ON c.id = pi.category_id
        WHERE c.parent_id IS NULL
        GROUP BY c.id, c.name, c.sort_order
        ORDER BY c.sort_order
    """
    
    summary_rows = await pool.fetch(summary_query)
    
    # Get recent items
    recent_query = """
        SELECT pi.*, c.name as category_name
        FROM planning_items pi
        JOIN categories c ON pi.category_id = c.id
        WHERE pi.status = 'active'
        ORDER BY pi.created_at DESC
        LIMIT 10
    """
    
    recent_rows = await pool.fetch(recent_query)
    
    # Get source statistics
    source_stats_query = """
        SELECT type, COUNT(*) as count
        FROM sources
        GROUP BY type
        ORDER BY count DESC
    """
    
    source_stats = await pool.fetch(source_stats_query)
    
    return {
        "summary": [dict(row) for row in summary_rows],
        "recent_items": [dict(row) for row in recent_rows],
        "source_statistics": [dict(row) for row in source_stats],
        "total_categories": len(summary_rows),
        "last_updated": datetime.now().isoformat()
    }

# Simple web interface
@app.get("/web", response_class=HTMLResponse)
async def get_web_interface():
    """Simple web interface for viewing planning data."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KK6 Planning Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .header { background-color: #4CAF50; color: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #f2f2f2; }
            .status-active { color: green; font-weight: bold; }
            .status-needs-verification { color: orange; font-weight: bold; }
            .confidence-high { color: green; }
            .confidence-medium { color: orange; }
            .confidence-low { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Kanna Kickback 6 Planning Dashboard</h1>
                <p>Event planning information management system</p>
            </div>
            
            <div class="card">
                <h2>Planning Categories Summary</h2>
                <div id="summary-table">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Recent Planning Items</h2>
                <div id="recent-items">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Source Statistics</h2>
                <div id="source-stats">Loading...</div>
            </div>
        </div>
        
        <script>
            async function loadDashboard() {
                try {
                    const response = await fetch('/dashboard');
                    const data = await response.json();
                    
                    // Render summary table
                    const summaryHtml = `
                        <table>
                            <tr>
                                <th>Category</th>
                                <th>Total Items</th>
                                <th>Active</th>
                                <th>Needs Verification</th>
                                <th>Avg Confidence</th>
                            </tr>
                            ${data.summary.map(row => `
                                <tr>
                                    <td>${row.category}</td>
                                    <td>${row.total_items}</td>
                                    <td class="status-active">${row.active_items}</td>
                                    <td class="status-needs-verification">${row.needs_verification}</td>
                                    <td class="${getConfidenceClass(row.avg_confidence)}">${row.avg_confidence || 'N/A'}</td>
                                </tr>
                            `).join('')}
                        </table>
                    `;
                    document.getElementById('summary-table').innerHTML = summaryHtml;
                    
                    // Render recent items
                    const recentHtml = `
                        <table>
                            <tr>
                                <th>Title</th>
                                <th>Category</th>
                                <th>Value</th>
                                <th>Confidence</th>
                                <th>Created</th>
                            </tr>
                            ${data.recent_items.map(item => `
                                <tr>
                                    <td>${item.title}</td>
                                    <td>${item.category_name}</td>
                                    <td>${item.value_text || item.value_numeric || item.value_date || 'N/A'}</td>
                                    <td class="${getConfidenceClass(item.confidence_level)}">${item.confidence_level || 'N/A'}</td>
                                    <td>${new Date(item.created_at).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </table>
                    `;
                    document.getElementById('recent-items').innerHTML = recentHtml;
                    
                    // Render source stats
                    const sourceHtml = `
                        <table>
                            <tr><th>Source Type</th><th>Count</th></tr>
                            ${data.source_statistics.map(stat => `
                                <tr><td>${stat.type}</td><td>${stat.count}</td></tr>
                            `).join('')}
                        </table>
                    `;
                    document.getElementById('source-stats').innerHTML = sourceHtml;
                    
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                    document.getElementById('summary-table').innerHTML = 'Error loading data';
                }
            }
            
            function getConfidenceClass(confidence) {
                if (!confidence) return '';
                if (confidence >= 8) return 'confidence-high';
                if (confidence >= 5) return 'confidence-medium';
                return 'confidence-low';
            }
            
            // Load dashboard on page load
            loadDashboard();
            
            // Refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)