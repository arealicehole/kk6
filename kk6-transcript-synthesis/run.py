#!/usr/bin/env python3
"""Simple runner script for the transcript processor."""

import asyncio
from src.kk6_transcript_synthesis.main import main

if __name__ == "__main__":
    asyncio.run(main())