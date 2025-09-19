"""CLI entry point for the package."""

from .main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())