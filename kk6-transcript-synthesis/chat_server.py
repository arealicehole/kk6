#!/usr/bin/env python3
"""FastAPI chat server for KK6 transcript database."""

import asyncio
import ast
import json
import logging
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.kk6_transcript_synthesis.api.embeddings import OllamaEmbeddingClient
from src.kk6_transcript_synthesis.api.factory import get_api_client
from src.kk6_transcript_synthesis.database import DatabaseManager, TranscriptRepository, TranscriptRecord
from src.kk6_transcript_synthesis.utils import get_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KK6 Transcript Chat",
    description="Chat interface for Gilbert transcript database",
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

# Global variables for database and clients
db_manager: Optional[DatabaseManager] = None
repository: Optional[TranscriptRepository] = None
embedding_client: Optional[OllamaEmbeddingClient] = None
llm_client = None
settings = None


# Pydantic models
class ChatMessage(BaseModel):
    content: str
    kickback_filter: bool = False
    max_results: int = 5


class TranscriptMatch(BaseModel):
    id: int
    filename: str
    content: str
    mentions_kickback: bool
    confidence_score: float
    similarity_score: float
    created_at: datetime


class ChatResponse(BaseModel):
    response: str
    matches: List[TranscriptMatch]
    query_embedding_generated: bool
    total_matches: int


