import httpx
import requests
from composio import Composio, ComposioToolSet
from typing import Dict, Any, List, Optional
from app.config.settings import get_settings
from fastapi import HTTPException

settings = get_settings()


class ComposioService:
    def __init__(self):
        self.api_key = settings.API_KEY
        self.base_url = settings.COMPOSIO_API_URL
        self.composio = Composio(api_key=self.api_key)
        self.toolset = ComposioToolSet(api_key=self.api_key)
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_app_details(self, app_name: str) -> Dict[str, Any]:
        """Get app details from the API."""
        try:
            app_response = requests.get(
                f"{self.base_url}/apps/{app_name}",
                headers={"x-api-key": self.api_key}
            )
            app_response.raise_for_status()
            return app_response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to get app details: {str(e)}")

    async def get_default_scopes(self, app_name: str) -> List[str]:
        """Extract the default scopes from the app's OAUTH2 auth scheme."""
        try:
            app_data = await self.get_app_details(app_name)
            
            # Extract default scopes from auth_schemes
            default_scopes = None
            for scheme in app_data.get("auth_schemes", []):
                if scheme.get("mode") == "OAUTH2":
                    for field in scheme.get("fields", []):
                        if field.get("name") == "scopes":
                            default_scopes = field.get("default")
                            break
            
            if not default_scopes:
                raise HTTPException(status_code=400, detail=f"No default scopes found for {app_name}")
                
            return default_scopes
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get default scopes: {str(e)}")

    async def create_connection(self, app_name: str) -> Dict[str, str]:
        """Create a connection for the given app."""
        try:
            # Get app details
            default_scopes = await self.get_default_scopes(app_name)
            
            # Get app from Composio SDK
            app = self.composio.apps.get(name=app_name)
            
            # Create integration
            integration = self.composio.integrations.create(
                app_id=app.appId,
                auth_config={"scopes": default_scopes},
                auth_mode="OAUTH2",
                force_new_integration=True,
                name=f"{app_name}_integration",
                use_composio_auth=True
            )
            
            # Get integration details
            integration = self.toolset.get_integration(id=integration.id)
            
            # Initiate connection
            connection_request = self.toolset.initiate_connection(
                integration_id=integration.id,
                entity_id="default",
            )
            
            return {
                "redirect_url": connection_request.redirectUrl,
                "connected_account_id": connection_request.connectedAccountId
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")
    
    async def create_mcp_server(self, name: str, apps: List[str], connected_account_ids: List[str], 
                               entity_id: str = "default", ttl: str = "no expiration") -> Dict[str, Any]:
        """Create a new MCP server."""
        try:
            url = f"{self.base_url}/mcp/servers"
            
            payload = {
                "name": name,
                "apps": apps,
                "connectedAccountIds": connected_account_ids,
                "entityId": entity_id,
                "ttl": ttl,
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            mcp_response = response.json()
            return {
                "url": mcp_response.get("url"),
                "server_id": mcp_response.get("id")
            }
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to create MCP server: {str(e)}")
