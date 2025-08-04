# MCP Knowledge Base Server

A Model Context Protocol (MCP) server implementation that provides AI assistants with access to a structured knowledge base. This project demonstrates how to build both MCP servers and clients, with support for multiple AI providers including OpenAI and GitHub AI.

## 🚀 Features

- **Knowledge Base Tool**: Retrieve structured information from a JSON knowledge base
- **Dual AI Provider Support**: Works with both OpenAI API and GitHub AI
- **MCP Protocol Implementation**: Full server and client implementation
- **Automatic Fallback**: Gracefully handles missing server connections
- **Flexible Transport**: Supports stdio transport protocol
- **Error Handling**: Robust error handling and logging

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key OR GitHub token (depending on your preferred AI provider)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd <your-repository-name>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   
   For OpenAI API:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   USE_GITHUB_AI=false
   ```
   
   For GitHub AI:
   ```bash
   GITHUB_TOKEN=your_github_token_here
   USE_GITHUB_AI=true
   ```

## 📁 Project Structure

```
mcp-knowledge-base/
├── server.py              # MCP server implementation
├── client.py              # MCP client with AI integration
├── data/
│   └── kb.json            # Knowledge base data
├── test_github_ai.py      # GitHub AI connection test
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
└── LICENSE               # MIT License
```

## 🏃‍♂️ Quick Start

### Running the Server Standalone

```bash
python server.py
```

The server will start and listen for MCP protocol messages via stdin/stdout.

### Running the Client with AI Integration

```bash
python client.py
```

This will:
1. Connect to the MCP server
2. Initialize the AI client (OpenAI or GitHub AI)
3. Process several test queries using both AI and knowledge base tools

### Testing Individual Components

Test GitHub AI connection:
```bash
python test_github_ai.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes (if using OpenAI) |
| `GITHUB_TOKEN` | GitHub personal access token | - | Yes (if using GitHub AI) |
| `USE_GITHUB_AI` | Use GitHub AI instead of OpenAI | `true` | No |

### Knowledge Base Format

The knowledge base is stored in `data/kb.json` as an array of Q&A objects:

```json
[
  {
    "question": "What is MCP?",
    "answer": "MCP (Model Context Protocol) is a protocol for AI assistants to communicate with external data sources and tools."
  },
  {
    "question": "How does the calculator tool work?",
    "answer": "The calculator provides add and subtract functions for basic arithmetic operations."
  }
]
```

## 🔌 MCP Tools

### `get_knowledge_base`

Retrieves the entire knowledge base as a formatted string.

**Parameters:** None

**Returns:** Formatted text containing all questions and answers from the knowledge base

**Example Usage:**
```python
# The AI assistant will automatically use this tool when relevant
# No manual invocation needed
```

## 🏗️ Architecture

### Server Component (`server.py`)

- Implements MCP protocol using the `mcp` library
- Provides `get_knowledge_base` tool
- Handles JSON knowledge base loading and formatting
- Uses stdio transport for communication

### Client Component (`client.py`)

- Connects to MCP server via stdio transport
- Integrates with OpenAI or GitHub AI APIs
- Automatically converts MCP tools to OpenAI function format
- Handles tool execution and response processing

### Key Classes

#### `MCPOpenAIClient`

Main client class that orchestrates MCP server communication and AI interactions.

**Methods:**
- `connect_to_server(server_script_path)`: Connect to MCP server
- `get_mcp_tools()`: Retrieve tools in OpenAI format
- `process_query(query)`: Process user query with AI and tools
- `cleanup()`: Clean up resources

## 🚨 Error Handling

The project includes comprehensive error handling:

- **Server Connection**: Graceful fallback when server is unavailable
- **API Errors**: Proper handling of AI provider API errors
- **File Operations**: Safe handling of missing or corrupted knowledge base files
- **Tool Execution**: Error reporting for failed tool calls

## 🔍 Usage Examples

### Basic Query Processing

```python
from client import MCPOpenAIClient

# Initialize client
client = MCPOpenAIClient(use_github_ai=True)

# Connect to server
await client.connect_to_server()

# Process a query
response = await client.process_query("What is MCP?")
print(response)

# Clean up
await client.cleanup()
```

### Sample Queries

The client comes with several test queries:

- "What is the default transport protocol for MCP?"
- "What is MCP?"
- "How does the calculator tool work?"
- "What transport protocols are supported?"

## 🧪 Testing

### Manual Testing

1. Start the server in one terminal:
   ```bash
   python server.py
   ```

2. Run the client in another terminal:
   ```bash
   python client.py
   ```

### GitHub AI Testing

```bash
python test_github_ai.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"Server script not found"**
   - Ensure `server.py` is in the current directory
   - Check file permissions

2. **"Timeout connecting to server"**
   - Verify Python environment and dependencies
   - Check if port is already in use

3. **"API key not found"**
   - Verify your `.env` file exists and contains the correct API key
   - Check environment variable names match exactly

4. **"Knowledge base file not found"**
   - The server will automatically create a sample `data/kb.json` if missing
   - Ensure the `data` directory is writable

### Debug Mode

For additional debugging information, the client includes extensive logging. Check console output for connection status and tool execution details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built using the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk)
- Supports OpenAI and GitHub AI APIs
- Inspired by the MCP community examples

## 📚 Learn More

- [MCP Documentation](https://modelcontextprotocol.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GitHub AI Documentation](https://docs.github.com/en/copilot)

---

**Happy coding with MCP! 🎉**