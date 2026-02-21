#!/usr/bin/env python3
"""
HAProxy Configuration File Generator

Creates a working HAProxy configuration from Sophos WAF JSON exports.
Uses a mapping file to connect frontends to backends.

Usage:
    # Generate initial mapping file (edit this to configure frontend-backend relations)
    python create_haproxy_conf.py --generate-mapping output/ frontend_backend_mapping.json

    # Generate HAProxy config using the mapping
    python create_haproxy_conf.py output/ frontend_backend_mapping.json haproxy.cfg
"""

import json
import re
import argparse
from pathlib import Path
from typing import Any
from datetime import datetime


def slugify(name: str) -> str:
    """Convert name to valid HAProxy identifier."""
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    slug = re.sub(r'_+', '_', slug)
    return slug.strip('_').lower()[:32]


def load_json(filepath: Path) -> list[dict]:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_mapping_file(input_dir: str, output_file: str):
    """
    Generate an initial mapping file for frontend-backend connections.
    User should edit this file to configure the correct mappings.
    """
    input_path = Path(input_dir)

    frontends = load_json(input_path / 'waf_frontends.json')
    locations = load_json(input_path / 'waf_locations.json')
    backends = load_json(input_path / 'waf_backends.json')

    # Build backend lookup by ref_id
    backend_lookup = {b['ref_id']: b for b in backends}

    mapping = {
        '_comment': [
            "Frontend-Backend Mapping Configuration",
            "Edit this file to configure which backends serve which frontends.",
            "Each frontend can have multiple path-based backend rules.",
            "",
            "Structure:",
            "  frontend_ref_id: {",
            "    'default_backend': 'location_ref_id',  # Default backend for this frontend",
            "    'path_rules': [  # Optional path-based routing",
            "      {'path': '/api/', 'backend': 'location_ref_id'},",
            "    ]",
            "  }"
        ],
        'mappings': {}
    }

    # Create initial mapping with suggestions
    for fe in frontends:
        fe_mapping = {
            'frontend_name': fe['name'],
            'domains': fe.get('domains', []),
            'enabled': fe['enabled'],
            'default_backend': None,
            'default_backend_name': None,
            'path_rules': [],
            '_available_backends': []
        }

        # List available backends for reference
        for loc in locations:
            backend_names = []
            for be_ref in loc.get('backends', []):
                be = backend_lookup.get(be_ref.get('ref_id', ''))
                if be:
                    backend_names.append(f"{be['name']} ({be['host'].get('address', '?')}:{be['port']})")

            fe_mapping['_available_backends'].append({
                'location_ref': loc['ref_id'],
                'location_name': loc['name'],
                'path': loc['path'],
                'servers': backend_names,
                'enabled': loc['enabled']
            })

            # Try to auto-match based on naming
            for domain in fe.get('domains', []):
                domain_lower = domain.lower()
                loc_name_lower = loc['name'].lower()

                # Check if domain appears in location name
                if domain_lower in loc_name_lower or loc_name_lower.split(':')[0].strip() == domain_lower:
                    fe_mapping['default_backend'] = loc['ref_id']
                    fe_mapping['default_backend_name'] = loc['name']
                    break

        mapping['mappings'][fe['ref_id']] = fe_mapping

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"Generated mapping file: {output_file}")
    print(f"\nFrontends found: {len(frontends)}")
    print(f"Locations (potential backends): {len(locations)}")
    print(f"\nPlease edit {output_file} to configure frontend-backend mappings.")
    print("Set 'default_backend' to the location ref_id that should handle requests.")


