import asyncio
import nest_asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

nest_asyncio.apply() #need to run this before running the client

async def main():
    server_params = StdioServerParameters(
        command='python',
        args=['server.py'],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
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





