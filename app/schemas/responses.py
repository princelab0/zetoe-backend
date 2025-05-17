from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ConnectionResponse(BaseModel):
    redirect_url: str = Field(..., description="URL to redirect the user for authorization")
    connected_account_id: str = Field(..., description="ID of the connected account")
    message: str = Field("Connection initiated successfully", description="Response message")


class MCPServerResponse(BaseModel):
    url: str = Field(..., description="URL of the created MCP server")
    server_id: str = Field(..., description="ID of the created MCP server")
    message: str = Field("MCP server created successfully", description="Response message")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error details")
