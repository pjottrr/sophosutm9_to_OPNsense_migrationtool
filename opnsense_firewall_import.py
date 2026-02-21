#!/usr/bin/env python3
"""
OPNsense Firewall Rules Import Script

Imports Sophos UTM firewall rules to OPNsense.

Usage:
    python opnsense_firewall_import.py [mapping.json]

Arguments:
    mapping.json    Optional path to interface mapping file (default: mapping.json)
"""

import argparse
import ipaddress
import json
import re
import sys
from pathlib import Path

# Add local pysense to path
sys.path.insert(0, str(Path(__file__).parent))

from pysense.client import Client
from pysense.pydantic.Alias import Alias
from pysense.pydantic.Rule import Rule
from pysense.pydantic.SNATRule import Rule as SNATRule


# OPNsense API credentials
OPNSENSE_URL = "https://192.168.1.1/api"
OPNSENSE_KEY = "your_api_key_here"
OPNSENSE_SECRET = "your_api_secret_here"

# Input directory with Sophos JSON exports
INPUT_DIR = Path(__file__).parent / "output"

# Default interface if Sophos rule has no interface specified
DEFAULT_INTERFACE = 'wan'

# Default mapping file
DEFAULT_MAPPING_FILE = Path(__file__).parent / "mapping.json"


def load_interface_mapping(filepath: Path) -> dict:
    """Load interface mapping from JSON file."""
    if not filepath.exists():
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Support both flat dict and nested structure
            if 'interface_mapping' in data:
                return data['interface_mapping']
            return data
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def save_mapping_template(filepath: Path, all_interfaces: list, unmapped: list, available: dict, existing_mapping: dict):
    """Save a template mapping file, preserving existing values."""
    # Build mapping: keep existing values, add empty for new interfaces
    mapping = {}
    for iface in sorted(all_interfaces):
        if iface in existing_mapping:
            mapping[iface] = existing_mapping[iface]
        else:
            mapping[iface] = ""  # Empty = skip this interface

    # Build interface list with descriptions: "lan (LAN), wan (WAN)"
    iface_list = [f"{key} ({name})" for key, name in available.items()]

    template = {
        "_comment": [
            "Interface Mapping Configuration",
            "Map Sophos network names to OPNsense interface names.",
            "Available OPNsense interfaces:",
        ] + [f"  - {key}: {name}" for key, name in available.items()] + [
            "Leave value empty to skip/ignore that interface."
        ],
        "interface_mapping": mapping
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"\nMapping file updated: {filepath}")
    print(f"  - {len(unmapped)} new interface(s) added")
    print(f"  - {len(existing_mapping)} existing mapping(s) preserved")
    print("Edit this file and set the correct OPNsense interfaces.")
    print("Leave value empty to skip/ignore an interface.")


def extract_sophos_interfaces(rules: list) -> set:
    """Extract unique interface/network names from Sophos rules."""
    interfaces = set()
    for rule in rules:
        for src in rule.get('sources', []):
            name = src.get('name', '')
            # Match patterns like "XX Name (Network)" or "Name (User Network)"
            if '(Network)' in name or '(User Network)' in name or '(User Group Network)' in name:
                interfaces.add(name)
        for dst in rule.get('destinations', []):
            name = dst.get('name', '')
            if '(Network)' in name or '(User Network)' in name or '(User Group Network)' in name:
                interfaces.add(name)
    return interfaces


def slugify(name: str) -> str:
    """Convert name to valid OPNsense alias name (alphanumeric and underscore only)."""
    slug = name.replace('-', '_').replace(' ', '_').replace('.', '_')
    slug = re.sub(r'[^a-zA-Z0-9_]', '', slug)
    slug = re.sub(r'_+', '_', slug)
    if slug and not slug[0].isalpha():
        slug = 'a_' + slug
    return slug.strip('_')[:31]


def ensure_alias_for_ip(client: Client, ip_or_cidr: str, existing_aliases: dict) -> str | None:
    """Ensure an alias exists for an IP address or CIDR range.

    Returns the alias name if found or created, None on failure.
    """
    # Generate a name from the IP/CIDR
    alias_name = slugify(f"net_{ip_or_cidr}")

    # Already exists
    if alias_name in existing_aliases:
        return alias_name

    # Determine type: network (has /) or host
    if '/' in ip_or_cidr:
        alias_type = Alias.AliasesAliasTypeEnum.NETWORK
    else:
        alias_type = Alias.AliasesAliasTypeEnum.HOST

    try:
        alias = Alias(
            enabled=True,
            name=alias_name,
            type=alias_type,
            content=ip_or_cidr,
            description=f"Auto-created from {ip_or_cidr}"
        )
        result = client.firewall_alias_add_item(alias)
        if result and hasattr(result, 'uuid') and result.uuid:
            existing_aliases[alias_name] = result.uuid
            return alias_name
    except Exception:
        pass

    return None


