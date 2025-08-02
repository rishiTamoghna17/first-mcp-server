# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY .env .

# Create data directory and copy knowledge base
COPY data/ ./data/

# Expose the port the server runs on
EXPOSE 8050

# Set environment variable for SSE transport
ENV TRANSPORT=sse

# Run the server
CMD ["python", "server.py"] 