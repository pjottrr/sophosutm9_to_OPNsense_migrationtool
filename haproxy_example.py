#!/usr/bin/env python3
"""
Example: HAProxy API usage for OPNsense

This file demonstrates how to configure HAProxy on OPNsense using the pysense API.
HAProxy is a powerful load balancer and reverse proxy. The key concepts are:

ARCHITECTURE OVERVIEW:
======================
1. Frontend  - Listens on ports (e.g., 80, 443) and receives client connections
2. Backend   - Pool of servers that handle requests
3. Server    - Individual server/target in a backend pool
4. ACL       - Access Control List / matching condition (e.g., match by hostname)
5. Action    - What to do when an ACL matches (e.g., route to a specific backend)

TYPICAL FLOW:
=============
Client -> Frontend (port 443) -> ACL matches "example.com" -> Action routes to backend_example -> Server at 192.168.1.10:8080

NAMING CONVENTION:
==================
The library uses a safe domain naming pattern: example.com -> example_dot_com
This ensures entity names are valid across the API.

ENTITY RELATIONSHIPS:
=====================
- Frontend.linkedActions -> [Action UUIDs]
- Action.linkedAcls -> [ACL UUIDs]
- Action.use_backend -> Backend UUID
- Backend.linkedServers -> [Server UUIDs]
"""

from pysense.client import Client
from pysense.pydantic.Server import Server
from pysense.pydantic.Backend import Backend
from pysense.pydantic.Frontend import Frontend
from pysense.pydantic.Acl import Acl
from pysense.pydantic.Action import Action
from pysense.pydantic.SearchRequest import SearchRequest

# Initialize client
client = Client(
    base_url='https://your-opnsense.local/api',
    api_key='your-api-key',
    api_secret='your-api-secret',
    verify_cert=False
)

# ============================================================
# STEP 1: CREATE A SERVER (Backend Target)
# ============================================================
# A Server is the actual endpoint that handles requests.
# This could be a web server, application server, etc.

server = Server(
    enabled=True,
    name="server_myapp",
    address="192.168.1.10",           # IP address or hostname
    port=8080,                         # Target port
    mode=Server.ServersServerModeEnum.ACTIVE,  # active, backup, or disabled
    ssl=False,                         # Enable if backend uses HTTPS
    description="My application server"
)
result = client.haproxy_settings_addServer(
    name=server.name,
    ip=server.address,
    port=server.port,
    description=server.description
)
server_uuid = result.uuid
print(f"Created server: {server_uuid}")

# List all servers
servers = client.haproxy_settings_searchServers()
for s in servers.rows:
    print(f"  Server: {s.name} -> {s.address}:{s.port}")

# Get a specific server
server_details = client.haproxy_settings_getServer(server_uuid)
print(f"Server details: {server_details.name} at {server_details.address}")


# ============================================================
# STEP 2: CREATE A BACKEND (Server Pool)
# ============================================================
# A Backend groups one or more servers and defines how to distribute
# traffic between them (load balancing algorithm).

result = client.haproxy_settings_addBackend(
    name="backend_myapp",
    server=server_uuid,                # Link to the server we created
    description="Backend pool for my application"
)
backend_uuid = result.uuid
print(f"Created backend: {backend_uuid}")

# For more control, you can create a Backend model directly:
backend = Backend(
    enabled=True,
    name="backend_myapp_advanced",
    mode=Backend.BackendsBackendModeEnum.HTTP,  # HTTP or TCP mode
    algorithm=Backend.BackendsBackendAlgorithmEnum.ROUNDROBIN,  # Load balancing algorithm
    linkedServers=[server_uuid],
    healthCheckEnabled=True,           # Enable health checks
    checkInterval="5s",                # Check every 5 seconds
    description="Advanced backend configuration"
)
# Note: For advanced backend creation, you'd need to use the full model

# List all backends
backends = client.haproxy_settings_searchBackend()
for b in backends.rows:
    print(f"  Backend: {b.name} (mode: {b.mode})")


# ============================================================
# STEP 3: CREATE AN ACL (Matching Condition)
# ============================================================
# ACLs define conditions for routing. Common expressions:
# - hdr: Match HTTP Host header exactly
# - hdr_beg: Match beginning of Host header
# - path_beg: Match beginning of URL path
# - ssl_fc_sni: Match SNI hostname for SSL/TLS
# - src: Match source IP address