def create_alias_group(client: Client, group_name: str, members: list[str], existing_aliases: dict) -> str | None:
    """Create a network group alias for multiple sources/destinations.

    Network groups can only contain alias names, not raw IPs/CIDRs.
    Creates individual aliases for IP/CIDR entries first.

    Returns the alias name if created or already exists, None on failure.
    """
    alias_name = slugify(group_name)

    # Already exists
    if alias_name in existing_aliases:
        return alias_name

    # Resolve members to alias names
    alias_members = []
    for member in members:
        if member == 'any':
            continue

        # Check if it's an IP/CIDR (contains dots/colons)
        if re.match(r'^\d+\.\d+\.\d+\.\d+(/\d+)?$', member) or ':' in member:
            # Create alias for IP/CIDR first
            member_alias = ensure_alias_for_ip(client, member, existing_aliases)
            if member_alias:
                alias_members.append(member_alias)
        else:
            # Already an alias name
            alias_members.append(member)

    if not alias_members:
        return None

    # Build content: join alias names with newlines
    content = '\n'.join(alias_members)

    try:
        alias = Alias(
            enabled=True,
            name=alias_name,
            type=Alias.AliasesAliasTypeEnum.NETWORKGROUP,
            content=content,
            description=f"Auto-created for rule: {group_name[:200]}"
        )
        result = client.firewall_alias_add_item(alias)
        if result and hasattr(result, 'uuid') and result.uuid:
            existing_aliases[alias_name] = result.uuid
            print(f"  * Created alias group: {alias_name} ({len(alias_members)} members)")
            return alias_name
        else:
            print(f"  ! Failed to create alias group {alias_name}: {result}")
    except Exception as e:
        print(f"  ! Error creating alias group {alias_name}: {e}")

    return None


def get_available_interfaces(client: Client) -> dict:
    """Get available interfaces from OPNsense.

    Returns dict mapping interface key to display name, e.g.:
    {'lan': 'LAN', 'wan': 'WAN', 'opt1': 'OPT1'}
    """
    data = client._get('firewall/filter/getRule')
    interfaces = {}
    if data and 'rule' in data and 'interface' in data['rule']:
        for key, info in data['rule']['interface'].items():
            interfaces[key] = info.get('value', key)
    return interfaces


def validate_interfaces(available: dict, required: list) -> tuple:
    """Validate that required interfaces exist in OPNsense.

    Returns (valid: bool, missing: list)
    """
    missing = []
    for iface in required:
        if iface not in available:
            missing.append(iface)
    return len(missing) == 0, missing


def load_json(filepath: Path) -> list[dict]:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_existing_aliases(client: Client) -> dict:
    """Get existing aliases and return a dict by name."""
    data = client._get('firewall/alias/search_item')
    existing = {}
    if data and 'rows' in data:
        for row in data['rows']:
            existing[row['name']] = row['uuid']
    return existing


def get_existing_rules(client: Client) -> list:
    """Get existing firewall rules."""
    data = client._get('firewall/filter/searchRule')
    if data and 'rows' in data:
        return data['rows']
    return []


def delete_all_rules(client: Client) -> int:
    """Delete all non-system firewall rules."""
    print("\n=== Deleting existing firewall rules ===")

    existing = get_existing_rules(client)
    deleted = 0

    for rule in existing:
        uuid = rule.get('uuid')
        if not uuid:
            continue

        try:
            result = client._post(f'firewall/filter/delRule/{uuid}', {})
            if result and result.get('result') == 'deleted':
                deleted += 1
        except Exception as e:
            print(f"  ! Error deleting rule: {e}")

    print(f"  Deleted {deleted} rules")
    return deleted


def map_source_destination(item: dict, existing_aliases: dict) -> str:
    """Map a Sophos source/destination to OPNsense format."""
    name = item.get('name', '')
    address = item.get('address', '')
    netmask = item.get('netmask', '')

    # Handle "Any"
    if name == 'Any' or address == '0.0.0.0':
        return 'any'

    # Try to find existing alias by slugified name
    alias_name = slugify(name)
    if alias_name in existing_aliases:
        return alias_name

    # If we have an address, use it directly
    if address:
        if netmask and netmask != '32':
            return f"{address}/{netmask}"
        return address

    # Fallback to any if we can't resolve
    return 'any'


def map_service(service: dict, existing_aliases: dict) -> tuple:
    """
    Map a Sophos service to OPNsense protocol and port.
    Returns (protocol, port) tuple.
    """
    name = service.get('name', '')
    port = service.get('port', '')
    protocol = service.get('protocol', '')
    dst_low = service.get('dst_low')
    dst_high = service.get('dst_high')

    # Handle "Any"
    if name == 'Any':
        return ('any', None)

    # Common protocol mappings
    if 'ping' in name.lower() or 'icmp' in name.lower():
        return ('icmp', None)

    # Handle port ranges FIRST (Sophos uses dst_low/dst_high)
    if dst_low and dst_high and dst_low != dst_high:
        port_str = f"{dst_low}-{dst_high}"  # OPNsense uses dash for ranges
        proto = 'tcp'
        if 'udp' in name.lower():
            proto = 'udp'
        return (proto, port_str)

    # Handle single port from dst_low
    if dst_low:
        proto = 'tcp'
        if 'udp' in name.lower():
            proto = 'udp'
        return (proto, str(dst_low))

    # Try to extract port from port field (Sophos already uses dash format)
    if port:
        proto = 'tcp'
        if 'udp' in name.lower():
            proto = 'udp'
        return (proto, port)

    # Try to find existing PORT alias by slugified name (only port type aliases)
    alias_name = slugify(name)
    if alias_name in existing_aliases:
        # Only use if it's actually a port alias (we check by trying to use it)
        # For now, skip this and extract from name instead
        pass

    # Try to extract port from name
    port_match = re.search(r'(\d+)', name)
    if port_match:
        port_num = port_match.group(1)
        if 'udp' in name.lower():
            return ('udp', port_num)
        elif 'tcp' in name.lower():
            return ('tcp', port_num)
        else:
            return ('any', port_num)

    # Default to any
    return ('any', None)