def generate_haproxy_config(input_dir: str, mapping_file: str, output_file: str):
    """Generate a working HAProxy configuration file."""
    input_path = Path(input_dir)

    # Load data
    frontends = load_json(input_path / 'waf_frontends.json')
    locations = load_json(input_path / 'waf_locations.json')
    backends = load_json(input_path / 'waf_backends.json')

    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    # Build lookups
    frontend_lookup = {f['ref_id']: f for f in frontends}
    location_lookup = {l['ref_id']: l for l in locations}
    backend_lookup = {b['ref_id']: b for b in backends}

    lines = []

    # =========================================================================
    # GLOBAL SECTION
    # =========================================================================
    lines.extend([
        "#" + "=" * 79,
        "# HAProxy Configuration",
        f"# Generated from Sophos UTM 9 WAF on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "# Source: webadmin-sanitized.xml",
        "#" + "=" * 79,
        "",
        "global",
        "    log /dev/log local0",
        "    log /dev/log local1 notice",
        "    chroot /var/lib/haproxy",
        "    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners",
        "    stats timeout 30s",
        "    user haproxy",
        "    group haproxy",
        "    daemon",
        "",
        "    # SSL settings",
        "    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256",
        "    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384",
        "    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets",
        "",
    ])

    # =========================================================================
    # DEFAULTS SECTION
    # =========================================================================
    lines.extend([
        "defaults",
        "    log     global",
        "    mode    http",
        "    option  httplog",
        "    option  dontlognull",
        "    option  forwardfor",
        "    option  http-server-close",
        "    timeout connect 5000",
        "    timeout client  50000",
        "    timeout server  50000",
        "    errorfile 400 /etc/haproxy/errors/400.http",
        "    errorfile 403 /etc/haproxy/errors/403.http",
        "    errorfile 408 /etc/haproxy/errors/408.http",
        "    errorfile 500 /etc/haproxy/errors/500.http",
        "    errorfile 502 /etc/haproxy/errors/502.http",
        "    errorfile 503 /etc/haproxy/errors/503.http",
        "    errorfile 504 /etc/haproxy/errors/504.http",
        "",
    ])

    # =========================================================================
    # BACKENDS SECTION
    # =========================================================================
    lines.extend([
        "#" + "=" * 79,
        "# BACKENDS",
        "#" + "=" * 79,
        "",
    ])

    # Create a backend for each location
    location_to_backend_name = {}

    for loc in locations:
        backend_id = f"be_{slugify(loc['name'])}"
        location_to_backend_name[loc['ref_id']] = backend_id

        if not loc['enabled']:
            lines.append(f"# DISABLED: {loc['name']}")

        lines.append(f"backend {backend_id}")
        lines.append(f"    # Sophos location: {loc['name']}")
        lines.append(f"    # Path: {loc['path']}")
        lines.append(f"    mode http")
        lines.append(f"    balance roundrobin")

        # HTTP health check
        lines.append(f"    option httpchk GET / HTTP/1.1\\r\\nHost:\\ localhost")

        # Sticky sessions if enabled
        if loc.get('sticky_session'):
            lines.append(f"    cookie SERVERID insert indirect nocache")

        # Add servers
        server_idx = 0
        for be_ref in loc.get('backends', []):
            be_ref_id = be_ref.get('ref_id', '')
            be = backend_lookup.get(be_ref_id)

            if be:
                host = be.get('host', {})
                address = host.get('address', '127.0.0.1')
                port = be['port']
                server_id = slugify(be['name'])

                opts = []
                if be['ssl']:
                    opts.append("ssl verify none")
                opts.append("check")

                if loc.get('sticky_session'):
                    opts.append(f"cookie s{server_idx}")

                if loc.get('hot_standby') and server_idx > 0:
                    opts.append("backup")

                if not be['enabled']:
                    opts.append("disabled")

                opt_str = " ".join(opts)
                lines.append(f"    server {server_id} {address}:{port} {opt_str}")
                server_idx += 1

        # Access control (allowed/denied networks)
        allowed = loc.get('allowed_networks', [])
        denied = loc.get('denied_networks', [])

        if denied:
            lines.append(f"    # Denied networks:")
            for net in denied:
                addr = net.get('address', '')
                mask = net.get('netmask', '')
                if addr and addr != '0.0.0.0':
                    cidr = f"{addr}/{mask}" if mask else addr
                    lines.append(f"    http-request deny if {{ src {cidr} }}")

        if allowed and not any(n.get('name') == 'Any' for n in allowed):
            lines.append(f"    # Allowed networks only:")
            acl_parts = []
            for net in allowed:
                addr = net.get('address', '')
                mask = net.get('netmask', '')
                if addr:
                    cidr = f"{addr}/{mask}" if mask else addr
                    acl_parts.append(cidr)
            if acl_parts:
                lines.append(f"    acl allowed_src src {' '.join(acl_parts)}")
                lines.append(f"    http-request deny unless allowed_src")

        lines.append("")

    # =========================================================================
    # FRONTENDS SECTION
    # =========================================================================
    lines.extend([
        "#" + "=" * 79,
        "# FRONTENDS",
        "#" + "=" * 79,
        "",
    ])

    for fe in frontends:
        fe_mapping = mapping.get('mappings', {}).get(fe['ref_id'], {})
        frontend_id = f"fe_{slugify(fe['name'])}"

        address = fe.get('address', {})
        bind_addr = address.get('address', '*')
        bind_port = fe['port']

        if not fe['enabled']:
            lines.append(f"# DISABLED: {fe['name']}")

        lines.append(f"frontend {frontend_id}")
        lines.append(f"    # Sophos frontend: {fe['name']}")
        lines.append(f"    # Domains: {', '.join(fe.get('domains', []))}")

        # Bind
        if fe['type'] == 'https':
            # SSL certificate path - user needs to configure this
            cert_path = f"/etc/haproxy/certs/{slugify(fe['name'])}.pem"
            lines.append(f"    bind {bind_addr}:{bind_port} ssl crt {cert_path}")

            # HTTP to HTTPS redirect frontend (optional)
            if fe.get('implicit_redirect'):
                lines.append(f"    # Note: implicit_redirect was enabled in Sophos")
                lines.append(f"    # Consider adding HTTP->HTTPS redirect frontend on port 80")
        else:
            lines.append(f"    bind {bind_addr}:{bind_port}")

        lines.append(f"    mode http")

        # Preserve host header
        if fe.get('preserve_host'):
            lines.append(f"    # preserve_host enabled - backend will see original Host header")

        # Domain ACLs
        for domain in fe.get('domains', []):
            acl_name = f"host_{slugify(domain)}"
            lines.append(f"    acl {acl_name} hdr(host) -i {domain}")
            lines.append(f"    acl {acl_name} hdr(host) -i {domain}:{bind_port}")

        # Path-based routing rules
        path_rules = fe_mapping.get('path_rules', [])
        for rule in path_rules:
            path = rule.get('path', '/')
            backend_ref = rule.get('backend')
            if backend_ref and backend_ref in location_to_backend_name:
                backend_name = location_to_backend_name[backend_ref]
                acl_name = f"path_{slugify(path)}"
                lines.append(f"    acl {acl_name} path_beg {path}")
                lines.append(f"    use_backend {backend_name} if {acl_name}")

        # Default backend
        default_backend_ref = fe_mapping.get('default_backend')
        if default_backend_ref and default_backend_ref in location_to_backend_name:
            backend_name = location_to_backend_name[default_backend_ref]
            lines.append(f"    default_backend {backend_name}")
        else:
            lines.append(f"    # WARNING: No default_backend configured!")
            lines.append(f"    # Edit mapping file to set default_backend for this frontend")
            # Suggest possible backends
            lines.append(f"    # Available backends: {', '.join(location_to_backend_name.values())}")

        lines.append("")

    # =========================================================================
    # STATS SECTION (optional)
    # =========================================================================
    lines.extend([
        "#" + "=" * 79,
        "# STATISTICS",
        "#" + "=" * 79,
        "",
        "listen stats",
        "    bind *:8404",
        "    mode http",
        "    stats enable",
        "    stats uri /stats",
        "    stats refresh 10s",
        "    stats admin if LOCALHOST",
        "",
    ])

    # Write config
    config_content = "\n".join(lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print(f"Generated HAProxy config: {output_file}")
    print(f"\nSummary:")
    print(f"  Frontends: {len(frontends)}")
    print(f"  Backends: {len(locations)}")
    print(f"  Servers: {len(backends)}")

    # Check for missing mappings
    missing = []
    for fe in frontends:
        fe_mapping = mapping.get('mappings', {}).get(fe['ref_id'], {})
        if not fe_mapping.get('default_backend'):
            missing.append(fe['name'])

    if missing:
        print(f"\nWARNING: The following frontends have no default_backend configured:")
        for name in missing:
            print(f"  - {name}")
        print(f"\nEdit {mapping_file} to configure the mappings.")


def main():
    parser = argparse.ArgumentParser(
        description='Generate HAProxy configuration from Sophos WAF exports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Step 1: Generate mapping file (edit this to configure frontend-backend relations)
  python create_haproxy_conf.py --generate-mapping output/ mapping.json

  # Step 2: Edit mapping.json to configure which backends serve which frontends

  # Step 3: Generate HAProxy config
  python create_haproxy_conf.py output/ mapping.json haproxy.cfg
        """
    )

    parser.add_argument('input_dir', help='Directory containing WAF JSON files')
    parser.add_argument('mapping_or_output', help='Mapping file (for config) or output file (for --generate-mapping)')
    parser.add_argument('output_file', nargs='?', help='Output HAProxy config file')
    parser.add_argument('--generate-mapping', action='store_true',
                        help='Generate initial mapping file instead of HAProxy config')

    args = parser.parse_args()

    if args.generate_mapping:
        generate_mapping_file(args.input_dir, args.mapping_or_output)
    else:
        if not args.output_file:
            parser.error("output_file is required when generating HAProxy config")
        generate_haproxy_config(args.input_dir, args.mapping_or_output, args.output_file)


if __name__ == "__main__":
    main()
