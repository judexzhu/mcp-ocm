from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional
import asyncio

import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("OCM MCP Server")

class RedHatAPI:
    """Red Hat API client for OCM operations"""
    
    def __init__(self):
        self.offline_token = os.getenv("RH_API_OFFLINE_TOKEN")
        self.base_url = os.getenv("OCM_BASE_URL", "https://api.openshift.com")
        self.sso_url = "https://sso.redhat.com"
        self.access_token: Optional[str] = None
        
    async def get_access_token(self) -> str:
        """Get access token using offline token"""
        if not self.offline_token:
            raise ValueError("RH_API_OFFLINE_TOKEN environment variable not set")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.sso_url}/auth/realms/redhat-external/protocol/openid-connect/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": "rhsm-api", 
                    "refresh_token": self.offline_token
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return self.access_token
    
    async def resolve_cluster_id(self, cluster_id: str) -> str:
        """Resolve a cluster identifier to an internal OCM cluster ID.
        Accepts either an internal ID or an external ID (UUID format) and returns the internal ID."""
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE
        )
        if not uuid_pattern.match(cluster_id):
            return cluster_id

        if not self.access_token:
            await self.get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters",
                params={"search": f"external_id = '{cluster_id}'"},
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if not items:
                raise ValueError(f"No cluster found with external_id '{cluster_id}'")
            return items[0]["id"]

    async def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generic authenticated GET request with automatic token refresh on 401"""
        if not self.access_token:
            await self.get_access_token()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            if response.status_code == 401:
                await self.get_access_token()
                response = await client.get(
                    f"{self.base_url}{path}",
                    params=params,
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
            response.raise_for_status()
            return response.json()

    async def search_clusters(self, search: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        params = {"search": search, "page": str(page), "size": str(size)}
        return await self._get("/api/clusters_mgmt/v1/clusters", params=params)

    async def get_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster details by cluster ID (accepts internal or external ID)"""
        cluster_id = await self.resolve_cluster_id(cluster_id)
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}")

    async def get_cluster_machine_pools(self, cluster_id: str, is_hcp: bool) -> Dict[str, Any]:
        endpoint = "node_pools" if is_hcp else "machine_pools"
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/{endpoint}")

    async def get_cluster_service_logs(self, external_id: str, page: int = 1, size: int = 50) -> Dict[str, Any]:
        return await self._get(
            f"/api/service_logs/v1/clusters/{external_id}/cluster_logs",
            params={"page": str(page), "size": str(size)}
        )

    async def get_cluster_identity_providers(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/identity_providers")

    async def get_cluster_ingress(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/ingresses")

    async def get_cluster_limited_support_reasons(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/limited_support_reasons")

    async def get_cluster_install_logs(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/logs/install")

    async def get_cluster_alerts(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/alerts")

    async def get_cluster_operators(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/cluster_operators")

    async def get_cluster_upgrade_policies(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/upgrade_policies")

    async def get_cluster_control_plane_upgrade_policies(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/control_plane/upgrade_policies")

    async def get_node_pool_upgrade_policies(self, cluster_id: str, node_pool_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/node_pools/{node_pool_id}/upgrade_policies")

    async def get_cluster_vpc(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/vpc")

    async def get_accounts_by_email(self, email: str) -> Dict[str, Any]:
        return await self._get("/api/accounts_mgmt/v1/accounts", params={"search": f"email = '{email}'"})

    async def get_cluster_status(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/status")

    async def get_cluster_resources_live(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/resources/live")

    async def get_cluster_uninstall_logs(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/logs/uninstall")

    async def get_cluster_inflight_checks(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/inflight_checks")


    async def get_cluster_cpu_metrics(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/cpu_total_by_node_roles_os")

    async def get_cluster_socket_metrics(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/socket_total_by_node_roles_os")

    async def get_cluster_node_metrics(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/nodes")

    async def get_cluster_addons(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/addons")

    async def get_cluster_autoscaler(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/autoscaler")

    async def get_cluster_groups(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/groups")

    async def get_cluster_group_users(self, cluster_id: str, group_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/groups/{group_id}/users")


    async def get_cluster_kubelet_configs(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/kubelet_configs")

    async def get_cluster_private_link_config(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/aws/private_link_configuration")

    async def get_cluster_sts_operator_roles(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/sts_operator_roles")

    async def get_cluster_provision_shard(self, cluster_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/clusters_mgmt/v1/clusters/{cluster_id}/provision_shard")

    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/accounts_mgmt/v1/subscriptions/{subscription_id}")

    async def get_organization(self, org_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/accounts_mgmt/v1/organizations/{org_id}")

    async def get_current_account(self) -> Dict[str, Any]:
        return await self._get("/api/accounts_mgmt/v1/current_account")

# Initialize API client
rhapi = RedHatAPI()

@mcp.tool()
async def ocm_get_cluster(cluster_id: str) -> Dict[str, Any]:
    """
    Get OpenShift cluster details from OCM API
    
    Args:
        cluster_id: The cluster ID to retrieve details for
    
    Returns:
        Dictionary containing cluster details including:
        - id: Cluster ID
        - external_id: External cluster ID  
        - name: Cluster name
        - state: Cluster state
        - hypershift: HCP configuration (enabled: true/false)
        - And other cluster metadata
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data = await rhapi.get_cluster(cluster_id)

        # Add cluster type determination
        is_hcp = cluster_data.get("hypershift", {}).get("enabled", False)
        cluster_data["cluster_type"] = "HCP" if is_hcp else "Classic"
        
        return cluster_data
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_search_clusters(search: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
    """
    Search for clusters using OCM search syntax.

    Args:
        search: OCM search query (e.g. "name like 'my-cluster%'", "state = 'ready'",
                "cloud_provider.id = 'aws' and region.id = 'us-east-1'")
        page: Page number (default 1)
        size: Results per page (default 10, max 100)

    Returns:
        Dictionary containing:
        - clusters: List of matching clusters (id, name, state, cloud_provider, region, version, cluster_type)
        - total: Total number of matching clusters
        - page/size: Pagination info
    """
    try:
        data = await rhapi.search_clusters(search, page, size)
        clusters = []
        for c in data.get("items", []):
            is_hcp = c.get("hypershift", {}).get("enabled", False)
            clusters.append({
                "id": c.get("id"),
                "external_id": c.get("external_id"),
                "name": c.get("name"),
                "state": c.get("state"),
                "cloud_provider": c.get("cloud_provider", {}).get("id"),
                "region": c.get("region", {}).get("id"),
                "version": c.get("openshift_version"),
                "cluster_type": "HCP" if is_hcp else "Classic",
                "product": c.get("product", {}).get("id"),
            })
        return {
            "clusters": clusters,
            "total": data.get("total", 0),
            "page": page,
            "size": size
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_machine_pools(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster machine pools (Classic) or node pools (HCP) automatically based on cluster type
    
    Args:
        cluster_id: The cluster ID to retrieve pools for
    
    Returns:
        Dictionary containing:
        - cluster_type: "HCP" or "Classic" 
        - pool_type: "node_pools" or "machine_pools"
        - pools: List of pools data
        - cluster_info: Basic cluster information
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # First get cluster info to determine type
        cluster_data = await rhapi.get_cluster(cluster_id)
        is_hcp = cluster_data.get("hypershift", {}).get("enabled", False)
        cluster_type = "HCP" if is_hcp else "Classic"
        pool_type = "node_pools" if is_hcp else "machine_pools"
        
        # Get the appropriate pools
        pools_data = await rhapi.get_cluster_machine_pools(cluster_id, is_hcp)
        
        return {
            "cluster_type": cluster_type,
            "pool_type": pool_type,
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "pools": pools_data.get("items", []),
            "total_pools": pools_data.get("total", 0)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_service_logs(cluster_id: str, page: int = 1, size: int = 50) -> Dict[str, Any]:
    """
    Get cluster service logs using external_id from cluster data

    Args:
        cluster_id: The cluster ID to retrieve service logs for (internal or external UUID)
        page: Page number (default 1)
        size: Results per page (default 50)

    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - logs: List of service log entries
        - total_logs: Total number of log entries
        - page/size: Pagination info
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # First get cluster info to get external_id
        cluster_data = await rhapi.get_cluster(cluster_id)
        external_id = cluster_data.get("external_id")

        if not external_id:
            return {"error": "Cluster external_id not found"}

        # Get service logs using external_id (UUID)
        logs_data = await rhapi.get_cluster_service_logs(external_id, page, size)

        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": external_id,
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "logs": logs_data.get("items", []),
            "total_logs": logs_data.get("total", 0),
            "page": page,
            "size": size
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or service logs not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_identity_providers(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster identity providers configuration
    
    Args:
        cluster_id: The cluster ID to retrieve identity providers for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - identity_providers: List of identity provider configurations
        - total_providers: Total number of identity providers
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and identity providers in parallel
        cluster_data, idp_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_identity_providers(cluster_id)
        )
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "identity_providers": idp_data.get("items", []),
            "total_providers": idp_data.get("total", 0)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or identity providers not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_ingress(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster ingress configuration
    
    Args:
        cluster_id: The cluster ID to retrieve ingress configuration for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - ingress: List of ingress configurations
        - total_ingress: Total number of ingress configurations
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and ingress config in parallel
        cluster_data, ingress_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_ingress(cluster_id)
        )
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "ingress": ingress_data.get("items", []),
            "total_ingress": ingress_data.get("total", 0)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or ingress configuration not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_limited_support_reasons(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster limited support reasons
    
    Args:
        cluster_id: The cluster ID to retrieve limited support reasons for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - limited_support_reasons: List of reasons why cluster has limited support
        - total_reasons: Total number of limited support reasons
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and limited support reasons in parallel
        cluster_data, reasons_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_limited_support_reasons(cluster_id)
        )
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "limited_support_reasons": reasons_data.get("items", []),
            "total_reasons": reasons_data.get("total", 0)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or limited support reasons not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_install_logs(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster install logs
    
    Args:
        cluster_id: The cluster ID to retrieve install logs for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - install_logs: Install log data
        - log_content: Raw log content if available
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and install logs in parallel
        cluster_data, logs_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_install_logs(cluster_id)
        )
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "install_logs": logs_data.get("content", ""),
            "log_size": len(logs_data.get("content", "")),
            "has_logs": bool(logs_data.get("content"))
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or install logs not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_alerts(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster alerts
    
    Args:
        cluster_id: The cluster ID to retrieve alerts for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - alerts: List of alerts
        - total_alerts: Total number of alerts
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and alerts in parallel
        cluster_data, alerts_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_alerts(cluster_id)
        )
        
        alerts_list = alerts_data.get("alerts", [])
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "alerts": alerts_list,
            "total_alerts": len(alerts_list)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or alerts not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_operators(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster operators status
    
    Args:
        cluster_id: The cluster ID to retrieve operators status for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - operators: List of operators (each has 'time', 'name', 'condition', 'reason', 'version' fields)
        - total_operators: Total number of operators
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and operators in parallel
        cluster_data, operators_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_operators(cluster_id)
        )
        
        operators_list = operators_data.get("operators", [])
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "operators": operators_list,
            "total_operators": len(operators_list)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or operators not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_upgrade_policies(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster upgrade policies (handles both Classic and HCP clusters)
    
    Args:
        cluster_id: The cluster ID to retrieve upgrade policies for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information including cluster type
        - upgrade_policies: For Classic clusters, or control_plane_policies for HCP
        - node_pool_policies: For HCP clusters only - policies for each node pool
        - total_policies: Total number of upgrade policies found
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # First get cluster info to determine type
        cluster_data = await rhapi.get_cluster(cluster_id)
        is_hcp = cluster_data.get("hypershift", {}).get("enabled", False)
        cluster_type = "HCP" if is_hcp else "Classic"

        result = {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state"),
                "cluster_type": cluster_type
            }
        }
        
        if is_hcp:
            # For HCP clusters, get control plane policies and node pool policies
            control_plane_policies_data, node_pools_data = await asyncio.gather(
                rhapi.get_cluster_control_plane_upgrade_policies(cluster_id),
                rhapi.get_cluster_machine_pools(cluster_id, is_hcp)
            )
            
            result["control_plane_policies"] = control_plane_policies_data.get("items", [])
            result["total_control_plane_policies"] = control_plane_policies_data.get("total", 0)
            
            # Get upgrade policies for each node pool
            node_pools = node_pools_data.get("items", [])
            node_pool_policies = {}
            
            if node_pools:
                # Get policies for all node pools in parallel
                node_pool_tasks = []
                for pool in node_pools:
                    pool_id = pool.get("id")
                    if pool_id:
                        task = rhapi.get_node_pool_upgrade_policies(cluster_id, pool_id)
                        node_pool_tasks.append((pool_id, task))
                
                if node_pool_tasks:
                    # Execute all node pool policy requests in parallel
                    node_pool_results = await asyncio.gather(
                        *[task for _, task in node_pool_tasks],
                        return_exceptions=True
                    )
                    
                    # Process results
                    for i, (pool_id, _) in enumerate(node_pool_tasks):
                        policies_result = node_pool_results[i]
                        if isinstance(policies_result, Exception):
                            node_pool_policies[pool_id] = {"error": str(policies_result)}
                        else:
                            node_pool_policies[pool_id] = {
                                "policies": policies_result.get("items", []),
                                "total": policies_result.get("total", 0)
                            }
            
            result["node_pool_policies"] = node_pool_policies
            result["total_node_pools"] = len(node_pools)
            
            # Calculate total policies
            total_policies = result["total_control_plane_policies"]
            for pool_policies in node_pool_policies.values():
                if "total" in pool_policies:
                    total_policies += pool_policies["total"]
            result["total_policies"] = total_policies
            
        else:
            # For Classic clusters, get cluster upgrade policies
            upgrade_policies_data = await rhapi.get_cluster_upgrade_policies(cluster_id)
            result["upgrade_policies"] = upgrade_policies_data.get("items", [])
            result["total_policies"] = upgrade_policies_data.get("total", 0)
        
        return result
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or upgrade policies not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_vpc(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster VPC information
    
    Args:
        cluster_id: The cluster ID to retrieve VPC information for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - vpc: VPC information including id, name, cidr_block, red_hat_managed
        - aws_subnets: List of AWS subnets with details
        - total_subnets: Total number of subnets
        - subnet_summary: Summary of public vs private subnets
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        # Get cluster info and VPC info in parallel
        cluster_data, vpc_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_vpc(cluster_id)
        )
        
        aws_subnets = vpc_data.get("aws_subnets", [])
        
        # Analyze subnets
        subnet_summary = {"public": 0, "private": 0}
        for subnet in aws_subnets:
            if subnet.get("public", False):
                subnet_summary["public"] += 1
            else:
                subnet_summary["private"] += 1
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "vpc": {
                "id": vpc_data.get("id"),
                "name": vpc_data.get("name"),
                "cidr_block": vpc_data.get("cidr_block"),
                "red_hat_managed": vpc_data.get("red_hat_managed", False)
            },
            "aws_subnets": aws_subnets,
            "total_subnets": len(aws_subnets),
            "subnet_summary": subnet_summary
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or VPC information not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_accounts_by_email(email: str) -> Dict[str, Any]:
    """
    Search for Red Hat accounts by email address
    
    Args:
        email: The email address to search for
    
    Returns:
        Dictionary containing:
        - accounts: List of matching accounts
        - total_accounts: Total number of accounts found
        - search_email: The email address that was searched
    """
    try:
        accounts_data = await rhapi.get_accounts_by_email(email)
        
        accounts_list = accounts_data.get("items", [])
        
        return {
            "search_email": email,
            "accounts": accounts_list,
            "total_accounts": accounts_data.get("total", 0)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"No accounts found for email '{email}'"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def ocm_get_cluster_status(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster status (DNS readiness, provisioning state, health)

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, status_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_status(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "status": status_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_resources(cluster_id: str) -> Dict[str, Any]:
    """
    Get currently available cluster resources (CPU, memory)

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, resources_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_resources_live(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "resources": resources_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_uninstall_logs(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster uninstall logs

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, logs_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_uninstall_logs(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "uninstall_logs": logs_data.get("content", ""),
            "log_size": len(logs_data.get("content", "")),
            "has_logs": bool(logs_data.get("content"))
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or uninstall logs not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_inflight_checks(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster inflight checks (useful for debugging provisioning issues)

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, checks_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_inflight_checks(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "inflight_checks": checks_data.get("items", []),
            "total_checks": checks_data.get("total", 0)
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_cpu_metrics(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster CPU metrics broken down by node roles and OS

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, metrics_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_cpu_metrics(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "cpu_metrics": metrics_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_socket_metrics(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster socket metrics broken down by node roles and OS

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, metrics_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_socket_metrics(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "socket_metrics": metrics_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_node_metrics(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster node metrics

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, metrics_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_node_metrics(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "node_metrics": metrics_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_addons(cluster_id: str) -> Dict[str, Any]:
    """
    Get installed add-ons for a cluster

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, addons_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_addons(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "addons": addons_data.get("items", []),
            "total_addons": addons_data.get("total", 0)
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_autoscaler(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster autoscaler configuration

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, autoscaler_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_autoscaler(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "autoscaler": autoscaler_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or autoscaler not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_groups(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster RBAC groups and their users

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, groups_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_groups(cluster_id)
        )

        groups = groups_data.get("items", [])

        # Fetch users for each group in parallel
        if groups:
            user_tasks = []
            for group in groups:
                group_id = group.get("id")
                if group_id:
                    user_tasks.append((group_id, rhapi.get_cluster_group_users(cluster_id, group_id)))

            if user_tasks:
                user_results = await asyncio.gather(
                    *[task for _, task in user_tasks],
                    return_exceptions=True
                )
                for i, (group_id, _) in enumerate(user_tasks):
                    result = user_results[i]
                    if isinstance(result, Exception):
                        for g in groups:
                            if g.get("id") == group_id:
                                g["users"] = {"error": str(result)}
                    else:
                        for g in groups:
                            if g.get("id") == group_id:
                                g["users"] = result.get("items", [])

        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "groups": groups,
            "total_groups": groups_data.get("total", 0)
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_kubelet_configs(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster kubelet configurations

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, kubelet_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_kubelet_configs(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "kubelet_configs": kubelet_data.get("items", []),
            "total_configs": kubelet_data.get("total", 0)
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_private_link(cluster_id: str) -> Dict[str, Any]:
    """
    Get AWS Private Link configuration for a cluster

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, pl_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_private_link_config(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "private_link_configuration": pl_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or Private Link config not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_sts_operator_roles(cluster_id: str) -> Dict[str, Any]:
    """
    Get STS operator IAM roles for a cluster

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, roles_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_sts_operator_roles(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "sts_operator_roles": roles_data.get("items", []),
            "total_roles": roles_data.get("total", 0)
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_cluster_provision_shard(cluster_id: str) -> Dict[str, Any]:
    """
    Get the provision shard that manages a cluster

    Args:
        cluster_id: The cluster ID (internal or external UUID)
    """
    try:
        cluster_id = await rhapi.resolve_cluster_id(cluster_id)
        cluster_data, shard_data = await asyncio.gather(
            rhapi.get_cluster(cluster_id),
            rhapi.get_cluster_provision_shard(cluster_id)
        )
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": cluster_data.get("external_id"),
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "provision_shard": shard_data
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Cluster '{cluster_id}' or provision shard not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Get subscription details by subscription ID

    Args:
        subscription_id: The subscription ID to retrieve
    """
    try:
        subscription_data = await rhapi.get_subscription(subscription_id)
        return {"subscription": subscription_data}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Subscription '{subscription_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_organization(org_id: str) -> Dict[str, Any]:
    """
    Get organization details by organization ID

    Args:
        org_id: The organization ID to retrieve
    """
    try:
        org_data = await rhapi.get_organization(org_id)
        return {"organization": org_data}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Organization '{org_id}' not found"}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def ocm_get_current_account() -> Dict[str, Any]:
    """
    Get the currently authenticated user's account information
    """
    try:
        account_data = await rhapi.get_current_account()
        return {"current_account": account_data}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"error": "Authentication failed - check RH_API_OFFLINE_TOKEN"}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