def map_action(sophos_action: str) -> Rule.RulesRuleActionEnum:
    """Map Sophos action to OPNsense action."""
    if sophos_action == 'accept':
        return Rule.RulesRuleActionEnum.PASS
    elif sophos_action == 'drop':
        return Rule.RulesRuleActionEnum.BLOCK
    elif sophos_action == 'reject':
        return Rule.RulesRuleActionEnum.REJECT
    return Rule.RulesRuleActionEnum.BLOCK


def create_port_alias(client: Client, group_name: str, ports: list[str], existing_aliases: dict) -> str | None:
    """Create a port alias for multiple ports/ranges.

    Returns the alias name if created or already exists, None on failure.
    """
    alias_name = slugify(group_name)

    # Already exists
    if alias_name in existing_aliases:
        return alias_name

    if not ports:
        return None

    # Port aliases use colon for ranges (e.g. 1028:1049), not dash
    alias_ports = [p.replace('-', ':') for p in ports]

    # Build content: join ports with newlines
    content = '\n'.join(alias_ports)

    try:
        alias = Alias(
            enabled=True,
            name=alias_name,
            type=Alias.AliasesAliasTypeEnum.PORT,
            content=content,
            description=f"Auto-created for rule: {group_name[:200]}"
        )
        result = client.firewall_alias_add_item(alias)
        if result and hasattr(result, 'uuid') and result.uuid:
            existing_aliases[alias_name] = result.uuid
            print(f"  * Created port alias: {alias_name} ({len(ports)} ports)")
            return alias_name
        else:
            # Retry via raw API for validation errors
            raw = client._post('firewall/alias/addItem', {'alias': {
                'enabled': '1',
                'name': alias_name,
                'type': 'port',
                'content': content,
                'description': f"Auto-created for rule: {group_name[:200]}"
            }})
            if raw and raw.get('uuid'):
                existing_aliases[alias_name] = raw['uuid']
                print(f"  * Created port alias: {alias_name} ({len(ports)} ports)")
                return alias_name
            validations = raw.get('validations', {}) if raw else {}
            print(f"  ! Failed to create port alias {alias_name}: {validations or raw}")
    except Exception as e:
        print(f"  ! Error creating port alias {alias_name}: {e}")

    return None


def build_subnet_lookup(interface_networks: list, interface_mapping: dict) -> list:
    """Build subnet-to-interface lookup from interface networks."""
    subnets = []
    for net in interface_networks:
        name = net.get('name', '')
        address = net.get('address', '')
        netmask = net.get('netmask', '')
        if not address or not netmask:
            continue
        opnsense_iface = interface_mapping.get(name, '')
        if not opnsense_iface:
            continue
        try:
            network = ipaddress.IPv4Network(f"{address}/{netmask}", strict=False)
            subnets.append((network, opnsense_iface))
        except ValueError:
            continue
    # Sort by prefix length descending (most specific first)
    subnets.sort(key=lambda x: x[0].prefixlen, reverse=True)
    return subnets


def lookup_interface_by_ip(ip_str: str, subnet_lookup: list) -> str | None:
    """Find which OPNsense interface an IP belongs to."""
    try:
        ip = ipaddress.IPv4Address(ip_str)
    except ValueError:
        return None
    for network, iface in subnet_lookup:
        if ip in network:
            return iface
    return None


def determine_interface(sophos_rule: dict, interface_mapping: dict, subnet_lookup: list) -> str | None:
    """Determine OPNsense interface based on source/destination networks.

    First checks for direct interface network name matches in the mapping,
    then falls back to IP-based subnet lookup for hosts and networks.

    Returns interface name or None if no mapping found.
    """
    # Check sources - interface network names first
    for src in sophos_rule.get('sources', []):
        name = src.get('name', '')
        if name in interface_mapping and interface_mapping[name]:
            return interface_mapping[name]

    # Check destinations - interface network names
    for dst in sophos_rule.get('destinations', []):
        name = dst.get('name', '')
        if name in interface_mapping and interface_mapping[name]:
            return interface_mapping[name]

    # Check source IPs against subnets
    for src in sophos_rule.get('sources', []):
        address = src.get('address', '')
        if address:
            iface = lookup_interface_by_ip(address, subnet_lookup)
            if iface:
                return iface

    # Check destination IPs against subnets
    for dst in sophos_rule.get('destinations', []):
        address = dst.get('address', '')
        if address:
            iface = lookup_interface_by_ip(address, subnet_lookup)
            if iface:
                return iface

    return None


