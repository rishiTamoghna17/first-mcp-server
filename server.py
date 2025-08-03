#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from typing import Any, Sequence

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Create server instance
server = Server("knowledge-base-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get_knowledge_base",
            description="Retrieve the entire knowledge base as a formatted string",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "get_knowledge_base":
        try:
            # Try to find kb.json in data directory
            kb_path = os.path.join(os.path.dirname(__file__), "data", "kb.json")
            
            if not os.path.exists(kb_path):
                # Create a sample knowledge base if it doesn't exist
                os.makedirs(os.path.dirname(kb_path), exist_ok=True)
                sample_kb = [
                    {
                        "question": "What is MCP?",
                        "answer": "MCP (Model Context Protocol) is a protocol for connecting AI models with external tools and data sources."
                    },
                    {
                        "question": "What is the default transport protocol for MCP?",
                        "answer": "The default transport protocol for MCP is stdio (standard input/output)."
                    }
                ]
                with open(kb_path, 'w') as f:
                    json.dump(sample_kb, f, indent=2)
            
            with open(kb_path, 'r') as kb_file:
                kb_data = json.load(kb_file)
                kb_text = "===============Here is the retrieved knowledge base:\n\n"
                
                if isinstance(kb_data, list):
                    for i, item in enumerate(kb_data, 1):
                        if isinstance(item, dict):
                            question = item.get("question", "Unknown question")
                            answer = item.get("answer", "Unknown answer")
                        else:
                            question = f"Item {i}"
                            answer = str(item)
                        kb_text += f"Q{i}: **{question}**\n"
                        kb_text += f"A{i}: {answer}\n\n"
                else:
                    kb_text += f"Knowledge base content: {json.dumps(kb_data, indent=2)}\n\n"
                
                return [types.TextContent(type="text", text=kb_text)]
                
        except FileNotFoundError:
            return [types.TextContent(type="text", text="Knowledge base file not found.")]
        except json.JSONDecodeError:
            return [types.TextContent(type="text", text="Error decoding knowledge base file. Please ensure it is in valid JSON format.")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"An error occurred while retrieving the knowledge base: {str(e)}")]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="knowledge-base-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())