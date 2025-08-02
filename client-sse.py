import asyncio
import nest_asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client

nest_asyncio.apply()

"""
make sure :
1. the server is running before running this script.
2.the server is configured to use SSE transport.
3. the server is listening on port 8050.
"""

async def main():

    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            tool_result = await session.list_tools()
            print("Available tools:")
            for tool in tool_result.tools:
                print(f"- {tool.name}: {tool.description}")
                
            result = await session.call_tool(
                name="add",
                arguments={"a": 1, "b": 2},
            )
            print(f"Result of add(1, 2): {result.content}")
            
if __name__ == "__main__":
    asyncio.run(main())