# ACL to match by hostname
acl_host = Acl(
    name="acl_myapp_host",
    expression=Acl.AclsAclExpressionEnum.HDR,  # Match Host header
    hdr="myapp.example.com",
    description="Match requests for myapp.example.com"
)
result = client.haproxy_settings_addAcl(acl_host)
acl_host_uuid = result.uuid
print(f"Created host ACL: {acl_host_uuid}")

# ACL to match by path prefix
acl_path = Acl(
    name="acl_api_path",
    expression=Acl.AclsAclExpressionEnum.PATH_BEG,  # Match path beginning
    path_beg="/api/",
    description="Match requests starting with /api/"
)
result = client.haproxy_settings_addAcl(acl_path)
acl_path_uuid = result.uuid
print(f"Created path ACL: {acl_path_uuid}")

# ACL to match by source IP
acl_src = Acl(
    name="acl_internal_network",
    expression=Acl.AclsAclExpressionEnum.SRC,  # Match source IP
    src="192.168.0.0/16",
    description="Match requests from internal network"
)
result = client.haproxy_settings_addAcl(acl_src)
acl_src_uuid = result.uuid
print(f"Created source ACL: {acl_src_uuid}")

# ACL for SNI-based routing (useful for TCP mode / SSL passthrough)
acl_sni = Acl(
    name="acl_myapp_sni",
    expression=Acl.AclsAclExpressionEnum.SSL_SNI,  # Match SNI hostname
    ssl_sni="myapp.example.com",
    description="Match SNI for myapp.example.com"
)

# List all ACLs
acls = client.haproxy_settings_searchAcls()
for a in acls.rows:
    print(f"  ACL: {a.name} ({a.expression})")


# ============================================================
# STEP 4: CREATE AN ACTION (Routing Decision)
# ============================================================
# Actions define what happens when ACL conditions are met.
# Common action types:
# - use_backend: Route to a specific backend
# - http-request_redirect: Redirect the request
# - http-request_deny: Deny the request
# - http-request_set-header: Add/modify headers

# Action to route matching requests to a backend
action_route = Action(
    name="action_route_myapp",
    type=Action.ActionsActionTypeEnum.USE_BACKEND,
    use_backend=backend_uuid,          # Route to this backend
    linkedAcls=[acl_host_uuid],        # When this ACL matches
    testType=Action.ActionsActionTesttypeEnum.IF,  # IF acl matches
    operator=Action.ActionsActionOperatorEnum.AND,  # AND logic for multiple ACLs
    description="Route myapp.example.com to backend"
)
result = client.haproxy_settings_addAction(action_route)
action_route_uuid = result.uuid
print(f"Created routing action: {action_route_uuid}")

# Action to redirect HTTP to HTTPS
action_https_redirect = Action(
    name="action_https_redirect",
    type=Action.ActionsActionTypeEnum.HTTP_REQUEST_REDIRECT,
    http_request_redirect="scheme https code 301",
    linkedAcls=[],  # No ACL = applies to all (or configure SSL ACL)
    description="Redirect HTTP to HTTPS"
)
result = client.haproxy_settings_addAction(action_https_redirect)
action_redirect_uuid = result.uuid
print(f"Created redirect action: {action_redirect_uuid}")

# Action to add a custom header
action_add_header = Action(
    name="action_add_xff_header",
    type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER,
    http_request_set_header_name="X-Forwarded-For",
    http_request_set_header_content="%[src]",
    description="Add X-Forwarded-For header"
)
result = client.haproxy_settings_addAction(action_add_header)
action_header_uuid = result.uuid
print(f"Created header action: {action_header_uuid}")

# Action with multiple ACLs (AND logic)
action_api_internal = Action(
    name="action_api_internal_only",
    type=Action.ActionsActionTypeEnum.HTTP_REQUEST_DENY,
    linkedAcls=[acl_path_uuid, acl_src_uuid],  # Match both: /api/ AND internal network
    operator=Action.ActionsActionOperatorEnum.AND,
    testType=Action.ActionsActionTesttypeEnum.UNLESS,  # UNLESS both match (deny external API access)
    description="Deny API access from external networks"
)

# List all actions
actions = client.haproxy_settings_searchActions()
for a in actions.rows:
    print(f"  Action: {a.name} ({a.type})")


