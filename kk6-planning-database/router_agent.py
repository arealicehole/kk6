"""
Router Agent for KK6 Planning System

Intelligent query routing between semantic search (pgvector) and structured database queries.
Implements intent classification to optimize query handling based on user intent and data type.
"""

import asyncio
import asyncpg
import httpx
import json
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# Load environment configuration
def load_env_config():
    env_path = Path(__file__).parent / '.env'
    config = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value.strip('"').strip("'")
    return config

env_config = load_env_config()

# Configuration
DATABASE_URL = env_config.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kk6_planning')
OPENROUTER_API_KEY = env_config.get('OPENROUTER_API_KEY')
OPENROUTER_MODEL = env_config.get('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the router can handle."""
    SEMANTIC_SEARCH = "semantic_search"      # Best for: content similarity, concept search, fuzzy matching
    STRUCTURED_QUERY = "structured_query"   # Best for: specific data retrieval, filtering, aggregation
    HYBRID_ANALYSIS = "hybrid_analysis"     # Best for: complex analysis requiring both approaches
    DIRECT_EXTRACTION = "direct_extraction" # Best for: LLM-powered data extraction/transformation


class QueryIntent(Enum):
    """Intent classification for user queries."""
    SEARCH_CONTENT = "search_content"           # Find items by content similarity
    FILTER_DATA = "filter_data"                # Filter by specific criteria
    AGGREGATE_STATS = "aggregate_stats"        # Get counts, summaries, statistics
    FIND_DUPLICATES = "find_duplicates"        # Deduplication analysis
    EXTRACT_INSIGHTS = "extract_insights"      # LLM-powered analysis
    COMPARE_ITEMS = "compare_items"            # Compare specific items
    TEMPORAL_ANALYSIS = "temporal_analysis"    # Time-based queries


@dataclass
class RoutingDecision:
    """Represents a routing decision made by the Router Agent."""
    query_type: QueryType
    intent: QueryIntent
    confidence: float
    reasoning: str
    suggested_parameters: Dict[str, Any]
    fallback_strategy: Optional[QueryType] = None


@dataclass
class QueryContext:
    """Context information for a user query."""
    user_query: str
    session_id: Optional[str] = None
    category_filter: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None
    similarity_threshold: Optional[float] = None
    limit: int = 50


class RouterAgent:
    """
    Intelligent Router Agent for KK6 Planning System.
    
    Routes queries between:
    1. Semantic Search (pgvector + embeddings) - for content similarity
    2. Structured Queries (SQL) - for precise data retrieval  
    3. Hybrid Analysis - combining both approaches
    4. Direct LLM Extraction - for complex analysis
    """
    
    def __init__(self):
        self.db_pool = None
        self.intent_patterns = self._initialize_intent_patterns()
        
    async def initialize(self):
        """Initialize database connection and load optimization data."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        
        # Cache common query patterns for faster classification
        await self._load_query_optimization_data()
        
        logger.info("🧠 Router Agent initialized successfully")
        
    def _initialize_intent_patterns(self) -> Dict[QueryIntent, Dict[str, List[str]]]:
        """Define patterns for intent classification."""
        return {
            QueryIntent.SEARCH_CONTENT: {
                "keywords": ["find", "search", "similar", "like", "related", "about", "containing"],
                "patterns": ["what.*about", "find.*similar", "search.*for", "items.*like"]
            },
            QueryIntent.FILTER_DATA: {
                "keywords": ["filter", "where", "category", "status", "type", "from", "in"],
                "patterns": ["items.*where", "filter.*by", "from.*category", "status.*is"]
            },
            QueryIntent.AGGREGATE_STATS: {
                "keywords": ["count", "total", "how many", "statistics", "summary", "average"],
                "patterns": ["how many", "total.*items", "count.*of", "statistics.*for"]
            },
            QueryIntent.FIND_DUPLICATES: {
                "keywords": ["duplicate", "similar", "redundant", "overlapping", "merge"],
                "patterns": ["find.*duplicates", "similar.*items", "redundant.*entries"]
            },
            QueryIntent.EXTRACT_INSIGHTS: {
                "keywords": ["analyze", "insights", "patterns", "trends", "summarize", "explain"],
                "patterns": ["analyze.*items", "what.*patterns", "insights.*from", "summarize.*data"]
            },
            QueryIntent.COMPARE_ITEMS: {
                "keywords": ["compare", "difference", "versus", "vs", "between"],
                "patterns": ["compare.*items", "difference.*between", ".*vs.*", "item.*versus"]
            },
            QueryIntent.TEMPORAL_ANALYSIS: {
                "keywords": ["when", "time", "date", "recent", "old", "timeline", "history"],
                "patterns": ["when.*created", "recent.*items", "over.*time", "timeline.*of"]
            }
        }
        
    async def _load_query_optimization_data(self):
        """Load data to optimize routing decisions."""
        try:
            # Get database statistics for routing optimization
            stats_query = """
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(DISTINCT category_id) as categories,
                    COUNT(DISTINCT extraction_session_id) as sessions,
                    AVG(confidence_score) as avg_confidence
                FROM extraction_results 
                WHERE created_at > NOW() - INTERVAL '30 days'
            """
            
            stats = await self.db_pool.fetchrow(stats_query)
            self.db_stats = dict(stats) if stats else {}
            
            logger.info(f"📊 Loaded optimization data: {self.db_stats}")
            
        except Exception as e:
            logger.warning(f"Could not load optimization data: {e}")
            self.db_stats = {}
    
    async def classify_intent(self, query: str) -> QueryIntent:
        """Classify user intent using pattern matching and optional LLM fallback."""
        query_lower = query.lower()
        
        # Score each intent based on keyword and pattern matches
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            
            # Keyword matching
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    score += 1
                    
            # Pattern matching (simple contains check for now)
            for pattern in patterns["patterns"]:
                if any(word in query_lower for word in pattern.split(".*")):
                    score += 2
                    
            intent_scores[intent] = score
            
        # Return highest scoring intent, fallback to SEARCH_CONTENT
        if intent_scores:
            best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x])
            if intent_scores[best_intent] > 0:
                logger.info(f"🎯 Classified intent: {best_intent.value} (score: {intent_scores[best_intent]})")
                return best_intent
                
        # Fallback to LLM classification if patterns don't match
        return await self._llm_classify_intent(query)
    
    async def _llm_classify_intent(self, query: str) -> QueryIntent:
        """Use LLM for intent classification when pattern matching fails."""
        
        if not OPENROUTER_API_KEY:
            logger.warning("No LLM available, defaulting to SEARCH_CONTENT intent")
            return QueryIntent.SEARCH_CONTENT
            
        prompt = f"""Classify the intent of this KK6 event planning query:

Query: "{query}"

Available intents:
- SEARCH_CONTENT: Find items by content similarity or concepts
- FILTER_DATA: Filter items by specific criteria (category, status, etc.)
- AGGREGATE_STATS: Get counts, totals, or statistical summaries
- FIND_DUPLICATES: Find duplicate or similar items
- EXTRACT_INSIGHTS: Analyze patterns or extract insights
- COMPARE_ITEMS: Compare specific items or categories
- TEMPORAL_ANALYSIS: Time-based queries (recent, when, timeline)

Respond with only the intent name (e.g., "SEARCH_CONTENT")."""

        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                intent_str = result["choices"][0]["message"]["content"].strip()
                
                # Parse the intent
                for intent in QueryIntent:
                    if intent.value.upper() in intent_str.upper():
                        logger.info(f"🤖 LLM classified intent: {intent.value}")
                        return intent
                        
        except Exception as e:
            logger.warning(f"LLM intent classification failed: {e}")
            
        # Final fallback
        return QueryIntent.SEARCH_CONTENT
    
    async def route_query(self, context: QueryContext) -> RoutingDecision:
        """
        Main routing logic: determine optimal query strategy based on intent and context.
        """
        
        logger.info(f"🧭 Routing query: '{context.user_query}'")
        
        # Step 1: Classify intent
        intent = await self.classify_intent(context.user_query)
        
        # Step 2: Route based on intent and context
        decision = await self._determine_routing_strategy(intent, context)
        
        logger.info(f"✅ Routing decision: {decision.query_type.value} (confidence: {decision.confidence:.2f})")
        logger.info(f"💭 Reasoning: {decision.reasoning}")
        
        return decision
    
    async def _determine_routing_strategy(self, intent: QueryIntent, context: QueryContext) -> RoutingDecision:
        """Determine the optimal routing strategy based on intent and context."""
        
        query = context.user_query.lower()
        
        # Intent-based routing logic
        if intent == QueryIntent.SEARCH_CONTENT:
            # Semantic search is optimal for content similarity
            return RoutingDecision(
                query_type=QueryType.SEMANTIC_SEARCH,
                intent=intent,
                confidence=0.9,
                reasoning="Content search requires semantic similarity matching",
                suggested_parameters={
                    "embedding_search": True,
                    "similarity_threshold": context.similarity_threshold or 0.7,
                    "limit": context.limit
                },
                fallback_strategy=QueryType.STRUCTURED_QUERY
            )
            
        elif intent == QueryIntent.FILTER_DATA:
            # Structured queries optimal for filtering
            return RoutingDecision(
                query_type=QueryType.STRUCTURED_QUERY,
                intent=intent,
                confidence=0.85,
                reasoning="Data filtering requires precise SQL queries",
                suggested_parameters={
                    "use_sql": True,
                    "enable_filtering": True,
                    "category_filter": context.category_filter
                }
            )
            
        elif intent == QueryIntent.AGGREGATE_STATS:
            # SQL aggregation is fastest for statistics
            return RoutingDecision(
                query_type=QueryType.STRUCTURED_QUERY,
                intent=intent,
                confidence=0.95,
                reasoning="Statistical aggregation best handled by SQL",
                suggested_parameters={
                    "use_sql": True,
                    "enable_aggregation": True,
                    "group_by_category": True
                }
            )
            
        elif intent == QueryIntent.FIND_DUPLICATES:
            # Hybrid approach for duplicate detection
            return RoutingDecision(
                query_type=QueryType.HYBRID_ANALYSIS,
                intent=intent,
                confidence=0.8,
                reasoning="Duplicate detection requires both semantic similarity and structured analysis",
                suggested_parameters={
                    "semantic_similarity": True,
                    "structural_analysis": True,
                    "threshold_same_category": 0.4,
                    "threshold_cross_category": 0.7
                }
            )
            
        elif intent == QueryIntent.EXTRACT_INSIGHTS:
            # LLM extraction for complex analysis
            return RoutingDecision(
                query_type=QueryType.DIRECT_EXTRACTION,
                intent=intent,
                confidence=0.85,
                reasoning="Insight extraction requires LLM-powered analysis",
                suggested_parameters={
                    "use_llm": True,
                    "analysis_depth": "comprehensive",
                    "include_context": True
                }
            )
            
        elif intent == QueryIntent.COMPARE_ITEMS:
            # Hybrid approach for comparisons
            return RoutingDecision(
                query_type=QueryType.HYBRID_ANALYSIS,
                intent=intent,
                confidence=0.75,
                reasoning="Item comparison benefits from both semantic similarity and structured comparison",
                suggested_parameters={
                    "semantic_comparison": True,
                    "structured_comparison": True,
                    "side_by_side_analysis": True
                }
            )
            
        elif intent == QueryIntent.TEMPORAL_ANALYSIS:
            # Structured queries for time-based analysis
            return RoutingDecision(
                query_type=QueryType.STRUCTURED_QUERY,
                intent=intent,
                confidence=0.9,
                reasoning="Temporal analysis requires precise timestamp queries",
                suggested_parameters={
                    "use_sql": True,
                    "time_based_filtering": True,
                    "temporal_grouping": True,
                    "time_range": context.time_range
                }
            )
            
        # Fallback to semantic search
        return RoutingDecision(
            query_type=QueryType.SEMANTIC_SEARCH,
            intent=intent,
            confidence=0.5,
            reasoning="Fallback to semantic search for unclassified queries",
            suggested_parameters={"embedding_search": True}
        )
    
    async def execute_routed_query(self, context: QueryContext, decision: RoutingDecision) -> Dict[str, Any]:
        """Execute the query based on the routing decision."""
        
        logger.info(f"🚀 Executing {decision.query_type.value} query")
        
        try:
            if decision.query_type == QueryType.SEMANTIC_SEARCH:
                return await self._execute_semantic_search(context, decision)
                
            elif decision.query_type == QueryType.STRUCTURED_QUERY:
                return await self._execute_structured_query(context, decision)
                
            elif decision.query_type == QueryType.HYBRID_ANALYSIS:
                return await self._execute_hybrid_analysis(context, decision)
                
            elif decision.query_type == QueryType.DIRECT_EXTRACTION:
                return await self._execute_llm_extraction(context, decision)
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            
            # Try fallback strategy if available
            if decision.fallback_strategy:
                logger.info(f"🔄 Attempting fallback strategy: {decision.fallback_strategy.value}")
                fallback_decision = RoutingDecision(
                    query_type=decision.fallback_strategy,
                    intent=decision.intent,
                    confidence=0.3,
                    reasoning="Fallback strategy due to primary query failure",
                    suggested_parameters={}
                )
                return await self.execute_routed_query(context, fallback_decision)
            
            raise
    
    async def _execute_semantic_search(self, context: QueryContext, decision: RoutingDecision) -> Dict[str, Any]:
        """Execute semantic search using embeddings."""
        
        # This would integrate with the existing EmbeddingService
        # For now, return a placeholder that shows the routing worked
        
        params = decision.suggested_parameters
        similarity_threshold = params.get("similarity_threshold", 0.7)
        limit = params.get("limit", 50)
        
        # Placeholder query - in real implementation, this would use EmbeddingService
        query = """
            SELECT 
                er.id, er.raw_result, er.confidence_score,
                c.name as category_name,
                ts_rank(to_tsvector(raw_result), plainto_tsquery($1)) as text_rank
            FROM extraction_results er
            JOIN categories c ON er.category_id = c.id
            WHERE to_tsvector(raw_result) @@ plainto_tsquery($1)
            ORDER BY text_rank DESC, er.confidence_score DESC
            LIMIT $2
        """
        
        rows = await self.db_pool.fetch(query, context.user_query, limit)
        
        return {
            "query_type": "semantic_search",
            "results": [dict(row) for row in rows],
            "routing_info": {
                "intent": decision.intent.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "parameters_used": params
            }
        }
    
    async def _execute_structured_query(self, context: QueryContext, decision: RoutingDecision) -> Dict[str, Any]:
        """Execute structured SQL query."""
        
        params = decision.suggested_parameters
        
        if decision.intent == QueryIntent.AGGREGATE_STATS:
            # Statistical aggregation query
            query = """
                SELECT 
                    c.name as category,
                    COUNT(*) as item_count,
                    AVG(er.confidence_score) as avg_confidence,
                    MAX(er.created_at) as latest_item
                FROM extraction_results er
                JOIN categories c ON er.category_id = c.id
                GROUP BY c.name
                ORDER BY item_count DESC
            """
            rows = await self.db_pool.fetch(query)
            
        elif decision.intent == QueryIntent.FILTER_DATA:
            # Filtering query
            where_clause = "WHERE 1=1"
            query_params = []
            param_count = 0
            
            if context.category_filter:
                param_count += 1
                where_clause += f" AND c.name ILIKE ${param_count}"
                query_params.append(f"%{context.category_filter}%")
            
            query = f"""
                SELECT 
                    er.id, er.raw_result, er.confidence_score,
                    c.name as category_name, er.created_at
                FROM extraction_results er
                JOIN categories c ON er.category_id = c.id
                {where_clause}
                ORDER BY er.created_at DESC
                LIMIT {context.limit}
            """
            
            rows = await self.db_pool.fetch(query, *query_params)
            
        else:
            # Generic structured query
            query = """
                SELECT 
                    er.id, er.raw_result, er.confidence_score,
                    c.name as category_name, er.created_at
                FROM extraction_results er
                JOIN categories c ON er.category_id = c.id
                ORDER BY er.created_at DESC
                LIMIT $1
            """
            rows = await self.db_pool.fetch(query, context.limit)
        
        return {
            "query_type": "structured_query",
            "results": [dict(row) for row in rows],
            "routing_info": {
                "intent": decision.intent.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "parameters_used": params
            }
        }
    
    async def _execute_hybrid_analysis(self, context: QueryContext, decision: RoutingDecision) -> Dict[str, Any]:
        """Execute hybrid analysis combining semantic and structured approaches."""
        
        # For hybrid analysis, we'll run both semantic and structured queries
        semantic_context = QueryContext(
            user_query=context.user_query,
            limit=context.limit // 2  # Split the limit
        )
        
        semantic_decision = RoutingDecision(
            query_type=QueryType.SEMANTIC_SEARCH,
            intent=decision.intent,
            confidence=0.8,
            reasoning="Semantic component of hybrid analysis",
            suggested_parameters={"similarity_threshold": 0.6}
        )
        
        structured_decision = RoutingDecision(
            query_type=QueryType.STRUCTURED_QUERY,
            intent=decision.intent,
            confidence=0.8,
            reasoning="Structured component of hybrid analysis",
            suggested_parameters={"use_sql": True}
        )
        
        # Execute both approaches
        semantic_results = await self._execute_semantic_search(semantic_context, semantic_decision)
        structured_results = await self._execute_structured_query(context, structured_decision)
        
        return {
            "query_type": "hybrid_analysis",
            "semantic_results": semantic_results,
            "structured_results": structured_results,
            "routing_info": {
                "intent": decision.intent.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "hybrid_strategy": "parallel_execution"
            }
        }
    
    async def _execute_llm_extraction(self, context: QueryContext, decision: RoutingDecision) -> Dict[str, Any]:
        """Execute LLM-powered extraction and analysis."""
        
        if not OPENROUTER_API_KEY:
            raise Exception("LLM extraction requires OpenRouter API key")
        
        # First, get relevant data
        data_query = """
            SELECT 
                er.raw_result, er.confidence_score,
                c.name as category_name, er.created_at
            FROM extraction_results er
            JOIN categories c ON er.category_id = c.id
            ORDER BY er.created_at DESC
            LIMIT 20
        """
        
        rows = await self.db_pool.fetch(data_query)
        data_context = [dict(row) for row in rows]
        
        # Create LLM prompt for analysis
        prompt = f"""Analyze the following KK6 event planning data based on this query: "{context.user_query}"

Data context:
{json.dumps(data_context[:10], indent=2, default=str)}

Provide insights, patterns, or answers relevant to the query. Focus on actionable information for event planning."""

        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]
                
                return {
                    "query_type": "llm_extraction",
                    "analysis": analysis,
                    "data_context": data_context,
                    "routing_info": {
                        "intent": decision.intent.value,
                        "confidence": decision.confidence,
                        "reasoning": decision.reasoning,
                        "llm_model": OPENROUTER_MODEL
                    }
                }
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise
    
    async def close(self):
        """Clean up resources."""
        if self.db_pool:
            await self.db_pool.close()


# Convenience function for easy integration
async def route_and_execute_query(
    user_query: str,
    session_id: Optional[str] = None,
    category_filter: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Convenience function to route and execute a query in one call.
    
    Example usage:
        result = await route_and_execute_query("Find items similar to entertainment")
        result = await route_and_execute_query("How many items in each category?")
        result = await route_and_execute_query("Analyze patterns in venue planning")
    """
    
    router = RouterAgent()
    await router.initialize()
    
    try:
        context = QueryContext(
            user_query=user_query,
            session_id=session_id,
            category_filter=category_filter,
            limit=limit
        )
        
        # Route the query
        decision = await router.route_query(context)
        
        # Execute the routed query
        result = await router.execute_routed_query(context, decision)
        
        return result
        
    finally:
        await router.close()


# Testing function
async def test_router_agent():
    """Test the router agent with various query types."""
    
    test_queries = [
        "Find items similar to entertainment planning",
        "How many items are in each category?",
        "Filter items by venue category",
        "Find duplicate planning items",
        "Analyze patterns in the planning data", 
        "Compare venue and catering items",
        "Show me recent planning items"
    ]
    
    logger.info("🧪 Testing Router Agent with various queries")
    
    for query in test_queries:
        try:
            logger.info(f"\n🔍 Testing query: '{query}'")
            result = await route_and_execute_query(query, limit=5)
            
            routing_info = result.get("routing_info", {})
            logger.info(f"✅ Routed to: {routing_info.get('intent', 'unknown')}")
            logger.info(f"📊 Results: {len(result.get('results', []))} items")
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
    
    logger.info("🏁 Router Agent testing complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_router_agent())