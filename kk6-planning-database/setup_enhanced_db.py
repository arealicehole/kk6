#!/usr/bin/env python3
"""
Setup Enhanced KK6 Planning Database with Vector Support
"""

import asyncio
import asyncpg
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def setup_enhanced_database():
    """Set up the enhanced database with vector support."""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        logger.info("🔧 Setting up enhanced KK6 planning database...")
        
        # First, try to install pgvector extension
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            logger.info("✅ pgvector extension enabled")
        except Exception as e:
            logger.error(f"❌ Failed to install pgvector: {e}")
            logger.info("💡 You may need to install pgvector first:")
            logger.info("   Docker: docker exec -it <container> sh -c 'apt update && apt install -y postgresql-16-pgvector'")
            logger.info("   Or rebuild container with pgvector support")
            return False
        
        # Read and execute the enhanced schema
        schema_path = Path("enhanced_schema_with_vectors.sql")
        if schema_path.exists():
            with open(schema_path) as f:
                schema_sql = f.read()
            
            # Execute schema
            await conn.execute(schema_sql)
            logger.info("✅ Enhanced schema created with vector support")
        else:
            logger.error("❌ Schema file not found: enhanced_schema_with_vectors.sql")
            return False
            
        # Insert the 31 categories with descriptions for embedding
        categories_data = [
            ("venue_management", None, "Venue selection, layout, capacity planning, space requirements, accessibility"),
            ("food_catering", None, "Food and beverage planning, catering services, menu selection, dietary restrictions"),
            ("cannabis_supply", None, "Cannabis products, supply chain, regulations, dispensary partnerships"),
            ("budget_finance", None, "Budget planning, cost tracking, revenue projections, financial management"),
            ("staffing_volunteers", None, "Staff requirements, volunteer coordination, role assignments, scheduling"),
            ("legal_compliance", None, "Legal requirements, permits, licenses, regulatory compliance, liability"),
            ("marketing_promotion", None, "Marketing strategies, promotional campaigns, social media, advertising"),
            ("security_safety", None, "Security planning, crowd control, safety measures, risk management"),
            ("attendee_management", None, "Guest list management, registration, check-in processes, attendee services"),
            ("logistics_coordination", None, "Event logistics, coordination between teams, timeline management"),
            ("equipment_supplies", None, "Equipment rental, supplies procurement, setup requirements"),
            ("entertainment_activities", None, "Entertainment planning, activities, performances, guest experiences"),
            ("transportation_parking", None, "Transportation arrangements, parking management, accessibility"),
            ("risk_management", None, "Risk assessment, contingency planning, insurance, emergency procedures"),
            ("partnerships_sponsors", None, "Partnership agreements, sponsor management, vendor relationships"),
            ("charity_component", None, "Charitable aspects, toy drive, donation management, beneficiary coordination"),
            ("communication_coordination", None, "Team communication, coordination tools, information management"),
            ("date_scheduling", None, "Event date selection, timeline planning, milestone scheduling"),
            ("capacity_attendance", None, "Attendance projections, capacity planning, crowd management"),
            ("technology_av", None, "Audio/visual equipment, technology requirements, technical support"),
            ("permits_licensing", None, "Event permits, licensing requirements, regulatory approvals"),
            ("waste_management", None, "Waste disposal, recycling, environmental considerations"),
            ("weather_contingency", None, "Weather planning, contingency plans, backup options"),
            ("photography_media", None, "Photography, videography, media coverage, content creation"),
            ("registration_ticketing", None, "Registration systems, ticketing, payment processing"),
            ("accessibility_accommodation", None, "Accessibility planning, accommodations, inclusive design"),
            ("vendor_management", None, "Vendor selection, contract management, supplier relationships"),
            ("quality_control", None, "Quality assurance, standards management, performance monitoring"),
            ("post_event_analysis", None, "Post-event evaluation, feedback collection, lessons learned"),
            ("emergency_procedures", None, "Emergency planning, crisis management, safety protocols"),
            ("miscellaneous", None, "Other event planning considerations not covered by specific categories")
        ]
        
        # Insert categories (check if they exist first)
        for name, parent_id, description in categories_data:
            exists = await conn.fetchval(
                "SELECT 1 FROM categories WHERE name = $1", name
            )
            if not exists:
                await conn.execute(
                    "INSERT INTO categories (name, parent_id, description) VALUES ($1, $2, $3)",
                    name, parent_id, description
                )
        
        logger.info(f"✅ Inserted {len(categories_data)} categories")
        
        # Verify setup
        categories_count = await conn.fetchval("SELECT COUNT(*) FROM categories")
        logger.info(f"📊 Database setup complete: {categories_count} categories")
        
        # Check vector extension
        vector_check = await conn.fetchval("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        if vector_check:
            logger.info("✅ Vector extension verified working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False
        
    finally:
        await conn.close()

if __name__ == "__main__":
    success = asyncio.run(setup_enhanced_database())
    if success:
        print("\n🎉 Enhanced database setup complete!")
        print("🔗 Next steps:")
        print("   1. Run embedding_service.py to test vectorization")
        print("   2. Process transcripts with intelligent chunking")
        print("   3. Test category-specific semantic search")
    else:
        print("\n❌ Setup failed - check logs above")