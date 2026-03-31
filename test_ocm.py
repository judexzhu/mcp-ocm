#!/usr/bin/env python3
"""
Simple test script for OCM MCP Server
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our MCP tools
from ocm_mcp_server import (
    ocm_get_cluster,
    ocm_get_cluster_machine_pools,
    ocm_get_cluster_service_logs,
    ocm_get_cluster_identity_providers,
    ocm_get_cluster_ingress,
    ocm_get_cluster_limited_support_reasons,
    ocm_get_cluster_install_logs,
    ocm_get_cluster_alerts,
    ocm_get_cluster_operators,
    ocm_get_cluster_upgrade_policies,
    ocm_get_cluster_vpc,
    ocm_get_accounts_by_email,
    ocm_get_cluster_status,
    ocm_get_cluster_resources,
    ocm_get_cluster_uninstall_logs,
    ocm_get_cluster_inflight_checks,
    ocm_get_cluster_cpu_metrics,
    ocm_get_cluster_socket_metrics,
    ocm_get_cluster_node_metrics,
    ocm_get_cluster_addons,
    ocm_get_cluster_autoscaler,
    ocm_get_cluster_groups,
    ocm_get_cluster_kubelet_configs,
    ocm_get_cluster_private_link,
    ocm_get_cluster_sts_operator_roles,
    ocm_get_cluster_provision_shard,
    ocm_get_subscription,
    ocm_get_organization,
    ocm_get_current_account,
)


async def run_test(name: str, coro):
    """Run a single test and print result"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    try:
        result = await coro
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            # Print top-level keys and summary
            for key, value in result.items():
                if isinstance(value, list):
                    print(f"  {key}: [{len(value)} items]")
                elif isinstance(value, dict):
                    print(f"  {key}: {{{', '.join(value.keys())}}}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        return result
    except Exception as e:
        print(f"  Exception: {e}")
        return {"error": str(e)}


async def test_tools():
    """Test all OCM MCP tools"""

    # Replace with actual values for testing
    cluster_id = "your_cluster_id_here"
    test_email = "your-email@example.com"

    print("Testing OCM MCP Tools")
    print(f"Cluster ID: {cluster_id}")
    print(f"Total tools: 31")

    # --- Cluster info ---
    cluster_result = await run_test("ocm_get_cluster", ocm_get_cluster(cluster_id))
    if "error" in cluster_result:
        print("\nCluster not found, skipping cluster-dependent tests.")
        return

    # --- Original tools ---
    await run_test("ocm_get_cluster_machine_pools", ocm_get_cluster_machine_pools(cluster_id))
    await run_test("ocm_get_cluster_service_logs", ocm_get_cluster_service_logs(cluster_id))
    await run_test("ocm_get_cluster_identity_providers", ocm_get_cluster_identity_providers(cluster_id))
    await run_test("ocm_get_cluster_ingress", ocm_get_cluster_ingress(cluster_id))
    await run_test("ocm_get_cluster_limited_support_reasons", ocm_get_cluster_limited_support_reasons(cluster_id))
    await run_test("ocm_get_cluster_install_logs", ocm_get_cluster_install_logs(cluster_id))
    await run_test("ocm_get_cluster_alerts", ocm_get_cluster_alerts(cluster_id))
    await run_test("ocm_get_cluster_operators", ocm_get_cluster_operators(cluster_id))
    await run_test("ocm_get_cluster_upgrade_policies", ocm_get_cluster_upgrade_policies(cluster_id))
    await run_test("ocm_get_cluster_vpc", ocm_get_cluster_vpc(cluster_id))

    # --- New tools: Cluster diagnostics ---
    await run_test("ocm_get_cluster_status", ocm_get_cluster_status(cluster_id))
    await run_test("ocm_get_cluster_resources", ocm_get_cluster_resources(cluster_id))
    await run_test("ocm_get_cluster_uninstall_logs", ocm_get_cluster_uninstall_logs(cluster_id))
    await run_test("ocm_get_cluster_inflight_checks", ocm_get_cluster_inflight_checks(cluster_id))
    # --- New tools: Metrics ---
    await run_test("ocm_get_cluster_cpu_metrics", ocm_get_cluster_cpu_metrics(cluster_id))
    await run_test("ocm_get_cluster_socket_metrics", ocm_get_cluster_socket_metrics(cluster_id))
    await run_test("ocm_get_cluster_node_metrics", ocm_get_cluster_node_metrics(cluster_id))

    # --- New tools: Configuration ---
    await run_test("ocm_get_cluster_addons", ocm_get_cluster_addons(cluster_id))
    await run_test("ocm_get_cluster_autoscaler", ocm_get_cluster_autoscaler(cluster_id))
    await run_test("ocm_get_cluster_groups", ocm_get_cluster_groups(cluster_id))
await run_test("ocm_get_cluster_kubelet_configs", ocm_get_cluster_kubelet_configs(cluster_id))

    # --- New tools: AWS-specific ---
    await run_test("ocm_get_cluster_private_link", ocm_get_cluster_private_link(cluster_id))
    await run_test("ocm_get_cluster_sts_operator_roles", ocm_get_cluster_sts_operator_roles(cluster_id))
    await run_test("ocm_get_cluster_provision_shard", ocm_get_cluster_provision_shard(cluster_id))

    # --- New tools: Accounts API ---
    # Get subscription_id and org_id from cluster data if available
    subscription = cluster_result.get("subscription", {})
    subscription_id = subscription.get("id") if isinstance(subscription, dict) else None
    organization = cluster_result.get("organization", {})
    org_id = organization.get("id") if isinstance(organization, dict) else None

    if subscription_id:
        await run_test("ocm_get_subscription", ocm_get_subscription(subscription_id))
    else:
        print("\n  Skipping ocm_get_subscription (no subscription_id in cluster data)")

    if org_id:
        await run_test("ocm_get_organization", ocm_get_organization(org_id))
    else:
        print("\n  Skipping ocm_get_organization (no org_id in cluster data)")

    await run_test("ocm_get_current_account", ocm_get_current_account())
    await run_test("ocm_get_accounts_by_email", ocm_get_accounts_by_email(test_email))

    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    if not os.getenv("RH_API_OFFLINE_TOKEN"):
        print("Please set RH_API_OFFLINE_TOKEN environment variable")
        exit(1)

    asyncio.run(test_tools())
