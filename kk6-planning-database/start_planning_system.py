#!/usr/bin/env python3
"""
KK6 Planning Database System Launcher
Starts the planning database API server and provides system status.
"""

import asyncio
import subprocess
import sys
import time
import httpx
from pathlib import Path

async def check_database():
    """Check if PostgreSQL database is accessible."""
    try:
        import asyncpg
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:55432/kk6_planning")
        await conn.execute("SELECT 1")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Database not accessible: {e}")
        return False

async def check_ollama():
    """Check if Ollama is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            return response.status_code == 200
    except:
        return False

async def main():
    """Main launcher function."""
    print("🎉 KK6 Planning Database System")
    print("=" * 40)
    
    # Check prerequisites
    print("🔍 Checking system prerequisites...")
    
    # Check database
    db_ok = await check_database()
    if not db_ok:
        print("💡 To setup database, run: python setup_planning_db.py")
        return
    
    print("✅ Database connection OK")
    
    # Check Ollama (optional for extraction)
    ollama_ok = await check_ollama()
    if ollama_ok:
        print("✅ Ollama LLM available for extraction")
    else:
        print("⚠️ Ollama not available (extraction won't work)")
    
    print("\n🚀 Starting KK6 Planning API Server...")
    print("📊 Dashboard: http://localhost:8090/web")
    print("📋 API Docs: http://localhost:8090/docs")
    print("🔄 Press Ctrl+C to stop")
    print("-" * 40)
    
    # Start the API server
    try:
        subprocess.run([sys.executable, "kk6_planning_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down KK6 Planning System")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    asyncio.run(main())