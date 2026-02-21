#!/usr/bin/env python3
"""
HAProxy Configuration Generator

Generates HAProxy configuration from Sophos WAF JSON exports.
Output is a JSON structure suitable for OPNsense HAProxy plugin import.

Usage:
    python generate_haproxy.py output/  # reads from output/ directory
    python generate_haproxy.py output/ haproxy_config.json  # custom output file
"""

import json
import re
from pathlib import Path
from typing import Any


def slugify(name: str) -> str:
    """Convert name to valid HAProxy identifier."""
    # Replace spaces and special chars with underscores
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    # Remove consecutive underscores
    slug = re.sub(r'_+', '_', slug)
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    return slug.lower()


def load_json(filepath: Path) -> list[dict]:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_haproxy_config(input_dir: str) -> dict[str, Any]:
    """
    Generate HAProxy configuration from Sophos WAF JSON files.

    Returns a structure with:
    - servers: backend server definitions
    - backends: HAProxy backends (server pools)
    - frontends: HAProxy frontends (listeners)
    - acls: ACL definitions for routing
    - mappings: frontend-to-location mappings (for manual review)
    """
    input_path = Path(input_dir)

    # Load WAF data
    waf_frontends = load_json(input_path / 'waf_frontends.json')
    waf_backends = load_json(input_path / 'waf_backends.json')
    waf_locations = load_json(input_path / 'waf_locations.json')

    # Build HAProxy structure
    config = {
        'servers': [],
        'backends': [],
        'frontends': [],
        'frontend_backend_mappings': [],
        '_metadata': {
            'source': 'Sophos UTM 9 WAF',
            'generator': 'generate_haproxy.py'
        }
    }

    # 1. Create servers from WAF backends
    server_map = {}  # ref_id -> server config
    for wb in waf_backends:
        host = wb.get('host', {})
        server_id = slugify(wb['name'])

        server = {
            'id': server_id,
            'name': wb['name'],
            'address': host.get('address', ''),
            'port': wb['port'],
            'ssl': wb['ssl'],
            'enabled': wb['enabled'],
            'sophos_ref': wb['ref_id'],
            'comment': wb.get('comment', '')
        }
        config['servers'].append(server)
        server_map[wb['ref_id']] = server

    # 2. Create backends from WAF locations
    # Each location becomes a backend with its servers
    backend_map = {}  # location ref_id -> backend config
    for loc in waf_locations:
        backend_id = slugify(f"backend_{loc['name']}")

        # Get servers for this backend
        servers = []
        for backend_ref in loc.get('backends', []):
            ref_id = backend_ref.get('ref_id', '')
            if ref_id in server_map:
                servers.append({
                    'server_id': server_map[ref_id]['id'],
                    'server_name': server_map[ref_id]['name'],
                    'address': server_map[ref_id]['address'],
                    'port': server_map[ref_id]['port'],
                    'ssl': server_map[ref_id]['ssl']
                })

        backend = {
            'id': backend_id,
            'name': loc['name'],
            'path': loc['path'],
            'servers': servers,
            'mode': 'http',
            'balance': 'roundrobin',
            'sticky_session': loc.get('sticky_session', False),
            'hot_standby': loc.get('hot_standby', False),
            'enabled': loc['enabled'],
            'sophos_ref': loc['ref_id'],
            'allowed_networks': loc.get('allowed_networks', []),
            'denied_networks': loc.get('denied_networks', [])
        }
        config['backends'].append(backend)
        backend_map[loc['ref_id']] = backend

    # 3. Create frontends from WAF frontends
    for wf in waf_frontends:
        address = wf.get('address', {})
        frontend_id = slugify(f"frontend_{wf['name']}")

        # Determine bind address
        bind_address = address.get('address', '*')
        bind_port = wf['port']

        frontend = {
            'id': frontend_id,
            'name': wf['name'],
            'bind': f"{bind_address}:{bind_port}",
            'bind_address': bind_address,
            'bind_port': bind_port,
            'mode': 'http',
            'ssl': wf['type'] == 'https',
            'domains': wf.get('domains', []),
            'enabled': wf['enabled'],
            'preserve_host': wf.get('preserve_host', False),
            'html_rewrite': wf.get('html_rewrite', False),
            'implicit_redirect': wf.get('implicit_redirect', False),
            'sophos_ref': wf['ref_id'],
            'comment': wf.get('comment', ''),
            # ACLs for domain matching
            'acls': [
                {
                    'name': f"host_{slugify(domain)}",
                    'criterion': 'hdr(host)',
                    'pattern': domain
                }
                for domain in wf.get('domains', [])
            ],
            # Default backend (needs manual mapping)
            'default_backend': None,
            'use_backend_rules': []
        }
        config['frontends'].append(frontend)

    # 4. Create mapping suggestions based on naming patterns
    # This helps the user connect frontends to backends
    for frontend in config['frontends']:
        for backend in config['backends']:
            # Try to match by domain in location name
            for domain in frontend['domains']:
                if domain.lower() in backend['name'].lower():
                    config['frontend_backend_mappings'].append({
                        'frontend': frontend['name'],
                        'frontend_id': frontend['id'],
                        'backend': backend['name'],
                        'backend_id': backend['id'],
                        'path': backend['path'],
                        'match_reason': f"domain '{domain}' found in location name",
                        'confidence': 'medium'
                    })

            # Try to match by similar naming
            frontend_words = set(frontend['name'].lower().replace('.', ' ').replace('-', ' ').split())
            backend_words = set(backend['name'].lower().replace('.', ' ').replace('-', ' ').replace('/', ' ').split())
            common_words = frontend_words & backend_words - {'frl', 'nl', 'www', 'http', 'https'}

            if len(common_words) >= 1:
                config['frontend_backend_mappings'].append({
                    'frontend': frontend['name'],
                    'frontend_id': frontend['id'],
                    'backend': backend['name'],
                    'backend_id': backend['id'],
                    'path': backend['path'],
                    'match_reason': f"common words: {', '.join(common_words)}",
                    'confidence': 'low'
                })

    return config


