import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

# Apply nest_asyncio to allow nested event loops (needed for Jupyter/IPython)
nest_asyncio.apply()

# Load environment variables
load_dotenv(".env")


class MCPOpenAIClient:
    """Client for interacting with OpenAI models using MCP tools."""

    def __init__(self, model: str = "openai/gpt-4o", use_github_ai: bool = False):
        """Initialize the OpenAI MCP client.

        Args:
            model: The model to use.
            use_github_ai: If True, use GitHub AI endpoint instead of OpenAI.
        """
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model = model
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None
        self._cleanup_done = False
        
        # Initialize the appropriate client based on configuration
        if use_github_ai:
            # Use GitHub AI endpoint
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise ValueError("GITHUB_TOKEN environment variable is required for GitHub AI")
            
            endpoint = "https://models.github.ai/inference"
            self.openai_client = AsyncOpenAI(
                base_url=endpoint,
                api_key=token,
            )
            print(f"Using GitHub AI endpoint with model: {model}")
        else:
            # Use standard OpenAI endpoint
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI")
            
            self.openai_client = AsyncOpenAI(api_key=api_key)
            print(f"Using OpenAI endpoint with model: {model}")

    async def connect_to_server(self, server_script_path: str = "server.py"):
        """Connect to an MCP server.

        Args:
            server_script_path: Path to the server script.
        """
        print(f"Attempting to connect to server: {server_script_path}")
        
        # Check if server file exists
        if not os.path.exists(server_script_path):
            raise FileNotFoundError(f"Server script not found: {server_script_path}")
        
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )

        try:
            print("Starting server connection...")
            # Connect to the server with timeout
            stdio_transport = await asyncio.wait_for(
                self.exit_stack.enter_async_context(stdio_client(server_params)),
                timeout=10.0  # 10 second timeout
            )
            self.stdio, self.write = stdio_transport
            print("Server transport established")
            
            print("Creating client session...")
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            print("Client session created")

            # Initialize the connection
            print("Initializing connection...")
            await self.session.initialize()
            print("Connection initialized")

            # List available tools
            print("Listing available tools...")
            tools_result = await self.session.list_tools()
            print(f"\nConnected to server with {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
                
        except asyncio.TimeoutError:
            print("ERROR: Timeout connecting to server")
            raise
        except Exception as e:
            print(f"ERROR: Failed to connect to server: {e}")
            raise

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
            
        tools_result = await self.session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]

    async def process_query_without_mcp(self, query: str) -> str:
        """Process a query using only OpenAI (no MCP tools).

        Args:
            query: The user query.

        Returns:
            The response from OpenAI.
        """
        print("Processing query without MCP tools...")
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools.

        Args:
            query: The user query.

        Returns:
            The response from OpenAI.
        """
        if not self.session:
            print("Warning: No MCP session available, processing without tools")
            return await self.process_query_without_mcp(query)
            
        # Get available tools
        tools = await self.get_mcp_tools()
        print(f"Using {len(tools)} MCP tools")

        # Enhanced system prompt to encourage tool usage
        system_prompt = """You are a helpful assistant with access to specialized knowledge base tools. 
        
        IMPORTANT: When answering questions, you should ALWAYS first check if there's relevant information in the available knowledge base using the get_knowledge_base tool, especially for questions about:
        - MCP (Model Context Protocol)
        - Transport protocols
        - Technical specifications
        - System capabilities
        
        Only provide your own knowledge if the knowledge base doesn't contain relevant information."""

        # Initial OpenAI API call
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto",
        )

        # Get assistant's response
        assistant_message = response.choices[0].message
        print(f"assistant_message --->>> {assistant_message}")

        # Initialize conversation with user query and assistant response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
            assistant_message,
        ]

        # Handle tool calls if present
        if assistant_message.tool_calls:
            print(f"Processing {len(assistant_message.tool_calls)} tool calls...")
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                print(f"Calling tool: {tool_call.function.name}")
                try:
                    # Execute tool call
                    result = await self.session.call_tool(
                        tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    )

                    # Add tool response to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result.content[0].text,
                        }
                    )
                except Exception as e:
                    print(f"Error calling tool {tool_call.function.name}: {e}")
                    # Add error message to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Error: {str(e)}",
                        }
                    )

            # Get final response from OpenAI with tool results
            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="none",  # Don't allow more tool calls
            )

            return final_response.choices[0].message.content

        # No tool calls, just return the direct response
        return assistant_message.content

    async def cleanup(self):
        """Clean up resources safely."""
        if self._cleanup_done:
            return
            
        try:
            # Close the session first if it exists
            if self.session:
                try:
                    # Don't await session cleanup as it might cause issues
                    self.session = None
                except Exception as e:
                    print(f"Warning: Error cleaning up session: {e}")
            
            # Then close the exit stack
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                print(f"Warning: Error cleaning up exit stack: {e}")
                # Force close if needed
                try:
                    self.exit_stack._exit_callbacks.clear()
                except:
                    pass
                    
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
        finally:
            self._cleanup_done = True

    def __del__(self):
        """Destructor to ensure cleanup happens."""
        if not self._cleanup_done:
            try:
                # Try to schedule cleanup if event loop is running
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.cleanup())
            except:
                pass


async def main():
    """Main entry point for the client."""
    client = None
    try:
        # Choose which AI service to use
        use_github_ai = os.environ.get("USE_GITHUB_AI", "true").lower() == "true"  # Default to GitHub AI
        
        if use_github_ai:
            client = MCPOpenAIClient(model="openai/gpt-4o", use_github_ai=True)
        else:
            client = MCPOpenAIClient(model="gpt-4o", use_github_ai=False)
        
        # Try to connect to server, but continue without it if it fails
        try:
            if os.path.exists("server.py"):
                await client.connect_to_server("server.py")
            else:
                print("No server.py found, continuing without MCP tools")
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            print("Continuing without MCP tools...")

        # Test multiple queries
        queries = [
            "What is the default transport protocol for MCP?",
            "What is MCP?",
            "How does the calculator tool work?",
            "What transport protocols are supported?"
        ]
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print('='*60)

            response = await client.process_query(query)
            print(f"\nResponse: {response}")
            
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        # Safe cleanup
        if client:
            try:
                await client.cleanup()
                print("Cleanup completed successfully")
            except Exception as e:
                print(f"Warning: Cleanup error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        print("Application finished")