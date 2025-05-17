from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.requests import MCPServerRequest
from app.schemas.responses import MCPServerResponse, ErrorResponse
from app.services.composio_service import ComposioService
from typing import Any

router = APIRouter(
    prefix="/mcp-servers",
    tags=["mcp-servers"],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)


@router.post("/", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    request: MCPServerRequest, 
    composio_service: ComposioService = Depends(lambda: ComposioService())
) -> Any:
    """
    Create a new MCP server.
    
    This will use the connected account ID to create an MCP server with the specified apps.
    
    Returns:
    - url: URL of the created MCP server
    - server_id: ID of the created MCP server
    """
    try:
        mcp_server_data = await composio_service.create_mcp_server(
            name=request.name,
            apps=request.apps,
            connected_account_ids=request.connected_account_ids,
            entity_id=request.entity_id,
            ttl=request.ttl
        )
        
        return MCPServerResponse(
            url=mcp_server_data["url"],
            server_id=mcp_server_data["server_id"]
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
