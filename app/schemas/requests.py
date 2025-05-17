from pydantic import BaseModel, Field
from typing import List, Optional


class ConnectionRequest(BaseModel):
    app_name: str = Field(..., description="Name of the app to connect to")


class MCPServerRequest(BaseModel):
    name: str = Field(..., description="Name of the MCP server")
    connected_account_ids: List[str] = Field(..., description="List of connected account IDs")
    apps: List[str] = Field(..., description="List of app names to include in the MCP server")
    entity_id: str = Field("default", description="Entity ID for the MCP server")
    ttl: str = Field("no expiration", description="Time to live for the MCP server")
