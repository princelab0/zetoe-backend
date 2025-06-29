from pydantic import BaseModel, Field
from typing import List, Optional


class ConnectionRequest(BaseModel):
    app_name: str = Field(..., description="Name of the app to connect to")


class MCPServerRequest(BaseModel):
    nanoid: str = Field(..., description="NanoId from Composio")
    ttl: str = Field("no expiration", description="Time to live for the MCP server")
