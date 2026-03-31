# OCM MCP Server

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![UV](https://img.shields.io/badge/package%20manager-uv-blue)](https://docs.astral.sh/uv/)

A Model Context Protocol (MCP) server for Red Hat OpenShift Cluster Manager (OCM) API operations. Provides 30 read-only tools for cluster management, monitoring, account operations, and infrastructure inspection. Supports both HCP (Hosted Control Plane) and Classic clusters with automatic type detection.

## Installation

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd mcp-ocm
   uv sync
   ```

2. **Environment Configuration**
   Create a `.env` file with your Red Hat API credentials:
   ```bash
   # Required: Your Red Hat API offline token
   RH_API_OFFLINE_TOKEN=your_offline_token_here

   # Optional: OCM API base URL (defaults to https://api.openshift.com)
   OCM_BASE_URL=https://api.openshift.com
   ```

   Get your offline token from [Red Hat API Tokens](https://access.redhat.com/management/api).

## Usage

### MCP Client Configuration

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
        "RH_API_OFFLINE_TOKEN": "your_actual_offline_token_here"
      }
    }
  }
}
```

## Tools Reference (30 tools)

### Cluster Info & Search
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster` | Cluster details with HCP/Classic detection |
| `ocm_search_clusters` | Search clusters by name, state, region, etc. (OCM search syntax) |
| `ocm_get_cluster_status` | Cluster status (DNS readiness, provisioning state, health) |
| `ocm_get_cluster_resources` | Currently available cluster resources (CPU, memory) |

### Pools & Nodes
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_machine_pools` | Machine pools (Classic) or node pools (HCP) — auto-detected |

### Logs
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_service_logs` | Service logs with pagination (page/size params) |
| `ocm_get_cluster_install_logs` | Installation logs and history |
| `ocm_get_cluster_uninstall_logs` | Uninstall logs |

### Monitoring & Metrics
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_alerts` | Cluster alerts with severity breakdown |
| `ocm_get_cluster_operators` | Operator status with condition summaries |
| `ocm_get_cluster_cpu_metrics` | CPU metrics by node role and OS |
| `ocm_get_cluster_socket_metrics` | Socket metrics by node role and OS |
| `ocm_get_cluster_node_metrics` | Node metrics |

### Networking
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_vpc` | VPC info with subnet analysis (public/private) |
| `ocm_get_cluster_ingress` | Ingress configuration and DNS info |
| `ocm_get_cluster_private_link` | AWS Private Link configuration |

### Auth & Access
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_identity_providers` | Identity provider configuration |
| `ocm_get_cluster_groups` | RBAC groups and their users |

### Configuration
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_addons` | Installed add-ons |
| `ocm_get_cluster_autoscaler` | Cluster autoscaler configuration |
| `ocm_get_cluster_kubelet_configs` | Kubelet configurations |
| `ocm_get_cluster_upgrade_policies` | Upgrade policies (Classic + HCP control plane + node pool) |

### Support & Diagnostics
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_limited_support_reasons` | Limited support reasons |
| `ocm_get_cluster_inflight_checks` | Inflight checks (provisioning debugging) |

### AWS / Infrastructure
| Tool | Purpose |
|------|---------|
| `ocm_get_cluster_sts_operator_roles` | STS operator IAM roles |
| `ocm_get_cluster_provision_shard` | Provision shard info |

### Accounts API
| Tool | Purpose |
|------|---------|
| `ocm_get_accounts_by_email` | Account lookup by email |
| `ocm_get_subscription` | Subscription details |
| `ocm_get_organization` | Organization details |
| `ocm_get_current_account` | Currently authenticated user info |

## API Coverage

### Clusters Management API (`clusters_mgmt/v1`)
- Cluster search, details, status, resources
- Machine pools / node pools
- Upgrade policies (cluster, control plane, node pool)
- VPC, ingresses, identity providers
- Alerts, operators, CPU/socket/node metrics
- Addons, autoscaler, kubelet configs, groups
- Limited support reasons, inflight checks
- AWS Private Link, STS operator roles, provision shard
- Install/uninstall logs

### Service Logs API (`service_logs/v1`)
- Cluster service logs with pagination

### Accounts Management API (`accounts_mgmt/v1`)
- Account search by email
- Subscriptions, organizations
- Current account

## Dependencies

- **httpx** — Async HTTP client
- **mcp[cli]** — Model Context Protocol framework
- **python-dotenv** — Environment variable management

## License

This project is licensed under the MIT License.
