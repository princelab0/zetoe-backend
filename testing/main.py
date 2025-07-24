from composio import Composio
from composio import ComposioToolSet
import requests

def create_gmail_integration(api_key: str, integration_name: str) -> dict:
    """
    Creates a new Gmail integration using the Composio client.

    Args:
        api_key (str): Your Composio API key.
        integration_name (str): The name to give the new integration.

    Returns:
        dict: A dictionary with appId, appName, and integrationId.
    """
    # Initialize the Composio client
    composio = Composio(api_key=api_key)

    # Get the Gmail app
    app = composio.apps.get(name="gmail")

    # Create a new integration
    integration = composio.integrations.create(
        app_id=app.appId,
        auth_mode="OAUTH2",
        force_new_integration=True,
        name=integration_name,
        use_composio_auth=True
    )

    return {
        "appId": integration.appId,
        "appName": integration.appName,
        "integrationId": integration.id
    }



def get_nanoid_from_uuid(uuid: str, api_key: str, type_: str = "AUTH_CONFIG") -> dict:
    """
    Fetches a NanoId from a UUID using the Composio migration API.

    Args:
        uuid (str): The UUID to look up.
        api_key (str): Your Composio API key.
        type_ (str): The type parameter, default is "AUTH_CONFIG".

    Returns:
        dict: The JSON response containing the NanoId or error.
    """
    url = "https://backend.composio.dev/api/v3/migration/get-nanoid"
    params = {
        "uuid": uuid,
        "type": type_
    }
    headers = {
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # will raise an error for HTTP 4xx/5xx
    return response.json()



def initiate_composio_connection(api_key: str, integration_id: str, entity_id: str = "default") -> dict:
    """
    Initiates a connection for a given integration using ComposioToolSet.

    Args:
        api_key (str): Your Composio API key.
        integration_id (str): The ID of the integration you want to connect.
        entity_id (str): Typically "default" or specific to your user/entity.

    Returns:
        dict: Contains expected input fields, redirect URL for OAuth, and connected account ID.
    """
    # Initialize the Composio toolset
    toolset = ComposioToolSet(api_key=api_key)

    # Get integration details
    integration = toolset.get_integration(id=integration_id)

    # Initiate the connection process
    connection_request = toolset.initiate_connection(
        integration_id=integration.id,
        entity_id=entity_id
    )

    return {
        "expectedInputFields": integration.expectedInputFields,
        "redirectUrl": connection_request.redirectUrl,
        "connectedAccountId": connection_request.connectedAccountId
    }



def create_mcp_server(api_key, name, auth_config_ids, ttl="no expiration"):
    """
    Creates a new MCP server using the Composio API and returns the MCP server URL.

    :param api_key: Your Composio API key
    :param name: Name for the MCP server
    :param auth_config_ids: List of authentication config IDs
    :param ttl: Time-to-live (default is "no expiration")
    :return: MCP server URL as a string, or None if creation failed
    """
    url = "https://backend.composio.dev/api/v3/mcp/servers"
    headers = {
        "x-api-key": api_key
    }
    payload = {
        "name": name,
        "auth_config_ids": auth_config_ids,
        "ttl": ttl
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        mcp_url = data.get("mcp_url")
        if mcp_url:
            return mcp_url
        else:
            print("MCP server created, but 'mcp_url' not found in response.")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


import random
import string

def generate_random_name(length=7):
    """
    Generates a random string of the specified length (default 7),
    using uppercase, lowercase letters and digits.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


from urllib.parse import urlparse, urlunparse


def to_standard_sse_url(mcp_url):
    """
    Given an MCP server URL, converts it to:
    https://mcp.composio.dev/composio/server/{server-id}/sse?useComposioHelperActions=true
    regardless of the original path or query.

    :param mcp_url: original MCP server URL
    :return: standardized SSE URL
    """
    parsed = urlparse(mcp_url)
    path_parts = parsed.path.strip('/').split('/')

    try:
        server_index = path_parts.index('server')
        server_id = path_parts[server_index + 1]
    except (ValueError, IndexError):
        raise ValueError(f"Could not extract server ID from URL: {mcp_url}")

    new_path = f"/composio/server/{server_id}/sse"
    new_query = "useComposioHelperActions=true"
    
    new_parsed = parsed._replace(path=new_path, query=new_query)
    return urlunparse(new_parsed)


# Example usage
if __name__ == "__main__":

    # create integration
    api_key = "s2zgl4aybxoir6hv1hj8a"
    integration_name = "gmail_VZ1j"
    result = create_gmail_integration(api_key, integration_name)

    # get nanoid from uuid
    uuid = result["integrationId"]
    nanoid = get_nanoid_from_uuid(uuid, api_key)
    value = nanoid['nanoid']

    # initiate connection
    result1 = initiate_composio_connection(api_key, result["integrationId"])
    auth_url = result1['redirectUrl']
    print(auth_url)
    
    # create mcp server
    mcp_url = create_mcp_server(
        api_key="s2zgl4aybxoir6hv1hj8a",
        name=generate_random_name(),
        auth_config_ids=[value],
        ttl="no expiration"
    )
    print(mcp_url)
    sse_url = to_standard_sse_url(mcp_url)
    print(sse_url)
    
