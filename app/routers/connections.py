from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.requests import ConnectionRequest
from app.schemas.responses import ConnectionResponse, ErrorResponse
from app.services.composio_service import ComposioService
from typing import Any

router = APIRouter(
    prefix="/connections",
    tags=["connections"],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    request: ConnectionRequest, 
    composio_service: ComposioService = Depends(lambda: ComposioService())
) -> Any:
    """
    Create a new connection for an app.
    
    This will:
    1. Get the app info
    2. Get the integration ID using the app info
    3. Get the connected account ID and auth URL using the integration ID
    
    Returns:
    - redirect_url: URL to redirect the user for authorization
    - connected_account_id: ID of the connected account
    """
    try:
        connection_data = await composio_service.create_connection(request.app_name)
        
        return ConnectionResponse(
            redirect_url=connection_data["redirect_url"],
            connected_account_id=connection_data["connected_account_id"]
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
