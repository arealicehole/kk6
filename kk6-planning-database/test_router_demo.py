"""
Demo of Router Agent Intent Classification (without database connection)

This demonstrates the router agent's intelligent intent classification
and routing decisions without requiring a database connection.
"""

import asyncio
import logging
from router_agent import RouterAgent, QueryContext, QueryType, QueryIntent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


class MockRouterAgent(RouterAgent):
    """Mock version of RouterAgent that doesn't require database connection."""
    
    async def initialize(self):
        """Mock initialization without database."""
        self.intent_patterns = self._initialize_intent_patterns()
        self.db_stats = {"total_items": 150, "categories": 8, "sessions": 12}
        logger.info("🧠 Mock Router Agent initialized successfully")
    
    async def _load_query_optimization_data(self):
        """Mock optimization data loading."""
        pass


async def demo_router_intelligence():
    """Demonstrate the router agent's intelligence without database dependency."""
    
    print("=" * 80)
    print("🎯 KK6 ROUTER AGENT INTELLIGENCE DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Test queries representing different intents
    test_queries = [
        ("Find items similar to entertainment planning", "Semantic search for content similarity"),
        ("How many items are in each category?", "Statistical aggregation query"),  
        ("Filter items by venue category", "Structured data filtering"),
        ("Find duplicate planning items", "Hybrid duplicate detection"),
        ("Analyze patterns in the planning data", "LLM-powered insight extraction"),
        ("Compare venue and catering items", "Hybrid comparison analysis"),
        ("Show me recent planning items", "Temporal/time-based query"),
        ("What venues were mentioned for the charity event?", "Content search"),
        ("Count total planning items created this week", "Aggregation with time filter"),
        ("Merge similar food and beverage entries", "Duplicate detection")
    ]
    
    router = MockRouterAgent()
    await router.initialize()
    
    print("🧪 TESTING QUERY ROUTING & INTENT CLASSIFICATION")
    print("-" * 60)
    
    for query, description in test_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"💡 Expected: {description}")
        
        try:
            # Create context
            context = QueryContext(user_query=query, limit=10)
            
            # Classify intent
            intent = await router.classify_intent(query)
            print(f"🎯 Intent: {intent.value}")
            
            # Get routing decision
            decision = await router._determine_routing_strategy(intent, context)
            
            print(f"🧭 Route: {decision.query_type.value}")
            print(f"📊 Confidence: {decision.confidence:.1%}")
            print(f"💭 Reasoning: {decision.reasoning}")
            
            # Show suggested parameters
            if decision.suggested_parameters:
                print(f"⚙️  Parameters: {list(decision.suggested_parameters.keys())}")
            
            if decision.fallback_strategy:
                print(f"🔄 Fallback: {decision.fallback_strategy.value}")
            
            print("✅ SUCCESS")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 60)
    
    print("\n🎉 ROUTER AGENT DEMONSTRATION COMPLETE!")
    print("\n📋 SUMMARY OF ROUTING CAPABILITIES:")
    print("  🔍 Semantic Search - Content similarity, fuzzy matching")
    print("  📊 Structured Query - Filtering, aggregation, precise data retrieval")
    print("  🔀 Hybrid Analysis - Complex comparisons, duplicate detection")
    print("  🤖 LLM Extraction - Pattern analysis, insight generation")
    print("  ⏰ Temporal Analysis - Time-based queries and filtering")
    print("\n🚀 READY FOR INTEGRATION INTO KK6 VISUAL PIPELINE!")


async def test_intent_classification_accuracy():
    """Test intent classification accuracy across various query patterns."""
    
    print("\n" + "=" * 60)
    print("🎯 INTENT CLASSIFICATION ACCURACY TEST")
    print("=" * 60)
    
    # Test cases with expected intents
    test_cases = [
        # Search content
        ("find entertainment items", QueryIntent.SEARCH_CONTENT),
        ("search for venue planning", QueryIntent.SEARCH_CONTENT),
        ("items about catering", QueryIntent.SEARCH_CONTENT),
        
        # Filter data  
        ("filter by category", QueryIntent.FILTER_DATA),
        ("items where status is approved", QueryIntent.FILTER_DATA),
        ("from venue category", QueryIntent.FILTER_DATA),
        
        # Aggregate stats
        ("how many items", QueryIntent.AGGREGATE_STATS),
        ("count of planning entries", QueryIntent.AGGREGATE_STATS),
        ("total items per category", QueryIntent.AGGREGATE_STATS),
        
        # Find duplicates
        ("find duplicates", QueryIntent.FIND_DUPLICATES),
        ("similar entries to merge", QueryIntent.FIND_DUPLICATES),
        ("overlapping planning items", QueryIntent.FIND_DUPLICATES),
        
        # Extract insights
        ("analyze planning patterns", QueryIntent.EXTRACT_INSIGHTS),
        ("what insights can you provide", QueryIntent.EXTRACT_INSIGHTS),
        ("summarize the planning data", QueryIntent.EXTRACT_INSIGHTS),
        
        # Compare items
        ("compare venue options", QueryIntent.COMPARE_ITEMS),
        ("difference between catering plans", QueryIntent.COMPARE_ITEMS),
        ("venue A versus venue B", QueryIntent.COMPARE_ITEMS),
        
        # Temporal analysis
        ("recent planning items", QueryIntent.TEMPORAL_ANALYSIS),
        ("when were items created", QueryIntent.TEMPORAL_ANALYSIS),
        ("timeline of planning activities", QueryIntent.TEMPORAL_ANALYSIS)
    ]
    
    router = MockRouterAgent()
    await router.initialize()
    
    correct_classifications = 0
    total_tests = len(test_cases)
    
    for query, expected_intent in test_cases:
        classified_intent = await router.classify_intent(query)
        
        is_correct = classified_intent == expected_intent
        correct_classifications += is_correct
        
        status = "✅" if is_correct else "❌"
        print(f"{status} '{query}' -> {classified_intent.value} (expected: {expected_intent.value})")
    
    accuracy = correct_classifications / total_tests
    print(f"\n📊 ACCURACY: {correct_classifications}/{total_tests} = {accuracy:.1%}")
    
    if accuracy >= 0.8:
        print("🎉 EXCELLENT: Router Agent shows high classification accuracy!")
    elif accuracy >= 0.6:
        print("👍 GOOD: Router Agent shows reasonable classification accuracy")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Classification accuracy could be better")
    
    return accuracy


if __name__ == "__main__":
    asyncio.run(demo_router_intelligence())
    asyncio.run(test_intent_classification_accuracy())