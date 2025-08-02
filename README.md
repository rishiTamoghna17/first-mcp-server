# MCP Calculator Server

A Model Context Protocol (MCP) server that provides calculator tools and knowledge base access.

## Features

- **Calculator Tools**: Add and subtract numbers
- **Knowledge Base**: Retrieve Q&A pairs from a JSON file
- **Multiple Transport Protocols**: Support for both stdio and SSE transport
- **Docker Support**: Easy deployment with Docker

## Prerequisites

- Docker installed on your system
- For local development: Python 3.11+ and pip

## Quick Start with Docker

### 1. Build the Docker Image

```bash
docker build -t mcp-calculator-server .
```

### 2. Run the Container

```bash
docker run -p 8050:8050 mcp-calculator-server
```

The server will be available at `http://localhost:8050/sse`

### 3. Test the Server

You can test the server using the provided client scripts:

```bash
# For SSE transport (recommended with Docker)
python client-sse.py

# For stdio transport (local development)
python client-stdio.py
```

## Local Development

### 1. Set up Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file:
```
TRANSPORT=sse
```

### 4. Run the Server

```bash
python server.py
```

## Available Tools

### Calculator Tools
- `add(a: int, b: int) -> int`: Add two numbers
- `subtract(a: int, b: int) -> int`: Subtract two numbers

### Knowledge Base Tool
- `get_knowledge_base() -> str`: Retrieve all Q&A pairs from the knowledge base

## Configuration

### Environment Variables

- `TRANSPORT`: Transport protocol (`stdio` or `sse`)
- `PORT`: Server port (default: 8050)
- `HOST`: Server host (default: 0.0.0.0)

### Knowledge Base

The knowledge base is stored in `data/kb.json` with the following format:

```json
[
  {
    "question": "What is MCP?",
    "answer": "MCP (Model Context Protocol) is a protocol for AI assistants..."
  }
]
```

## Docker Commands Reference

### Build Image
```bash
docker build -t mcp-calculator-server .
```

### Run Container
```bash
# Basic run
docker run -p 8050:8050 mcp-calculator-server

# Run with custom environment
docker run -p 8050:8050 -e TRANSPORT=stdio mcp-calculator-server

# Run in background
docker run -d -p 8050:8050 --name mcp-server mcp-calculator-server
```

### Manage Container
```bash
# Stop container
docker stop mcp-server

# Remove container
docker rm mcp-server

# View logs
docker logs mcp-server

# Execute commands in container
docker exec -it mcp-server bash
```

## Troubleshooting

### Port Already in Use
If port 8050 is already in use, you can map to a different port:
```bash
docker run -p 8080:8050 mcp-calculator-server
```

### Permission Issues
On Linux/Mac, you might need to use `sudo` for Docker commands.

### Container Won't Start
Check the logs:
```bash
docker logs <container_name>
```

## Project Structure

```
.
├── server.py              # Main MCP server
├── client-sse.py          # SSE client example
├── client-stdio.py        # STDIO client example
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env                  # Environment variables
├── data/
│   └── kb.json          # Knowledge base file
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## License

This project is open source and available under the MIT License. 