def import_firewall_rules(client: Client, existing_aliases: dict, rules: list, interface_mapping: dict, subnet_lookup: list) -> dict:
    """Import firewall rules."""
    print(f"\n=== Importing {len(rules)} firewall rules ===")

    imported = {}
    skipped = 0
    skipped_rules = []  # Rules skipped due to no interface mapping
    errors = 0
    sequence = 1

    for sophos_rule in rules:
        name = sophos_rule.get('name', 'Unnamed')
        enabled = sophos_rule.get('enabled', True)
        action = sophos_rule.get('action', 'drop')
        log = sophos_rule.get('log', False)
        comment = sophos_rule.get('comment', '')

        # Map sources
        sources = sophos_rule.get('sources', [])
        source_nets = []
        for src in sources:
            mapped = map_source_destination(src, existing_aliases)
            if mapped not in source_nets:
                source_nets.append(mapped)
        if not source_nets:
            source_nets = ['any']

        # Map destinations
        destinations = sophos_rule.get('destinations', [])
        dest_nets = []
        for dst in destinations:
            mapped = map_source_destination(dst, existing_aliases)
            if mapped not in dest_nets:
                dest_nets.append(mapped)
        if not dest_nets:
            dest_nets = ['any']

        # Map services - collect all ports
        services = sophos_rule.get('services', [])
        protocol = 'any'
        dest_ports = []

        for svc in services:
            proto, port = map_service(svc, existing_aliases)
            if proto != 'any':
                protocol = proto
            if port:
                dest_ports.append(port)

        try:
            # Create description from Sophos name and comment
            description = name[:50]
            if comment:
                description = f"{name[:30]}: {comment[:50]}"

            # Map action
            action_val = 'pass' if action == 'accept' else 'block'

            # Handle multiple ports by creating port alias
            dest_port = None
            if len(dest_ports) == 1:
                dest_port = dest_ports[0]
            elif len(dest_ports) > 1:
                group_name = f"port_{name[:18]}_{sophos_rule['ref_id'][-6:]}"
                dest_port = create_port_alias(client, group_name, dest_ports, existing_aliases)
                if dest_port is None:
                    # Fallback to first port
                    dest_port = dest_ports[0]
                    print(f"  ? Could not create port group for {name[:30]}, using first port")

            # If port is specified, we need TCP or UDP protocol
            if dest_port and protocol == 'any':
                protocol = 'TCP'

            # Handle multiple sources/destinations by creating alias groups
            if len(source_nets) == 1:
                source_net = source_nets[0]
            elif len(source_nets) > 1:
                group_name = f"src_{name[:20]}_{sophos_rule['ref_id'][-6:]}"
                source_net = create_alias_group(client, group_name, source_nets, existing_aliases)
                if source_net is None:
                    source_net = 'any'
                    print(f"  ? Could not create source group for {name[:30]}, using 'any'")

            if len(dest_nets) == 1:
                dest_net = dest_nets[0]
            elif len(dest_nets) > 1:
                group_name = f"dst_{name[:20]}_{sophos_rule['ref_id'][-6:]}"
                dest_net = create_alias_group(client, group_name, dest_nets, existing_aliases)
                if dest_net is None:
                    dest_net = 'any'
                    print(f"  ? Could not create dest group for {name[:30]}, using 'any'")

            # Determine interface from mapping
            interface = determine_interface(sophos_rule, interface_mapping, subnet_lookup)

            # Skip rule if no interface mapping found
            if interface is None:
                skipped += 1
                src_names = ', '.join(s.get('name', '') for s in sophos_rule.get('sources', []))
                dst_names = ', '.join(d.get('name', '') for d in sophos_rule.get('destinations', []))
                print(f"  ~ Skipped: {name[:35]} (src: {src_names[:30]}, dst: {dst_names[:30]})")
                skipped_rules.append({
                    'name': name,
                    'sources': [s.get('name', '') for s in sophos_rule.get('sources', [])],
                    'destinations': [d.get('name', '') for d in sophos_rule.get('destinations', [])]
                })
                continue

            # Build rule data directly for API
            rule_data = {
                'enabled': '1' if enabled else '0',
                'sequence': str(sequence),
                'action': action_val,
                'interface': interface,
                'direction': 'in',
                'ipprotocol': 'inet',
                'protocol': protocol.upper() if protocol not in ['any', 'ICMP'] else protocol,
                'source_net': source_net,
                'destination_net': dest_net,
                'log': '1' if log else '0',
                'description': description[:255]
            }

            # Add destination port if specified (only for TCP/UDP)
            if dest_port and protocol.upper() in ['TCP', 'UDP', 'TCP/UDP']:
                rule_data['destination_port'] = str(dest_port)

            result = client._post('firewall/filter/addRule', {'rule': rule_data})

            if result and result.get('uuid'):
                imported[sophos_rule['ref_id']] = result['uuid']
                action_str = "PASS" if action == "accept" else "BLOCK"
                print(f"  + [{action_str}] [{interface}] {description[:35]}")
                sequence += 1
            else:
                # Get validation errors
                validations = result.get('validations', {}) if result else {}
                if validations:
                    err_msg = "; ".join([f"{k}: {v}" for k, v in validations.items()])
                    print(f"  ! Failed: {name[:30]} - {err_msg[:60]}")
                else:
                    print(f"  ! Failed: {name[:30]} (no details)")
                errors += 1
        except Exception as e:
            print(f"  ! Error importing rule {name}: {e}")
            errors += 1

    print(f"  Rules: {len(imported)} imported, {skipped} skipped, {errors} errors")

    # Show skipped rules summary
    if skipped_rules:
        print(f"\n=== Skipped rules (no interface mapping) ===")
        for rule in skipped_rules:
            sources = ', '.join(rule['sources'][:2])
            if len(rule['sources']) > 2:
                sources += f" (+{len(rule['sources']) - 2})"
            dests = ', '.join(rule['destinations'][:2])
            if len(rule['destinations']) > 2:
                dests += f" (+{len(rule['destinations']) - 2})"
            print(f"  - {rule['name'][:40]}")
            print(f"      src: {sources[:50]}")
            print(f"      dst: {dests[:50]}")

    return imported


