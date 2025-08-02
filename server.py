import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Create an MCP server
mcp = FastMCP(
    name="Calculator",
    port=8050,
    host="0.0.0.0",
)


# # Add an addition tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b

# # Add a subtraction tool
# @mcp.tool()
# def subtract(a: int, b: int) -> int:
#     """Subtract two numbers"""
#     return a - b

@mcp.tool()
def get_knowledge_base() -> str:
    """Retrieve the entire knowledge base as a formatted string.
    return:
           A formatted string containing all Q&A pairs in the knowledge base.
    """
    try:
        kb_path = os.path.join(os.path.dirname(__file__), "data", "kb.json")
        with open(kb_path, 'r') as kb_file:
            kb_data = json.load(kb_file)
            kb_text = "Here is the retrieved knowledge base:\n\n"
            
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
            return kb_text
    except FileNotFoundError:
        return "Knowledge base file not found."
    except json.JSONDecodeError:
        return "Error decoding knowledge base file. Please ensure it is in valid JSON format."
    except Exception as e:
        return f"An error occurred while retrieving the knowledge base: {str(e)}"


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")  # Default to stdio if not set
    if transport == "stdio":
        print("Starting MCP server on stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Starting MCP server on sse transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Invalid transport: {transport}")
