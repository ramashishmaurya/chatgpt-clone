import os 
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_mcp_adapters.client import MultiServerMCPClient

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient({
    "tavily" : {
        "transport": "streamable_http", 
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
    }
}
)

async def get_mcp_tools():
    """Return all tools provided by tavily """

    return await client.get_tools()


async def main():
    tools = await get_mcp_tools()

    print("Available tools:")

    for tool in tools:
        print(tool.name)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


