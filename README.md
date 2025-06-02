# OCM MCP Server

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![UV](https://img.shields.io/badge/package%20manager-uv-blue)](https://docs.astral.sh/uv/)

A comprehensive Model Control Protocol (MCP) server for Red Hat OpenShift Cluster Manager (OCM) API operations. This server provides 12 intelligent tools for cluster management, account operations, and infrastructure monitoring.

## Features(Keep Adding)

- **`ocm_get_cluster`** - Get detailed cluster information with automatic HCP/Classic detection
- **`ocm_get_cluster_machine_pools`** - Smart pool management (automatically selects node_pools for HCP, machine_pools for Classic)
- **`ocm_get_cluster_upgrade_policies`** - Intelligent upgrade policy management for both cluster types

- **`ocm_get_cluster_service_logs`** - Service logs using dynamic external_id resolution
- **`ocm_get_cluster_alerts`** - Cluster alerts with severity breakdown
- **`ocm_get_cluster_operators`** - Operator status monitoring with condition summaries
- **`ocm_get_cluster_install_logs`** - Installation logs and history

- **`ocm_get_cluster_vpc`** - VPC information with subnet analysis (public/private breakdown)
- **`ocm_get_cluster_ingress`** - Ingress configuration and DNS information
- **`ocm_get_cluster_identity_providers`** - Authentication provider configuration

- **`ocm_get_cluster_limited_support_reasons`** - Support status and restrictions
- **`ocm_get_accounts_by_email`** - Account management and user lookup

## Installation

### Prerequisites
- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd mcp-ocm
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Environment Configuration**
   Create a `.env` file with your Red Hat API credentials:
   ```bash
   # Required: Your Red Hat API offline token
   RH_API_OFFLINE_TOKEN=your_offline_token_here
   
   # Optional: OCM API base URL (defaults to https://api.openshift.com)
   OCM_BASE_URL=https://api.openshift.com
   ```

   **Getting your offline token:**
   1. Visit [Red Hat API Tokens](https://access.redhat.com/management/api)
   2. Generate or copy your offline token
   3. Add it to your `.env` file


## Usage

### Running the MCP Server
```json
{
  "mcpServers": {
    "ocm": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/mcp-ocm",
        "run",
        "ocm_mcp_server.py"
      ],
      "env": {
        "RH_API_OFFLINE_TOKEN": "your_actual_offline_token_here",
        "OCM_BASE_URL": "https://api.openshift.com"
      }
    }
  }
}
```

## Tools Reference

| Tool | Purpose | Cluster Types | Key Features |
|------|---------|---------------|--------------|
| `ocm_get_cluster` | Basic cluster info | All | HCP/Classic detection |
| `ocm_get_cluster_machine_pools` | Pool management | All | Smart endpoint selection |
| `ocm_get_cluster_service_logs` | Service logs | All | Dynamic external_id resolution |
| `ocm_get_cluster_identity_providers` | Auth config | All | Provider type analysis |
| `ocm_get_cluster_ingress` | Ingress config | All | DNS and routing info |
| `ocm_get_cluster_limited_support_reasons` | Support status | All | Restriction analysis |
| `ocm_get_cluster_install_logs` | Install history | All | Log size and content |
| `ocm_get_cluster_alerts` | Alert monitoring | All | Severity breakdown |
| `ocm_get_cluster_operators` | Operator status | All | Condition summaries |
| `ocm_get_cluster_upgrade_policies` | Upgrade management | All | Multi-endpoint handling |
| `ocm_get_cluster_vpc` | Network info | All | Subnet analysis |
| `ocm_get_accounts_by_email` | Account lookup | N/A | User management |

## API Coverage

### Cluster Management API
- `/api/clusters_mgmt/v1/clusters/{id}`
- `/api/clusters_mgmt/v1/clusters/{id}/machine_pools`
- `/api/clusters_mgmt/v1/clusters/{id}/node_pools`
- `/api/clusters_mgmt/v1/clusters/{id}/upgrade_policies`
- `/api/clusters_mgmt/v1/clusters/{id}/control_plane/upgrade_policies`
- `/api/clusters_mgmt/v1/clusters/{id}/node_pools/{pool_id}/upgrade_policies`

### Service Logs API
- `/api/service_logs/v1/clusters/{external_id}/cluster_logs`

### Infrastructure APIs
- `/api/clusters_mgmt/v1/clusters/{id}/vpc`
- `/api/clusters_mgmt/v1/clusters/{id}/ingresses`
- `/api/clusters_mgmt/v1/clusters/{id}/identity_providers`

### Monitoring APIs
- `/api/clusters_mgmt/v1/clusters/{id}/metric_queries/alerts`
- `/api/clusters_mgmt/v1/clusters/{id}/metric_queries/cluster_operators`

### Account Management API
- `/api/accounts_mgmt/v1/accounts?search=email='...`

## Dependencies

- **httpx**: Async HTTP client
- **mcp**: Model Control Protocol framework
- **python-dotenv**: Environment variable management
- **asyncio**: Async/await support

## License

This project is licensed under the MIT License.
