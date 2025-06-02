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
    ocm_get_accounts_by_email
)

async def test_tools():
    """Test the OCM MCP tools"""
    
    # Test cluster ID from your REST API file
    cluster_id = "your_cluster_id_here"  # Replace with actual cluster ID
    
    print("🧪 Testing OCM MCP Tools")
    print("=" * 50)
    
    # Test ocm_get_cluster
    print(f"\n📊 Testing ocm_get_cluster with ID: {cluster_id}")
    cluster_result = await ocm_get_cluster(cluster_id)
    
    if "error" in cluster_result:
        print(f"❌ Error: {cluster_result['error']}")
        return
    
    print(f"✅ Cluster found: {cluster_result.get('name', 'Unknown')}")
    print(f"   Type: {cluster_result.get('cluster_type', 'Unknown')}")
    print(f"   State: {cluster_result.get('state', 'Unknown')}")
    print(f"   External ID: {cluster_result.get('external_id', 'Unknown')}")
    
    # Test ocm_get_cluster_machine_pools
    print(f"\n🔧 Testing ocm_get_cluster_machine_pools")
    pools_result = await ocm_get_cluster_machine_pools(cluster_id)
    
    if "error" in pools_result:
        print(f"❌ Error: {pools_result['error']}")
    else:
        print(f"✅ Pools retrieved successfully")
        print(f"   Cluster Type: {pools_result.get('cluster_type', 'Unknown')}")
        print(f"   Pool Type: {pools_result.get('pool_type', 'Unknown')}")
        print(f"   Total Pools: {pools_result.get('total_pools', 0)}")
        
        # Show first pool if exists
        pools = pools_result.get('pools', [])
        if pools:
            first_pool = pools[0]
            print(f"   First Pool ID: {first_pool.get('id', 'Unknown')}")

    # Test ocm_get_cluster_service_logs
    print(f"\n📋 Testing ocm_get_cluster_service_logs")
    logs_result = await ocm_get_cluster_service_logs(cluster_id)
    
    if "error" in logs_result:
        print(f"❌ Error: {logs_result['error']}")
    else:
        print(f"✅ Service logs retrieved successfully")
        print(f"   Total Logs: {logs_result.get('total_logs', 0)}")
        
        # Show first log if exists
        logs = logs_result.get('logs', [])
        if logs:
            first_log = logs[0]
            print(f"   First Log Severity: {first_log.get('severity', 'Unknown')}")
            print(f"   First Log Summary: {first_log.get('summary', 'Unknown')[:50]}...")
        else:
            print("   No service logs found")

    # Test ocm_get_cluster_identity_providers
    print(f"\n🔐 Testing ocm_get_cluster_identity_providers")
    idp_result = await ocm_get_cluster_identity_providers(cluster_id)
    
    if "error" in idp_result:
        print(f"❌ Error: {idp_result['error']}")
    else:
        print(f"✅ Identity providers retrieved successfully")
        print(f"   Total Providers: {idp_result.get('total_providers', 0)}")
        
        # Show first identity provider if exists
        providers = idp_result.get('identity_providers', [])
        if providers:
            first_provider = providers[0]
            print(f"   First Provider Type: {first_provider.get('type', 'Unknown')}")
            print(f"   First Provider Name: {first_provider.get('name', 'Unknown')}")
        else:
            print("   No identity providers found")

    # Test ocm_get_cluster_ingress
    print(f"\n🌐 Testing ocm_get_cluster_ingress")
    ingress_result = await ocm_get_cluster_ingress(cluster_id)
    
    if "error" in ingress_result:
        print(f"❌ Error: {ingress_result['error']}")
    else:
        print(f"✅ Ingress configuration retrieved successfully")
        print(f"   Total Ingress: {ingress_result.get('total_ingress', 0)}")
        
        # Show first ingress if exists
        ingress_list = ingress_result.get('ingress', [])
        if ingress_list:
            first_ingress = ingress_list[0]
            print(f"   First Ingress ID: {first_ingress.get('id', 'Unknown')}")
            print(f"   Default: {first_ingress.get('default', 'Unknown')}")
            dns_name = first_ingress.get('dns_name', 'Unknown')
            print(f"   DNS Name: {dns_name[:50]}..." if len(dns_name) > 50 else f"   DNS Name: {dns_name}")
        else:
            print("   No ingress configurations found")

    # Test ocm_get_cluster_limited_support_reasons
    print(f"\n⚠️  Testing ocm_get_cluster_limited_support_reasons")
    lsr_result = await ocm_get_cluster_limited_support_reasons(cluster_id)
    
    if "error" in lsr_result:
        print(f"❌ Error: {lsr_result['error']}")
    else:
        print(f"✅ Limited support reasons retrieved successfully")
        print(f"   Total Reasons: {lsr_result.get('total_reasons', 0)}")
        
        # Show first reason if exists
        reasons = lsr_result.get('limited_support_reasons', [])
        if reasons:
            first_reason = reasons[0]
            print(f"   First Reason ID: {first_reason.get('id', 'Unknown')}")
            summary = first_reason.get('summary', 'Unknown')
            print(f"   Summary: {summary[:70]}..." if len(summary) > 70 else f"   Summary: {summary}")
            print(f"   Details: {first_reason.get('details', 'Unknown')[:50]}...")
        else:
            print("   No limited support reasons found (cluster fully supported)")

    # Test ocm_get_cluster_install_logs
    print(f"\n📦 Testing ocm_get_cluster_install_logs")
    install_logs_result = await ocm_get_cluster_install_logs(cluster_id)
    
    if "error" in install_logs_result:
        print(f"❌ Error: {install_logs_result['error']}")
    else:
        print(f"✅ Install logs retrieved successfully")
        print(f"   Has Logs: {install_logs_result.get('has_logs', False)}")
        print(f"   Log Size: {install_logs_result.get('log_size', 0)} characters")
        
        # Show log preview if exists
        install_logs = install_logs_result.get('install_logs', '')
        if install_logs:
            # Show first few lines of logs
            log_lines = install_logs.split('\n')[:3]
            print(f"   Log Preview:")
            for i, line in enumerate(log_lines[:2]):
                if line.strip():
                    print(f"     {line[:80]}..." if len(line) > 80 else f"     {line}")
        else:
            print("   No install logs available (may be completed/purged)")

    # Test ocm_get_cluster_alerts
    print(f"\n🚨 Testing ocm_get_cluster_alerts")
    alerts_result = await ocm_get_cluster_alerts(cluster_id)
    
    if "error" in alerts_result:
        print(f"❌ Error: {alerts_result['error']}")
    else:
        print(f"✅ Cluster alerts retrieved successfully")
        print(f"   Total Alerts: {alerts_result.get('total_alerts', 0)}")
        
        # Show first alert if exists
        alerts = alerts_result.get('alerts', [])
        if alerts:
            first_alert = alerts[0]
            print(f"   First Alert Name: {first_alert.get('name', 'Unknown')}")
            print(f"   Severity: {first_alert.get('severity', 'Unknown')}")
            
            # Show alert summary by severity
            severities = {}
            for alert in alerts:
                severity = alert.get('severity', 'unknown')
                severities[severity] = severities.get(severity, 0) + 1
            
            print(f"   Alert Summary:")
            for severity, count in sorted(severities.items()):
                print(f"     {severity}: {count}")
        else:
            print("   No alerts configured")

    # Test ocm_get_cluster_operators
    print(f"\n⚙️  Testing ocm_get_cluster_operators")
    operators_result = await ocm_get_cluster_operators(cluster_id)
    
    if "error" in operators_result:
        print(f"❌ Error: {operators_result['error']}")
    else:
        print(f"✅ Cluster operators retrieved successfully")
        print(f"   Total Operators: {operators_result.get('total_operators', 0)}")
        
        # Show first operator if exists
        operators = operators_result.get('operators', [])
        if operators:
            first_operator = operators[0]
            print(f"   First Operator Name: {first_operator.get('name', 'Unknown')}")
            print(f"   Condition: {first_operator.get('condition', 'Unknown')}")
            print(f"   Version: {first_operator.get('version', 'Unknown')}")
            print(f"   Reason: {first_operator.get('reason', 'Unknown')}")
            
            # Show operator summary by condition
            conditions = {}
            for operator in operators:
                condition = operator.get('condition', 'unknown')
                conditions[condition] = conditions.get(condition, 0) + 1
            
            print(f"   Operator Summary:")
            for condition, count in sorted(conditions.items()):
                print(f"     {condition}: {count}")
        else:
            print("   No operators found")

    # Test ocm_get_cluster_upgrade_policies
    print(f"\n🔄 Testing ocm_get_cluster_upgrade_policies")
    upgrade_policies_result = await ocm_get_cluster_upgrade_policies(cluster_id)
    
    if "error" in upgrade_policies_result:
        print(f"❌ Error: {upgrade_policies_result['error']}")
    else:
        cluster_info = upgrade_policies_result.get("cluster_info", {})
        cluster_type = cluster_info.get("cluster_type", "Unknown")
        
        print(f"✅ Cluster upgrade policies retrieved successfully")
        print(f"   Cluster Type: {cluster_type}")
        print(f"   Total Policies: {upgrade_policies_result.get('total_policies', 0)}")
        
        if cluster_type == "HCP":
            # HCP cluster - show control plane and node pool policies
            cp_policies = upgrade_policies_result.get("control_plane_policies", [])
            print(f"   Control Plane Policies: {len(cp_policies)}")
            
            if cp_policies:
                first_cp_policy = cp_policies[0]
                print(f"     First CP Policy Version: {first_cp_policy.get('version', 'Unknown')}")
                print(f"     State: {first_cp_policy.get('state', 'Unknown')}")
            
            node_pool_policies = upgrade_policies_result.get("node_pool_policies", {})
            print(f"   Node Pool Policies:")
            for pool_id, pool_data in node_pool_policies.items():
                if "error" in pool_data:
                    print(f"     {pool_id}: Error - {pool_data['error']}")
                else:
                    policies_count = pool_data.get("total", 0)
                    print(f"     {pool_id}: {policies_count} policies")
                    if policies_count > 0:
                        first_policy = pool_data.get("policies", [{}])[0]
                        print(f"       First Policy Version: {first_policy.get('version', 'Unknown')}")
        else:
            # Classic cluster - show upgrade policies
            upgrade_policies = upgrade_policies_result.get("upgrade_policies", [])
            if upgrade_policies:
                first_policy = upgrade_policies[0]
                print(f"   First Policy Version: {first_policy.get('version', 'Unknown')}")
                print(f"   State: {first_policy.get('state', 'Unknown')}")
            else:
                print("   No upgrade policies configured")

    # Test ocm_get_cluster_vpc
    print(f"\n🌐 Testing ocm_get_cluster_vpc")
    vpc_result = await ocm_get_cluster_vpc(cluster_id)
    
    if "error" in vpc_result:
        print(f"❌ Error: {vpc_result['error']}")
    else:
        print(f"✅ Cluster VPC information retrieved successfully")
        
        vpc_info = vpc_result.get("vpc", {})
        print(f"   VPC ID: {vpc_info.get('id', 'Unknown')}")
        print(f"   VPC Name: {vpc_info.get('name', 'Unknown')}")
        print(f"   CIDR Block: {vpc_info.get('cidr_block', 'Unknown')}")
        print(f"   Red Hat Managed: {vpc_info.get('red_hat_managed', False)}")
        
        # Subnet information
        total_subnets = vpc_result.get("total_subnets", 0)
        subnet_summary = vpc_result.get("subnet_summary", {})
        print(f"   Total Subnets: {total_subnets}")
        print(f"     Public: {subnet_summary.get('public', 0)}")
        print(f"     Private: {subnet_summary.get('private', 0)}")
        
        # Show first subnet if exists
        aws_subnets = vpc_result.get("aws_subnets", [])
        if aws_subnets:
            first_subnet = aws_subnets[0]
            print(f"   First Subnet:")
            print(f"     ID: {first_subnet.get('subnet_id', 'Unknown')}")
            print(f"     Name: {first_subnet.get('name', 'Unknown')}")
            print(f"     AZ: {first_subnet.get('availability_zone', 'Unknown')}")
            print(f"     CIDR: {first_subnet.get('cidr_block', 'Unknown')}")
            print(f"     Public: {first_subnet.get('public', False)}")
        else:
            print("   No subnets found")

    # Test ocm_get_accounts_by_email
    print(f"\n👤 Testing ocm_get_accounts_by_email")
    test_email = "your-email@example.com"  # Replace with actual email address
    accounts_result = await ocm_get_accounts_by_email(test_email)
    
    if "error" in accounts_result:
        print(f"❌ Error: {accounts_result['error']}")
    else:
        print(f"✅ Account search completed successfully")
        print(f"   Search Email: {accounts_result.get('search_email', 'Unknown')}")
        print(f"   Total Accounts Found: {accounts_result.get('total_accounts', 0)}")
        
        # Show account details if found
        accounts = accounts_result.get("accounts", [])
        if accounts:
            first_account = accounts[0]
            print(f"   First Account:")
            print(f"     ID: {first_account.get('id', 'Unknown')}")
            print(f"     Username: {first_account.get('username', 'Unknown')}")
            print(f"     Email: {first_account.get('email', 'Unknown')}")
            print(f"     First Name: {first_account.get('first_name', 'Unknown')}")
            print(f"     Last Name: {first_account.get('last_name', 'Unknown')}")
            print(f"     Organization: {first_account.get('organization', {}).get('name', 'Unknown')}")
        else:
            print("   No accounts found for this email")

if __name__ == "__main__":
    # Check if token is set
    if not os.getenv("RH_API_OFFLINE_TOKEN"):
        print("❌ Please set RH_API_OFFLINE_TOKEN environment variable")
        exit(1)
    
    # Run the test
    asyncio.run(test_tools()) 