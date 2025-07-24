import uuid
import httpx
import requests
from composio import Composio, ComposioToolSet
from typing import Dict, Any, List, Optional
from app.config.settings import get_settings
from fastapi import HTTPException
from urllib.parse import urlparse, urlunparse
import random
import string

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

    def generate_random_name(self, length=7):
        """
        Generates a random string of the specified length (default 7),
        using uppercase, lowercase letters and digits.
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    def get_nanoid_from_uuid(self, uuid: str, type_: str = "AUTH_CONFIG") -> dict:
        """
        Fetches a NanoId from a UUID using the Composio migration API.

        Args:
            uuid (str): The UUID to look up.
            type_ (str): The type parameter, default is "AUTH_CONFIG".

        Returns:
            dict: The JSON response containing the NanoId
        """
        url = "https://backend.composio.dev/api/v3/migration/get-nanoid"
        params = {
            "uuid": uuid,
            "type": type_
        }
        headers = {
            "x-api-key": self.api_key
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

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
            # Get app from Composio SDK
            app = self.composio.apps.get(name=app_name)
            
            # Create integration with required parameters
            integration = self.composio.integrations.create(
                app_id=app.appId,
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
            
            uuid = integration.id
            nanoid = self.get_nanoid_from_uuid(uuid, type_="AUTH_CONFIG")

            # Return the connection details
            return {
                "redirect_url": connection_request.redirectUrl,
                "connected_account_id": connection_request.connectedAccountId,
                "nanoid": nanoid
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")
    
    def to_standard_sse_url(self, mcp_url: str) -> str:
        """
        Converts an MCP server URL to standard SSE format.

        Args:
            mcp_url (str): Original MCP server URL

        Returns:
            str: Standardized SSE URL
        """
        parsed = urlparse(mcp_url)
        path_parts = parsed.path.strip('/').split('/')

        try:
            server_index = path_parts.index('server')
            server_id = path_parts[server_index + 1]
        except (ValueError, IndexError):
            raise HTTPException(status_code=500, detail=f"Could not extract server ID from URL: {mcp_url}")

        new_path = f"/composio/server/{server_id}/sse"
        new_query = "useComposioHelperActions=true"
        
        new_parsed = parsed._replace(path=new_path, query=new_query)
        return urlunparse(new_parsed)

    async def create_mcp_server(self, name: str, auth_config_ids: List[str], ttl: str = "no expiration") -> Dict[str, Any]:
        """Create a new MCP server."""
        try:
            url = "https://backend.composio.dev/api/v3/mcp/servers"
            headers = {
                "x-api-key": self.api_key
            }
            payload = {
                "name": name,
                "auth_config_ids": auth_config_ids,
                "ttl": ttl
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            mcp_url = data.get("mcp_url")
            
            if not mcp_url:
                raise HTTPException(status_code=500, detail="MCP server created but URL not found in response")

            # Convert to standard SSE URL
            standard_url = self.to_standard_sse_url(mcp_url)
            
            return {
                "url": standard_url,
                "server_id": data.get("id")
            }
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to create MCP server: {str(e)}")