# ============================================================
# STEP 5: CREATE/UPDATE A FRONTEND (Listener)
# ============================================================
# A Frontend listens on a port and processes incoming requests.
# It links to Actions which determine routing based on ACLs.

# First, search for existing frontends
frontends = client.haproxy_settings_searchFrontends()
for f in frontends.rows:
    print(f"  Frontend: {f.name} on {f.bind}")

# Get an existing frontend by UUID
# frontend = client.haproxy_settings_getFrontend(frontend_uuid)

# Create a new frontend (HTTP, no SSL)
frontend_http = Frontend(
    enabled=True,
    name="frontend_http",
    bind=["0.0.0.0:80"],              # Listen on port 80
    mode=Frontend.FrontendsFrontendModeEnum.HTTP,
    linkedActions=[action_redirect_uuid],  # Redirect to HTTPS
    description="HTTP Frontend - redirects to HTTPS"
)
# Note: For full frontend creation, you may need to use lower-level API

# Create a new frontend (HTTPS with SSL)
frontend_https = Frontend(
    enabled=True,
    name="frontend_https",
    bind=["0.0.0.0:443"],             # Listen on port 443
    mode=Frontend.FrontendsFrontendModeEnum.SSL,
    ssl_enabled=True,
    ssl_certificates=["cert-uuid-here"],  # Your SSL certificate UUID
    ssl_minVersion=Frontend.FrontendsFrontendSslMinversionEnum.TLSV1_2,
    linkedActions=[
        action_header_uuid,            # Add headers first
        action_route_uuid,             # Then route based on ACL
    ],
    defaultBackend=backend_uuid,       # Default backend if no ACL matches
    description="HTTPS Frontend"
)

# Update an existing frontend to add our action
# This is the most common operation
existing_frontend_uuid = "your-frontend-uuid"
# frontend = client.haproxy_settings_getFrontend(existing_frontend_uuid)
# if action_route_uuid not in frontend.linkedActions:
#     frontend.linkedActions.append(action_route_uuid)
# client.haproxy_settings_setFrontend(existing_frontend_uuid, frontend)


# ============================================================
# STEP 6: TEST AND APPLY CONFIGURATION
# ============================================================
# Always test the configuration before applying!

# Test the configuration (dry run)
configtest = client.haproxy_service_configtest()
print(f"Config test result: {configtest.result}")

# Check if config is valid (no errors)
if "error" not in configtest.result.lower():
    # Apply the configuration (reconfigure HAProxy)
    client.haproxy_service_reconfigure()
    print("Configuration applied successfully!")
else:
    print("Configuration has errors, not applying")
    print(configtest.result)


# ============================================================
# COMPLETE EXAMPLE: Add a new website to existing frontend
# ============================================================
def add_website_to_haproxy(client, domain, backend_ip, backend_port, frontend_name):
    """
    Add a new website to HAProxy with automatic ACL, Server, Backend, and Action creation.

    Args:
        client: Pysense Client instance
        domain: Domain name (e.g., "mysite.example.com")
        backend_ip: IP address of the backend server
        backend_port: Port number of the backend server
        frontend_name: Name of the existing frontend to attach to
    """
    # Create safe name for entities
    domain_safe = client.domain_name_safe(domain)  # mysite.example.com -> mysite_dot_example_dot_com

    # 1. Create server
    server_result = client.haproxy_settings_addServer(
        name=f"server_{domain_safe}",
        ip=backend_ip,
        port=backend_port,
        description=f"Server for {domain}"
    )
    server_uuid = server_result.uuid

    # 2. Create backend
    backend_result = client.haproxy_settings_addBackend(
        name=f"backend_{domain_safe}",
        server=server_uuid,
        description=f"Backend for {domain}"
    )
    backend_uuid = backend_result.uuid

    # 3. Create ACL
    acl = Acl(
        name=f"acl_{domain_safe}",
        expression=Acl.AclsAclExpressionEnum.HDR,
        hdr=domain,
        description=f"Match Host header for {domain}"
    )
    acl_result = client.haproxy_settings_addAcl(acl)
    acl_uuid = acl_result.uuid

    # 4. Create action
    action = Action(
        name=f"action_{domain_safe}",
        type=Action.ActionsActionTypeEnum.USE_BACKEND,
        use_backend=backend_uuid,
        linkedAcls=[acl_uuid],
        description=f"Route {domain} to backend"
    )
    action_result = client.haproxy_settings_addAction(action)
    action_uuid = action_result.uuid

    # 5. Find and update frontend
    frontends = client.haproxy_settings_searchFrontends()
    frontend_uuid = None
    for f in frontends.rows:
        if f.name == frontend_name:
            frontend_uuid = f.uuid
            break

    if frontend_uuid is None:
        raise Exception(f"Frontend '{frontend_name}' not found")

    frontend = client.haproxy_settings_getFrontend(frontend_uuid)
    if action_uuid not in frontend.linkedActions:
        frontend.linkedActions.append(action_uuid)
    client.haproxy_settings_setFrontend(frontend_uuid, frontend)

    # 6. Test and apply
    configtest = client.haproxy_service_configtest()
    if "error" not in configtest.result.lower():
        client.haproxy_service_reconfigure()
        print(f"Successfully added {domain} to HAProxy!")
    else:
        print(f"Configuration error: {configtest.result}")

    return {
        "server_uuid": server_uuid,
        "backend_uuid": backend_uuid,
        "acl_uuid": acl_uuid,
        "action_uuid": action_uuid
    }