def generate_haproxy_conf(config: dict[str, Any]) -> str:
    """
    Generate HAProxy configuration file format.
    This is for reference - OPNsense uses its own format.
    """
    lines = [
        "# HAProxy Configuration",
        "# Generated from Sophos UTM 9 WAF",
        "# NOTE: This is a reference format. OPNsense HAProxy uses GUI/API.",
        "",
        "# =============================================================================",
        "# BACKENDS",
        "# =============================================================================",
        ""
    ]

    for backend in config['backends']:
        if not backend['enabled']:
            lines.append(f"# DISABLED: {backend['name']}")

        lines.append(f"backend {backend['id']}")
        lines.append(f"    # Sophos location: {backend['name']}")
        lines.append(f"    # Path: {backend['path']}")
        lines.append(f"    mode {backend['mode']}")
        lines.append(f"    balance {backend['balance']}")

        if backend['sticky_session']:
            lines.append("    cookie SERVERID insert indirect nocache")

        for i, server in enumerate(backend['servers']):
            ssl_opt = "ssl verify none" if server['ssl'] else ""
            cookie_opt = f"cookie s{i}" if backend['sticky_session'] else ""
            lines.append(f"    server {server['server_id']} {server['address']}:{server['port']} {ssl_opt} {cookie_opt}".strip())

        lines.append("")

    lines.extend([
        "# =============================================================================",
        "# FRONTENDS",
        "# =============================================================================",
        ""
    ])

    for frontend in config['frontends']:
        if not frontend['enabled']:
            lines.append(f"# DISABLED: {frontend['name']}")

        lines.append(f"frontend {frontend['id']}")
        lines.append(f"    # Sophos frontend: {frontend['name']}")
        lines.append(f"    # Domains: {', '.join(frontend['domains'])}")

        bind_opts = "ssl crt /path/to/cert.pem" if frontend['ssl'] else ""
        lines.append(f"    bind {frontend['bind']} {bind_opts}".strip())
        lines.append(f"    mode {frontend['mode']}")

        # ACLs for domains
        for acl in frontend['acls']:
            lines.append(f"    acl {acl['name']} {acl['criterion']} -i {acl['pattern']}")

        # use_backend rules would go here
        lines.append("    # TODO: Add use_backend rules based on mapping")
        lines.append("    # default_backend <backend_id>")
        lines.append("")

    return "\n".join(lines)


def main():
    import sys

    input_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "haproxy_config.json"

    print(f"Reading WAF data from {input_dir}/...")
    config = generate_haproxy_config(input_dir)

    # Write JSON config
    print(f"Writing HAProxy config to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # Write reference HAProxy conf
    conf_file = output_file.replace('.json', '.cfg')
    print(f"Writing reference HAProxy conf to {conf_file}...")
    conf_content = generate_haproxy_conf(config)
    with open(conf_file, 'w', encoding='utf-8') as f:
        f.write(conf_content)

    # Summary
    print(f"\nSummary:")
    print(f"  Servers:  {len(config['servers'])}")
    print(f"  Backends: {len(config['backends'])}")
    print(f"  Frontends: {len(config['frontends'])}")
    print(f"  Mapping suggestions: {len(config['frontend_backend_mappings'])}")

    print(f"\nFrontends:")
    for fe in config['frontends']:
        status = "enabled" if fe['enabled'] else "DISABLED"
        print(f"  - {fe['name']} ({fe['bind']}) [{status}]")
        print(f"    Domains: {', '.join(fe['domains'])}")

    print(f"\nBackends (from locations):")
    for be in config['backends']:
        status = "enabled" if be['enabled'] else "DISABLED"
        servers = ', '.join(s['server_name'] for s in be['servers']) or 'none'
        print(f"  - {be['name']} (path: {be['path']}) [{status}]")
        print(f"    Servers: {servers}")

    print(f"\nMapping suggestions (review manually):")
    for mapping in config['frontend_backend_mappings']:
        print(f"  {mapping['frontend']} -> {mapping['backend']}")
        print(f"    Reason: {mapping['match_reason']} (confidence: {mapping['confidence']})")


if __name__ == "__main__":
    main()
