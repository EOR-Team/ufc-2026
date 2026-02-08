import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # backend目录

from model import OnlineAgent

async def main():
    agent = OnlineAgent(name="TestAgent", instructions="You are a helpful assistant.")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())