# ============================================================
# USING THE HIGH-LEVEL haproxy_simple_proxy METHOD
# ============================================================
# The library also provides a high-level method that does all of the above:

# Add a simple HTTP proxy
# client.haproxy_simple_proxy(
#     domain="myapp.example.com",
#     ip="192.168.1.10",
#     port=8080,
#     frontend="frontend_https",
#     ssl_provider=None  # Set to provider name for auto SSL via ACME
# )

# Add HTTPS proxy with automatic Let's Encrypt certificate
# client.haproxy_simple_proxy(
#     domain="secure.example.com",
#     ip="192.168.1.20",
#     port=8443,
#     frontend="frontend_https",
#     ssl_provider="letsencrypt",  # Automatic certificate via ACME
#     domain_aliases=["www.secure.example.com"]  # Additional domains
# )


# ============================================================
# CLEANUP EXAMPLE
# ============================================================
def remove_website_from_haproxy(client, domain, frontend_name):
    """
    Remove a website configuration from HAProxy.
    """
    domain_safe = client.domain_name_safe(domain)

    # Find and unlink from frontend
    frontends = client.haproxy_settings_searchFrontends()
    for f in frontends.rows:
        if f.name == frontend_name:
            frontend = client.haproxy_settings_getFrontend(f.uuid)
            # Remove action from frontend (you'd need to find the action UUID first)
            break

    # Delete entities (in reverse order of dependencies)
    # client.haproxy_settings_delAction(action_uuid)
    # client.haproxy_settings_delAcls(acl_uuid)
    # client.haproxy_settings_delBackend(backend_uuid)
    # client.haproxy_settings_delServer(server_uuid)

    # Test and apply
    # configtest = client.haproxy_service_configtest()
    # client.haproxy_service_reconfigure()


# ============================================================
# ACL EXPRESSION QUICK REFERENCE
# ============================================================
"""
COMMON ACL EXPRESSIONS:
-----------------------
hdr           - Exact match on Host header
hdr_beg       - Match beginning of Host header
hdr_end       - Match end of Host header
hdr_reg       - Regex match on Host header
hdr_sub       - Substring match on Host header

path          - Exact match on URL path
path_beg      - Match beginning of path
path_end      - Match end of path (e.g., file extension)
path_reg      - Regex match on path
path_sub      - Substring match on path

ssl_fc_sni    - Match SNI hostname (for SSL/TLS)
ssl_sni       - Match SNI in TCP mode

src           - Match source IP/network
src_port      - Match source port

custom_acl    - Custom HAProxy ACL expression
"""


# ============================================================
# ACTION TYPE QUICK REFERENCE
# ============================================================
"""
COMMON ACTION TYPES:
--------------------
use_backend              - Route request to a backend pool
http-request_redirect    - HTTP redirect (301, 302, etc.)
http-request_deny        - Deny the request
http-request_allow       - Explicitly allow the request
http-request_add-header  - Add an HTTP header
http-request_set-header  - Set/replace an HTTP header
http-request_del-header  - Remove an HTTP header
http-request_set-path    - Rewrite the URL path
http-request_auth        - Require HTTP Basic authentication

REDIRECT EXAMPLES:
------------------
"scheme https code 301"           - Redirect to HTTPS
"location https://example.com"    - Redirect to specific URL
"prefix /app"                     - Add prefix to path
"""
