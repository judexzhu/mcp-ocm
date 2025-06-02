from __future__ import annotations

import os
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
    
    async def get_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster details by cluster ID"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_machine_pools(self, cluster_id: str, is_hcp: bool) -> Dict[str, Any]:
        """Get cluster machine pools (Classic) or node pools (HCP)"""
        if not self.access_token:
            await self.get_access_token()
            
        # Choose endpoint based on cluster type
        endpoint = "node_pools" if is_hcp else "machine_pools"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/{endpoint}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_service_logs(self, external_id: str) -> Dict[str, Any]:
        """Get cluster service logs using external_id"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/service_logs/v1/clusters/{external_id}/cluster_logs",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_identity_providers(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster identity providers"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/identity_providers",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_ingress(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster ingress configuration"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/ingresses",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_limited_support_reasons(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster limited support reasons"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/limited_support_reasons",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_install_logs(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster install logs"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/logs/install",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_alerts(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster alerts"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/alerts",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_operators(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster operators status"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/metric_queries/cluster_operators",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_upgrade_policies(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster upgrade policies (Classic clusters)"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/upgrade_policies",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_control_plane_upgrade_policies(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster control plane upgrade policies (HCP clusters)"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/control_plane/upgrade_policies",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_node_pool_upgrade_policies(self, cluster_id: str, node_pool_id: str) -> Dict[str, Any]:
        """Get node pool upgrade policies (HCP clusters)"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/node_pools/{node_pool_id}/upgrade_policies",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_cluster_vpc(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster VPC information"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clusters_mgmt/v1/clusters/{cluster_id}/vpc",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

    async def get_accounts_by_email(self, email: str) -> Dict[str, Any]:
        """Search for accounts by email address"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/accounts_mgmt/v1/accounts",
                params={"search": f"email = '{email}'"},
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

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
async def ocm_get_cluster_service_logs(cluster_id: str) -> Dict[str, Any]:
    """
    Get cluster service logs using external_id from cluster data
    
    Args:
        cluster_id: The cluster ID to retrieve service logs for
    
    Returns:
        Dictionary containing:
        - cluster_info: Basic cluster information
        - logs: List of service log entries
        - total_logs: Total number of log entries
    """
    try:
        # First get cluster info to get external_id
        cluster_data = await rhapi.get_cluster(cluster_id)
        external_id = cluster_data.get("external_id")
        
        if not external_id:
            return {"error": "Cluster external_id not found"}
        
        # Get service logs using external_id
        logs_data = await rhapi.get_cluster_service_logs(external_id)
        
        return {
            "cluster_info": {
                "id": cluster_data.get("id"),
                "external_id": external_id,
                "name": cluster_data.get("name"),
                "state": cluster_data.get("state")
            },
            "logs": logs_data.get("items", []),
            "total_logs": logs_data.get("total", 0)
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

if __name__ == "__main__":
    mcp.run(transport="stdio")