def delete_all_dnat_rules(client: Client) -> int:
    """Delete all existing DNAT/port forward rules."""
    print("\n=== Deleting existing DNAT rules ===")

    result = client.firewall_dnat_search_rule()
    deleted = 0

    for rule in result.rows:
        try:
            client.firewall_dnat_del_rule(str(rule.uuid))
            deleted += 1
        except Exception as e:
            print(f"  ! Error deleting DNAT rule: {e}")

    print(f"  Deleted {deleted} DNAT rules")
    return deleted


def resolve_dnat_service(service: dict, service_groups: list, existing_aliases: dict, client: Client) -> tuple:
    """Resolve a DNAT service to (protocol, port_str).

    For service groups, creates a port alias and returns the alias name.
    Returns (protocol, port_or_alias) tuple.
    Port ranges use dash format (e.g., '44300-44400') for DNAT rules.
    """
    name = service.get('name', '')
    dst_low = service.get('dst_low')
    dst_high = service.get('dst_high')
    port = service.get('port', '')

    # "Any" service
    if name == 'Any':
        return ('', '')

    # Service with direct port info
    if dst_low:
        proto = 'TCP'
        if 'udp' in name.lower():
            proto = 'UDP'
        if dst_high and dst_low != dst_high:
            return (proto, f"{dst_low}-{dst_high}")
        return (proto, str(dst_low))

    if port:
        proto = 'TCP'
        if 'udp' in name.lower():
            proto = 'UDP'
        return (proto, port)

    # Try to resolve as service group
    ref_id = service.get('ref_id', '')
    for group in service_groups:
        if group.get('ref_id') == ref_id or group.get('name') == name:
            members = group.get('members', [])
            if not members:
                break
            ports = []
            proto = 'TCP'
            for member in members:
                m_low = member.get('dst_low')
                m_high = member.get('dst_high')
                if m_low:
                    if m_high and m_low != m_high:
                        ports.append(f"{m_low}-{m_high}")
                    else:
                        ports.append(str(m_low))
                    if 'udp' in member.get('name', '').lower():
                        proto = 'UDP'
            if ports:
                if len(ports) == 1:
                    return (proto, ports[0])
                # Create port alias
                alias_name = create_port_alias(client, f"dnat_{slugify(name)}", ports, existing_aliases)
                if alias_name:
                    return (proto, alias_name)
                return (proto, ports[0])
            break

    # Fallback: try to extract port from name
    port_match = re.search(r'(\d+)', name)
    if port_match:
        proto = 'TCP'
        if 'udp' in name.lower():
            proto = 'UDP'
        return (proto, port_match.group(1))

    return ('any', '')