@app.on_event("startup")
async def startup_event():
    """Initialize database and API clients on startup."""
    global db_manager, repository, embedding_client, llm_client, settings
    
    logger.info("Starting KK6 transcript chat server...")
    
    # Load settings
    settings = get_settings()
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.initialize()
    repository = TranscriptRepository(db_manager)
    
    # Initialize embedding client
    embedding_client = OllamaEmbeddingClient(
        host=settings.ollama_host,
        model="nomic-embed-text"
    )
    
    # Initialize LLM client
    llm_client = get_api_client()
    
    logger.info("KK6 transcript chat server initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global db_manager, embedding_client, llm_client
    
    if embedding_client:
        await embedding_client.close()
    if llm_client:
        await llm_client.close()
    if db_manager:
        await db_manager.close()
    
    logger.info("KK6 transcript chat server shutdown complete")


async def similarity_search(
    query_embedding: List[float],
    kickback_filter: bool = False,
    limit: int = 5
) -> List[tuple[TranscriptRecord, float]]:
    """Perform vector similarity search on transcript database.
    
    Args:
        query_embedding: Vector embedding of the search query
        kickback_filter: If True, only return transcripts that mention kickback
        limit: Maximum number of results to return
        
    Returns:
        List of (transcript, similarity_score) tuples
    """
    # Build SQL query with vector similarity search (NO ORDER BY due to PostgreSQL issue)
    kickback_condition = "AND mentions_kickback = true" if kickback_filter else ""
    
    query = f"""
        SELECT 
            id, filename, content, mentions_kickback, confidence_score, 
            analysis_notes, embedding, metadata, created_at, updated_at,
            embedding <=> $1 AS distance,
            1 - (embedding <=> $1) AS similarity_score
        FROM transcripts 
        WHERE embedding IS NOT NULL {kickback_condition}
    """
    
    # Convert embedding to PostgreSQL vector format (no spaces after commas)
    embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
    logger.info(f"Searching with embedding format: {embedding_str[:50]}...")
    logger.info(f"Kickback filter: {kickback_filter}, Limit: {limit}")
    
    # Get all results (PostgreSQL ORDER BY with vector params fails)
    all_results = await db_manager.fetch_all(query, embedding_str)
    logger.info(f"Found {len(all_results)} total results")
    
    # Sort by distance in Python and apply limit
    sorted_results = sorted(all_results, key=lambda x: x['distance'])[:limit]
    logger.info(f"Returning top {len(sorted_results)} results after sorting")
    
    transcript_matches = []
    for row in sorted_results:
        # Parse embedding and metadata from string format
        
        # Parse embedding (comes as string representation of list)
        embedding_str = row["embedding"]
        if isinstance(embedding_str, str):
            # Convert string representation back to list
            embedding = ast.literal_eval(embedding_str) if embedding_str else []
        else:
            embedding = embedding_str
            
        # Parse metadata (comes as JSON string)
        metadata_str = row["metadata"]
        if isinstance(metadata_str, str):
            metadata = json.loads(metadata_str) if metadata_str else {}
        else:
            metadata = metadata_str
        
        transcript = TranscriptRecord(
            id=row["id"],
            filename=row["filename"],
            content=row["content"],
            mentions_kickback=row["mentions_kickback"],
            confidence_score=row["confidence_score"],
            analysis_notes=row["analysis_notes"],
            embedding=embedding,
            metadata=metadata,
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        similarity_score = float(row["similarity_score"])
        transcript_matches.append((transcript, similarity_score))
    
    return transcript_matches


async def generate_chat_response(
    user_query: str,
    matches: List[tuple[TranscriptRecord, float]]
) -> str:
    """Generate a chat response based on the user query and transcript matches."""
    if not matches:
        return "I couldn't find any relevant transcripts for your query. Try rephrasing your question or check if the Kanna Kickback filter is too restrictive."
    
    # Build context from top matches
    context_parts = []
    for i, (transcript, score) in enumerate(matches[:3], 1):
        context_parts.append(
            f"Transcript {i} (from {transcript.filename}, similarity: {score:.3f}):\n"
            f"{transcript.content[:500]}{'...' if len(transcript.content) > 500 else ''}\n"
        )
    
    context = "\n".join(context_parts)
    
    # Create prompt for LLM
    prompt = f"""You are a helpful assistant that answers questions about Gilbert's phone transcripts. 
Based on the following transcript excerpts, please answer the user's question clearly and concisely.

User Question: {user_query}

Relevant Transcript Excerpts:
{context}

Instructions:
- Answer the question based on the transcript content
- Be specific and reference which transcript contains the information
- If the transcripts don't contain enough information to answer fully, say so
- Keep your response conversational and helpful
- Mention if any transcripts reference the Kanna Kickback event

Answer:"""
    
    try:
        # Generate response using LLM
        analysis = await llm_client.analyze_transcript(prompt)
        return analysis.explanation
    except Exception as e:
        logger.error(f"Error generating LLM response: {e}")
        return f"I found {len(matches)} relevant transcripts, but encountered an error generating a detailed response. You can review the transcript matches below."


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Handle chat messages and return response with relevant transcripts."""
    try:
        # Generate embedding for user query
        query_embedding = await embedding_client.generate_embedding(message.content)
        
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Perform similarity search
        matches = await similarity_search(
            query_embedding=query_embedding,
            kickback_filter=message.kickback_filter,
            limit=message.max_results
        )
        
        # Generate chat response
        response_text = await generate_chat_response(message.content, matches)
        
        # Convert matches to response format
        transcript_matches = [
            TranscriptMatch(
                id=transcript.id,
                filename=transcript.filename,
                content=transcript.content,
                mentions_kickback=transcript.mentions_kickback,
                confidence_score=transcript.confidence_score,
                similarity_score=similarity_score,
                created_at=transcript.created_at
            )
            for transcript, similarity_score in matches
        ]
        
        return ChatResponse(
            response=response_text,
            matches=transcript_matches,
            query_embedding_generated=True,
            total_matches=len(matches)
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    total_transcripts = await repository.count_transcripts()
    
    # Count transcripts with embeddings
    query = "SELECT COUNT(*) as count FROM transcripts WHERE embedding IS NOT NULL"
    result = await db_manager.fetch_one(query)
    embedded_count = result["count"] if result else 0
    
    # Count kickback mentions
    kickback_query = "SELECT COUNT(*) as count FROM transcripts WHERE mentions_kickback = true"
    kickback_result = await db_manager.fetch_one(kickback_query)
    kickback_count = kickback_result["count"] if kickback_result else 0
    
    return {
        "total_transcripts": total_transcripts,
        "embedded_transcripts": embedded_count,
        "kickback_mentions": kickback_count,
        "embedding_coverage": f"{(embedded_count/total_transcripts*100):.1f}%" if total_transcripts > 0 else "0%"
    }


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the chat interface HTML."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KK6 Transcript Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 1200px;
            height: 90vh;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .controls {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .filter-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .filter-toggle input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: #667eea;
        }
        
        .filter-toggle label {
            font-weight: 500;
            color: #495057;
            cursor: pointer;
        }
        
        .stats {
            margin-left: auto;
            font-size: 12px;
            color: #6c757d;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafbfc;
        }
        
        .message {
            margin-bottom: 20px;
            max-width: 85%;
        }
        
        .message.user {
            margin-left: auto;
        }
        
        .message.bot {
            margin-right: auto;
        }
        
        .message-bubble {
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        
        .message.user .message-bubble {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 6px;
        }
        
        .message.bot .message-bubble {
            background: white;
            color: #333;
            border: 1px solid #e9ecef;
            border-bottom-left-radius: 6px;
        }
        
        .transcript-matches {
            margin-top: 15px;
        }
        
        .transcript-match {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            font-size: 13px;
        }
        
        .transcript-header {
            font-weight: 600;
            color: #495057;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .transcript-content {
            color: #6c757d;
            line-height: 1.3;
            max-height: 100px;
            overflow: hidden;
            position: relative;
        }
        
        .similarity-score {
            font-size: 11px;
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 6px;
            border-radius: 4px;
        }
        
        .kickback-badge {
            font-size: 11px;
            background: #fff3cd;
            color: #856404;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #ffeaa7;
        }
        
        .chat-input-container {
            background: white;
            border-top: 1px solid #e9ecef;
            padding: 20px;
        }
        
        .chat-input-form {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .send-button:hover:not(:disabled) {
            background: #5a6fd8;
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #6c757d;
            font-style: italic;
        }
        
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid #e9ecef;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .chat-container {
                width: 95%;
                height: 95vh;
            }
            
            .controls {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .stats {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🎤 KK6 Transcript Chat</h1>
            <p>Chat with Gilbert's phone transcripts - Ask questions about conversations and events</p>
        </div>
        
        <div class="controls">
            <div class="filter-toggle">
                <input type="checkbox" id="kickbackFilter">
                <label for="kickbackFilter">🎉 Kanna Kickback Only</label>
            </div>
            <div class="stats" id="stats">Loading stats...</div>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-bubble">
                    👋 Hi! I can help you search through Gilbert's phone transcripts. Ask me anything about his conversations, events, or specific topics. Use the "Kanna Kickback Only" filter to focus on party-related discussions.
                </div>
            </div>
        </div>
        
        <div class="chat-input-container">
            <form class="chat-input-form" id="chatForm">
                <input 
                    type="text" 
                    class="chat-input" 
                    id="chatInput" 
                    placeholder="Ask about Gilbert's transcripts..."
                    required
                >
                <button type="submit" class="send-button" id="sendButton">Send</button>
            </form>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const chatForm = document.getElementById('chatForm');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const kickbackFilter = document.getElementById('kickbackFilter');
        const stats = document.getElementById('stats');
        
        // Load stats on page load
        loadStats();
        
        async function loadStats() {
            try {
                const response = await fetch('/stats');
                const data = await response.json();
                stats.textContent = `${data.total_transcripts} transcripts, ${data.kickback_mentions} mention Kanna Kickback`;
            } catch (error) {
                stats.textContent = 'Stats unavailable';
            }
        }
        
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            chatInput.value = '';
            
            // Show loading
            const loadingMsg = addMessage('', 'bot', true);
            sendButton.disabled = true;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: message,
                        kickback_filter: kickbackFilter.checked,
                        max_results: 5
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                // Remove loading message
                loadingMsg.remove();
                
                // Add bot response
                addBotResponse(data);
                
            } catch (error) {
                loadingMsg.remove();
                addMessage('Sorry, I encountered an error processing your request. Please try again.', 'bot');
                console.error('Chat error:', error);
            } finally {
                sendButton.disabled = false;
                chatInput.focus();
            }
        });
        
        function addMessage(content, sender, isLoading = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            if (isLoading) {
                messageDiv.innerHTML = `
                    <div class="message-bubble">
                        <div class="loading">
                            <div class="spinner"></div>
                            Searching transcripts...
                        </div>
                    </div>
                `;
            } else {
                messageDiv.innerHTML = `<div class="message-bubble">${escapeHtml(content)}</div>`;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return messageDiv;
        }
        
        function addBotResponse(data) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            let matchesHtml = '';
            if (data.matches && data.matches.length > 0) {
                matchesHtml = '<div class="transcript-matches">';
                data.matches.forEach((match, index) => {
                    const truncatedContent = match.content.length > 200 
                        ? match.content.substring(0, 200) + '...' 
                        : match.content;
                    
                    const badges = [];
                    if (match.mentions_kickback) {
                        badges.push('<span class="kickback-badge">🎉 Kanna Kickback</span>');
                    }
                    badges.push(`<span class="similarity-score">${(match.similarity_score * 100).toFixed(1)}% match</span>`);
                    
                    matchesHtml += `
                        <div class="transcript-match">
                            <div class="transcript-header">
                                <span>${match.filename}</span>
                                <div>${badges.join(' ')}</div>
                            </div>
                            <div class="transcript-content">${escapeHtml(truncatedContent)}</div>
                        </div>
                    `;
                });
                matchesHtml += '</div>';
            }
            
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    ${escapeHtml(data.response)}
                    ${matchesHtml}
                </div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Focus input on page load
        chatInput.focus();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run(
        "chat_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )