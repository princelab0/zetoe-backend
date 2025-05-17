# MCP Store API

A FastAPI project for managing MCP (Model Context Protocol) integrations with Composio.

## Features

- **Connection Creation**: Create connections to apps through Composio, which generates authorization URLs and connected account IDs
- **MCP Server Creation**: Create MCP servers using connected account IDs and app names

## Project Structure

```
├── app
│   ├── config       # Configuration settings
│   ├── routers      # API route definitions
│   ├── schemas      # Pydantic models for request/response validation
│   ├── services     # Business logic layer
│   ├── main.py      # FastAPI application initialization
├── tests            # Unit tests 
├── .env             # Environment variables
├── requirements.txt # Project dependencies
├── run.py           # Application entry point
└── Dockerfile       # Docker configuration
```

## Setup and Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-store-api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` with your Composio API key:
```
API_KEY=your_api_key_here
COMPOSIO_API_URL=https://backend.composio.dev/api/v1
LOG_LEVEL=INFO
```

5. Run the application:
```bash
python run.py
```

The API will be available at http://localhost:8000

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t mcp-store-api .
```

2. Run the Docker container:
```bash
docker run -p 8000:8000 --env-file .env mcp-store-api
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### Create Connection

```
POST /connections
```

Request body:
```json
{
  "app_name": "gmail"
}
```

Response:
```json
{
  "redirect_url": "https://example.com/auth",
  "connected_account_id": "acc_123456",
  "message": "Connection initiated successfully"
}
```

### Create MCP Server

```
POST /mcp-servers
```

Request body:
```json
{
  "name": "Gmail Server",
  "connected_account_ids": ["acc_123456"],
  "apps": ["gmail"],
  "entity_id": "default",
  "ttl": "no expiration"
}
```

Response:
```json
{
  "url": "https://example.com/mcp-server",
  "server_id": "srv_123456",
  "message": "MCP server created successfully"
}
```