def import_dnat_rules(client: Client, existing_aliases: dict, rules: list,
                      service_groups: list, interface_mapping: dict, subnet_lookup: list) -> dict:
    """Import DNAT/port forward rules."""
    print(f"\n=== Importing {len(rules)} DNAT rules ===")

    imported = {}
    skipped = 0
    skipped_rules = []
    errors = 0
    sequence = 1

    for sophos_rule in rules:
        ref_id = sophos_rule.get('ref_id', '')
        enabled = sophos_rule.get('enabled', True)
        log = sophos_rule.get('log', False)
        comment = sophos_rule.get('comment', '')
        group = sophos_rule.get('group', '')

        source = sophos_rule.get('source', {})
        service = sophos_rule.get('service', {})
        destination = sophos_rule.get('destination', {})
        nat_destination = sophos_rule.get('nat_destination')
        nat_service = sophos_rule.get('nat_service')

        # Skip rules without nat_destination AND without nat_service
        # These are routing/allow rules, not actual port forwards
        if nat_destination is None and nat_service is None:
            src_name = source.get('name', '')
            dst_name = destination.get('name', '')
            svc_name = service.get('name', '')
            print(f"  ~ Skipped (no NAT): {src_name[:20]} -> {dst_name[:20]} [{svc_name[:15]}]")
            skipped_rules.append({'ref_id': ref_id, 'reason': 'no NAT target',
                                  'source': src_name, 'destination': dst_name})
            skipped += 1
            continue

        # Determine interface (where traffic enters)
        source_name = source.get('name', '')
        source_addr = source.get('address', '')

        interface = 'wan'
        if source_name in interface_mapping and interface_mapping[source_name]:
            interface = interface_mapping[source_name]
        elif source_addr and source_addr != '0.0.0.0':
            iface = lookup_interface_by_ip(source_addr, subnet_lookup)
            if iface:
                interface = iface

        # Map source network
        source_net = 'any'
        source_mask = source.get('netmask', '')
        if source_name in ('Any', 'Internet IPv4'):
            source_net = 'any'
        elif source_addr:
            if source_mask and source_mask not in ('0', '32'):
                source_net = f"{source_addr}/{source_mask}"
            elif source_mask == '0':
                source_net = 'any'
            else:
                source_net = source_addr
        else:
            alias = slugify(source_name)
            if alias in existing_aliases:
                source_net = alias

        # Map destination (external IP to match)
        dst_name = destination.get('name', '')
        dst_addr = destination.get('address', '')
        dst_mask = destination.get('netmask', '')

        destination_net = 'any'
        if dst_name in ('Any', 'Internet IPv4'):
            destination_net = 'any'
        elif dst_addr:
            if dst_mask and dst_mask not in ('0', '32'):
                destination_net = f"{dst_addr}/{dst_mask}"
            elif dst_mask == '0':
                destination_net = 'any'
            else:
                destination_net = dst_addr
        else:
            alias = slugify(dst_name)
            if alias in existing_aliases:
                destination_net = alias

        # Resolve service (external port to match)
        protocol, dest_port = resolve_dnat_service(service, service_groups, existing_aliases, client)

        # Map target (internal IP to forward to)
        target = ''
        if nat_destination:
            target = nat_destination.get('address', '')

        # Map local port (internal port)
        # Default: same as external port (leave empty for OPNsense to use dest port)
        local_port = ''
        if nat_service:
            nat_port = nat_service.get('port', '')
            if nat_port:
                local_port = nat_port
            elif nat_service.get('dst_low'):
                local_port = str(nat_service['dst_low'])

        # Build description
        desc_parts = []
        if group:
            desc_parts.append(f"[{group}]")
        if nat_destination:
            desc_parts.append(nat_destination.get('name', ''))
        elif nat_service:
            desc_parts.append(f"port redirect {nat_service.get('name', '')}")
        if comment:
            desc_parts.append(f"- {comment}")
        description = ' '.join(desc_parts).strip()[:255] or f"DNAT {ref_id[-8:]}"

        try:
            # Protocol: empty string for 'any', lowercase for named protocols
            proto_val = protocol.lower() if protocol else ''
            if proto_val == 'any':
                proto_val = ''

            rule_data = {
                'disabled': '0' if enabled else '1',
                'sequence': str(sequence),
                'interface': interface,
                'ipprotocol': 'inet',
                'protocol': proto_val,
                'source': {
                    'network': source_net,
                    'port': '',
                    'not': '0',
                },
                'destination': {
                    'network': destination_net,
                    'port': str(dest_port) if dest_port else '',
                    'not': '0',
                },
                'target': target,
                'local-port': str(local_port) if local_port else '',
                'log': '1' if log else '0',
                'descr': description,
                'natreflection': 'purenat',
                'pass': 'pass',
            }

            result = client._post('firewall/d_nat/addRule', {'rule': rule_data})

            if result and result.get('uuid'):
                imported[ref_id] = result['uuid']
                target_str = f"{target}:{local_port}" if local_port else target
                port_str = f":{dest_port}" if dest_port else ''
                print(f"  + [{interface}] {destination_net[:18]}{port_str} => {target_str} ({description[:35]})")
                sequence += 1
            else:
                validations = result.get('validations', {}) if result else {}
                if validations:
                    err_msg = "; ".join([f"{k}: {v}" for k, v in validations.items()])
                    print(f"  ! Failed: {description[:30]} - {err_msg[:80]}")
                else:
                    print(f"  ! Failed: {description[:30]} (no details: {result})")
                errors += 1
        except Exception as e:
            print(f"  ! Error: {description[:30]} - {e}")
            errors += 1

    print(f"  DNAT rules: {len(imported)} imported, {skipped} skipped, {errors} errors")

    if skipped_rules:
        print(f"\n=== Skipped DNAT rules (no NAT target) ===")
        for rule in skipped_rules:
            print(f"  - {rule['source'][:30]} -> {rule['destination'][:30]}")

    return imported


def delete_all_snat_rules(client: Client) -> int:
    """Delete all existing SNAT/outbound NAT rules."""
    print("\n=== Deleting existing SNAT rules ===")

    result = client.firewall_snat_search_rule()
    deleted = 0

    for rule in result.rows:
        try:
            client.firewall_snat_del_rule(str(rule.uuid))
            deleted += 1
        except Exception as e:
            print(f"  ! Error deleting SNAT rule: {e}")

    print(f"  Deleted {deleted} SNAT rules")
    return deleted


def resolve_outgoing_interface(sophos_name: str, available_interfaces: dict) -> str:
    """Map Sophos outgoing interface name to OPNsense interface key.

    Matches by display name (e.g., "Internet" -> "opt4").
    Falls back to 'wan' if no match found.
    """
    for key, display_name in available_interfaces.items():
        if display_name.lower() == sophos_name.lower():
            return key
    return 'wan'


def import_snat_rules(client: Client, existing_aliases: dict, rules: list,
                      available_interfaces: dict) -> dict:
    """Import SNAT/outbound NAT rules."""
    print(f"\n=== Importing {len(rules)} SNAT rules ===")

    imported = {}
    skipped = 0
    errors = 0
    sequence = 1

    for sophos_rule in rules:
        ref_id = sophos_rule.get('ref_id', '')
        enabled = sophos_rule.get('enabled', True)
        comment = sophos_rule.get('comment', '')

        source = sophos_rule.get('source', {})
        outgoing_iface = sophos_rule.get('outgoing_interface', {})
        outgoing_addr = sophos_rule.get('outgoing_address')

        source_name = source.get('name', '')
        source_addr = source.get('address', '')
        source_mask = source.get('netmask', '')

        # Map source network
        source_net = 'any'
        if source_addr:
            if source_mask and source_mask not in ('0', '32'):
                source_net = f"{source_addr}/{source_mask}"
            elif source_mask == '0':
                source_net = 'any'
            else:
                source_net = source_addr
        else:
            # Try alias
            alias = slugify(source_name)
            if alias in existing_aliases:
                source_net = alias
            else:
                print(f"  ~ Skipped: {source_name[:40]} (no address or alias)")
                skipped += 1
                continue

        # Map outgoing interface
        iface_name = outgoing_iface.get('name', 'Internet')
        interface = resolve_outgoing_interface(iface_name, available_interfaces)

        # Map target (NAT address)
        target = 'wanip'
        if outgoing_addr and outgoing_addr.get('address'):
            target = outgoing_addr['address']

        # Build description
        description = source_name
        if comment:
            description = f"{source_name[:40]} - {comment}"
        description = description[:255]

        try:
            rule = SNATRule(
                enabled=enabled,
                sequence=sequence,
                interface=interface,
                ipprotocol=SNATRule.SnatrulesRuleIpprotocolEnum.INET,
                protocol='any',
                source_net=source_net,
                destination_net='any',
                target=target,
                log=False,
                description=description,
            )

            result = client.firewall_snat_add_rule(rule)

            if result and result.uuid:
                imported[ref_id] = str(result.uuid)
                target_str = target if target != 'wanip' else 'WAN IP'
                status = 'ON ' if enabled else 'OFF'
                print(f"  + [{status}] [{interface}] {source_net[:20]} -> {target_str} ({description[:35]})")
                sequence += 1
            else:
                print(f"  ! Failed: {description[:30]} ({result.result if result else 'no response'})")
                errors += 1
        except Exception as e:
            print(f"  ! Error: {description[:30]} - {e}")
            errors += 1

    print(f"  SNAT rules: {len(imported)} imported, {skipped} skipped, {errors} errors")
    return imported


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Import Sophos UTM firewall rules to OPNsense'
    )
    parser.add_argument(
        'mapping_file',
        nargs='?',
        default=str(DEFAULT_MAPPING_FILE),
        help=f'Path to interface mapping JSON file (default: {DEFAULT_MAPPING_FILE.name})'
    )
    args = parser.parse_args()
    mapping_file = Path(args.mapping_file)

    print("=" * 60)
    print("OPNsense Firewall Rules Import")
    print("=" * 60)

    # Connect to OPNsense
    print(f"\nConnecting to OPNsense at {OPNSENSE_URL}...")
    client = Client(
        base_url=OPNSENSE_URL,
        api_key=OPNSENSE_KEY,
        api_secret=OPNSENSE_SECRET,
        verify_cert=False
    )

    # Check available interfaces
    print("\n=== Checking available interfaces ===")
    available_interfaces = get_available_interfaces(client)
    if not available_interfaces:
        print("ERROR: Could not retrieve interfaces from OPNsense!")
        print("Please check API connectivity and permissions.")
        sys.exit(1)

    print(f"Available interfaces in OPNsense:")
    for key, name in available_interfaces.items():
        print(f"  - {key}: {name}")

    # Validate default interface exists
    if DEFAULT_INTERFACE not in available_interfaces:
        print(f"\nERROR: Default interface '{DEFAULT_INTERFACE}' does not exist in OPNsense!")
        print(f"Available interfaces: {', '.join(available_interfaces.keys())}")
        print("\nPlease create the required interfaces in OPNsense first:")
        print("  1. Go to Interfaces > Assignments")
        print("  2. Add and configure the required interfaces")
        print("  3. Run this script again")
        sys.exit(1)

    # Load rules to extract required interfaces
    rules = load_json(INPUT_DIR / 'firewall_rules.json')
    sophos_interfaces = extract_sophos_interfaces(rules)

    # Load interface mapping from JSON file
    print(f"\n=== Loading interface mapping ===")
    interface_mapping = load_interface_mapping(mapping_file)
    if interface_mapping:
        print(f"Loaded {len(interface_mapping)} mappings from {mapping_file}")
    else:
        print(f"No mapping file found: {mapping_file}")

    # Check if all Sophos interfaces have an entry in the mapping (can be empty to skip)
    if sophos_interfaces:
        unmapped = []
        for iface in sorted(sophos_interfaces):
            if iface not in interface_mapping:
                unmapped.append(iface)

        if unmapped:
            print(f"\nERROR: {len(unmapped)} Sophos interface(s) not in mapping file!")
            print("\nMissing entries:")
            for iface in unmapped:
                print(f"  ! {iface}")

            # Update mapping file, preserving existing values
            save_mapping_template(
                mapping_file,
                list(sophos_interfaces),
                unmapped,
                available_interfaces,
                interface_mapping
            )
            print(f"\nRun this script again after editing {mapping_file}")
            sys.exit(1)

    # Count skipped interfaces (empty mapping)
    skipped_interfaces = [k for k, v in interface_mapping.items() if not k.startswith('_') and v == '']
    if skipped_interfaces:
        print(f"\nSkipping {len(skipped_interfaces)} interface(s) with empty mapping:")
        for iface in skipped_interfaces:
            print(f"  - {iface}")

    # Check if mapped interfaces exist in OPNsense (skip empty mappings)
    missing_interfaces = []
    for sophos_name, opnsense_name in interface_mapping.items():
        if sophos_name.startswith('_'):  # Skip comment fields
            continue
        if opnsense_name == '':  # Skip empty mappings
            continue
        if opnsense_name not in available_interfaces:
            missing_interfaces.append(f"{sophos_name} -> {opnsense_name}")

    if missing_interfaces:
        print(f"\nERROR: Required interfaces do not exist in OPNsense:")
        for mapping in missing_interfaces:
            print(f"  ! {mapping}")
        print(f"\nAvailable interfaces: {', '.join(available_interfaces.keys())}")
        print("\nPlease create the required interfaces in OPNsense first:")
        print("  1. Go to Interfaces > Assignments")
        print("  2. Add and configure the missing interfaces")
        print("  3. Run this script again")
        sys.exit(1)

    print(f"\nUsing default interface: {DEFAULT_INTERFACE} ({available_interfaces.get(DEFAULT_INTERFACE, 'Unknown')})")

    # Build subnet lookup for IP-based interface determination
    interface_networks = load_json(INPUT_DIR / 'interface_networks.json')
    subnet_lookup = build_subnet_lookup(interface_networks, interface_mapping)
    print(f"\nBuilt subnet lookup with {len(subnet_lookup)} networks")

    # Load DNAT rules, SNAT rules, and service groups
    dnat_rules = load_json(INPUT_DIR / 'nat_dnat_rules.json')
    snat_rules = load_json(INPUT_DIR / 'nat_snat_rules.json')
    service_groups = load_json(INPUT_DIR / 'service_groups.json')

    # Delete existing rules first
    delete_all_rules(client)
    delete_all_dnat_rules(client)
    delete_all_snat_rules(client)

    # Get existing aliases for reference
    print("\nFetching existing aliases...")
    existing_aliases = get_existing_aliases(client)
    print(f"Found {len(existing_aliases)} aliases for reference")

    # Import firewall rules
    rule_map = import_firewall_rules(client, existing_aliases, rules, interface_mapping, subnet_lookup)

    # Apply firewall filter changes
    print("\n=== Applying firewall configuration ===")
    try:
        result = client.firewall_filter_apply()
        if result and hasattr(result, 'result'):
            print(f"  Configuration applied: {result.result}")
        else:
            print("  Configuration applied")
    except Exception as e:
        print(f"  Warning: Could not apply configuration: {e}")

    # Import DNAT rules
    dnat_map = import_dnat_rules(client, existing_aliases, dnat_rules, service_groups, interface_mapping, subnet_lookup)

    # Apply DNAT changes
    print("\n=== Applying DNAT configuration ===")
    try:
        result = client._post('firewall/d_nat/apply', '')
        status = result.get('status', '') if isinstance(result, dict) else str(result)
        print(f"  DNAT configuration applied: {status.strip()}")
    except Exception as e:
        print(f"  Warning: Could not apply DNAT configuration: {e}")

    # Import SNAT rules
    snat_map = import_snat_rules(client, existing_aliases, snat_rules, available_interfaces)

    # Apply SNAT changes
    print("\n=== Applying SNAT configuration ===")
    try:
        result = client._post('firewall/source_nat/apply', '')
        status = result.get('status', '') if isinstance(result, dict) else str(result)
        print(f"  SNAT configuration applied: {status.strip()}")
    except Exception as e:
        print(f"  Warning: Could not apply SNAT configuration: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"  Firewall rules imported: {len(rule_map)}")
    print(f"  DNAT rules imported:     {len(dnat_map)}")
    print(f"  SNAT rules imported:     {len(snat_map)}")
    print(f"  Default interface used:  {DEFAULT_INTERFACE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
