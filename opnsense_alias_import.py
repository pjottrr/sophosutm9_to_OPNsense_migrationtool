#!/usr/bin/env python3
"""
OPNsense Alias Import Script

Imports Sophos UTM aliases (hosts, networks, services, groups) to OPNsense firewall aliases.

Usage:
    python opnsense_alias_import.py
"""

import json
import re
import sys
from pathlib import Path

# Add local pysense to path
sys.path.insert(0, str(Path(__file__).parent))

from pysense.client import Client
from pysense.pydantic.Alias import Alias
from pysense.pydantic.Category import Category


# OPNsense API credentials
OPNSENSE_URL = "https://192.168.1.1/api"
OPNSENSE_KEY = "your_api_key_here"
OPNSENSE_SECRET = "your_api_secret_here"

# Input directory with Sophos JSON exports
INPUT_DIR = Path(__file__).parent / "output"


def slugify(name: str) -> str:
    """Convert name to valid OPNsense alias name (alphanumeric and underscore only)."""
    # Replace common special chars
    slug = name.replace('-', '_').replace(' ', '_').replace('.', '_')
    # Remove any remaining invalid chars
    slug = re.sub(r'[^a-zA-Z0-9_]', '', slug)
    # Remove consecutive underscores
    slug = re.sub(r'_+', '_', slug)
    # Ensure it starts with a letter (OPNsense requirement)
    if slug and not slug[0].isalpha():
        slug = 'a_' + slug
    return slug.strip('_')[:31]


def load_json(filepath: Path) -> list[dict]:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_existing_aliases(client: Client) -> dict:
    """Get existing aliases and return a dict by name."""
    # Use raw API to get aliases, bypassing the pydantic parsing issue
    data = client._get('firewall/alias/search_item')
    existing = {}
    if data and 'rows' in data:
        for row in data['rows']:
            # The 'uuid' field in search results is the actual UUID
            existing[row['name']] = row['uuid']
    return existing


def delete_all_aliases(client: Client) -> int:
    """Delete all non-system aliases. Deletes in multiple passes to handle dependencies."""
    print("\n=== Deleting existing aliases ===")

    # System aliases that should not be deleted (start with __ or are built-in)
    system_prefixes = ('__', 'bogons', 'sshlockout', 'virusprot')

    total_deleted = 0
    pass_num = 0
    max_passes = 5  # Prevent infinite loops

    while pass_num < max_passes:
        pass_num += 1
        existing = get_existing_aliases(client)

        # Filter out system aliases
        to_delete = {name: uuid for name, uuid in existing.items()
                     if not name.startswith(system_prefixes)}

        if not to_delete:
            break

        deleted_this_pass = 0
        for name, uuid in to_delete.items():
            try:
                result = client._post(f'firewall/alias/del_item/{uuid}', {})
                if result and result.get('result') == 'deleted':
                    deleted_this_pass += 1
                    total_deleted += 1
            except Exception:
                pass  # Will retry in next pass

        print(f"  Pass {pass_num}: deleted {deleted_this_pass} aliases")

        if deleted_this_pass == 0:
            # No progress, remaining aliases might be in use by something else
            break

    remaining = len(get_existing_aliases(client)) - len([n for n in get_existing_aliases(client) if n.startswith(system_prefixes)])
    if remaining > 0:
        print(f"  Note: {remaining} aliases could not be deleted (may be in use)")

    print(f"  Total deleted: {total_deleted} aliases")
    return total_deleted


def get_existing_categories(client: Client) -> dict:
    """Get existing categories and return a dict by name."""
    data = client._get('firewall/category/search_item')
    existing = {}
    if data and 'rows' in data:
        for row in data['rows']:
            existing[row['name']] = row['uuid']
    return existing


def ensure_categories(client: Client) -> dict:
    """Ensure required categories exist and return a dict with their UUIDs."""
    print("\n=== Setting up categories ===")

    # Define categories with colors (no spaces in names, use simple color names)
    required_categories = {
        'Hosts': 'text-primary',           # Blue
        'Networks': 'text-success',         # Green
        'Ports': 'text-warning',            # Orange
        'NetworkGroups': 'text-info',       # Cyan
        'ServiceGroups': 'text-danger',     # Red
    }

    existing = get_existing_categories(client)
    category_uuids = {}

    for cat_name, color in required_categories.items():
        if cat_name in existing:
            category_uuids[cat_name] = existing[cat_name]
            print(f"  Category exists: {cat_name}")
        else:
            try:
                category = Category(
                    name=cat_name
                )
                result = client.firewall_category_add_item(category)
                if result and hasattr(result, 'uuid') and result.uuid:
                    category_uuids[cat_name] = result.uuid
                    print(f"  + Created category: {cat_name}")
                elif result and hasattr(result, 'result') and result.result == 'saved':
                    # Fetch the UUID from existing categories after save
                    updated = get_existing_categories(client)
                    if cat_name in updated:
                        category_uuids[cat_name] = updated[cat_name]
                        print(f"  + Created category: {cat_name}")
                    else:
                        print(f"  ! Failed to get UUID for category: {cat_name}")
                else:
                    print(f"  ! Failed to create category: {cat_name} (result: {result})")
            except Exception as e:
                print(f"  ! Error creating category {cat_name}: {e}")

    return category_uuids


def import_hosts(client: Client, existing_aliases: dict, category_uuid: str = None) -> dict:
    """Import hosts as host-type aliases."""
    hosts = load_json(INPUT_DIR / 'hosts.json')
    print(f"\n=== Importing {len(hosts)} hosts ===")

    imported = {}
    skipped = 0
    errors = 0

    for host in hosts:
        name = slugify(host['name'])
        address = host.get('address', '')

        if not name or not address:
            skipped += 1
            continue

        # Skip if already exists
        if name in existing_aliases:
            imported[host['ref_id']] = existing_aliases[name]
            skipped += 1
            continue

        try:
            alias = Alias(
                enabled=True,
                name=name,
                type=Alias.AliasesAliasTypeEnum.HOST,
                content=address,
                categories=[category_uuid] if category_uuid else [],
                description=host.get('comment', '')[:255] if host.get('comment') else f"Sophos host: {host['name']}"
            )

            result = client.firewall_alias_add_item(alias)
            if result and hasattr(result, 'uuid') and result.uuid:
                imported[host['ref_id']] = result.uuid
                print(f"  + Host: {name} -> {address}")
            else:
                print(f"  ! Failed to import host: {name} (result: {result})")
                errors += 1
        except Exception as e:
            print(f"  ! Error importing host {name}: {e}")
            errors += 1

    print(f"  Hosts: {len(imported)} imported, {skipped} skipped, {errors} errors")
    return imported


def import_networks(client: Client, existing_aliases: dict, category_uuid: str = None) -> dict:
    """Import networks as network-type aliases."""
    networks = load_json(INPUT_DIR / 'networks.json')
    print(f"\n=== Importing {len(networks)} networks ===")

    imported = {}
    skipped = 0
    errors = 0

    for network in networks:
        name = slugify(network['name'])
        address = network.get('address', '')
        netmask = network.get('netmask', '32')

        if not name or not address:
            skipped += 1
            continue

        # Skip special networks like "Internet IPv4" (0.0.0.0/0)
        if address == '0.0.0.0' and netmask == '0':
            skipped += 1
            continue

        # Skip if already exists
        if name in existing_aliases:
            imported[network['ref_id']] = existing_aliases[name]
            skipped += 1
            continue

        try:
            cidr = f"{address}/{netmask}"

            alias = Alias(
                enabled=True,
                name=name,
                type=Alias.AliasesAliasTypeEnum.NETWORK,
                content=cidr,
                categories=[category_uuid] if category_uuid else [],
                description=network.get('comment', '')[:255] if network.get('comment') else f"Sophos network: {network['name']}"
            )

            result = client.firewall_alias_add_item(alias)
            if result and hasattr(result, 'uuid') and result.uuid:
                imported[network['ref_id']] = result.uuid
                print(f"  + Network: {name} -> {cidr}")
            else:
                print(f"  ! Failed to import network: {name}")
                errors += 1
        except Exception as e:
            print(f"  ! Error importing network {name}: {e}")
            errors += 1

    print(f"  Networks: {len(imported)} imported, {skipped} skipped, {errors} errors")
    return imported


def import_services(client: Client, existing_aliases: dict, category_uuid: str = None) -> dict:
    """Import services as port-type aliases."""
    services = load_json(INPUT_DIR / 'services.json')
    print(f"\n=== Importing {len(services)} services ===")

    imported = {}
    skipped = 0
    errors = 0

    for service in services:
        name = slugify(service['name'])
        port = service.get('port', '')
        protocol = service.get('protocol', 'tcp')

        if not name or not port:
            skipped += 1
            continue

        # Skip if already exists
        if name in existing_aliases:
            imported[service['ref_id']] = existing_aliases[name]
            skipped += 1
            continue

        try:
            # Handle port ranges
            dst_low = service.get('dst_low')
            dst_high = service.get('dst_high')

            if dst_low and dst_high and dst_low != dst_high:
                port_content = f"{dst_low}:{dst_high}"
            else:
                port_content = str(port)

            alias = Alias(
                enabled=True,
                name=name,
                type=Alias.AliasesAliasTypeEnum.PORT,
                content=port_content,
                categories=[category_uuid] if category_uuid else [],
                description=service.get('comment', '')[:255] if service.get('comment') else f"Sophos service: {service['name']} ({protocol})"
            )

            result = client.firewall_alias_add_item(alias)
            if result and hasattr(result, 'uuid') and result.uuid:
                imported[service['ref_id']] = result.uuid
                print(f"  + Service: {name} -> {port_content} ({protocol})")
            else:
                print(f"  ! Failed to import service: {name}")
                errors += 1
        except Exception as e:
            print(f"  ! Error importing service {name}: {e}")
            errors += 1

    print(f"  Services: {len(imported)} imported, {skipped} skipped, {errors} errors")
    return imported


def import_network_groups(client: Client, existing_aliases: dict, host_map: dict, network_map: dict, category_uuid: str = None) -> dict:
    """Import network groups as networkgroup-type aliases."""
    groups = load_json(INPUT_DIR / 'network_groups.json')
    print(f"\n=== Importing {len(groups)} network groups ===")

    imported = {}
    skipped = 0
    errors = 0

    # Get updated existing aliases (to include newly created ones)
    all_aliases = get_existing_aliases(client)

    for group in groups:
        name = slugify(group['name'])
        members = group.get('members', [])

        if not name:
            skipped += 1
            continue

        # Skip empty groups
        if not members:
            skipped += 1
            continue

        # Skip if already exists
        if name in existing_aliases:
            imported[group['ref_id']] = existing_aliases[name]
            skipped += 1
            continue

        try:
            # Collect member addresses/aliases
            content_items = []

            for member in members:
                member_addr = member.get('address', '')
                member_name = slugify(member.get('name', ''))

                # Check if member was imported as an alias
                if member_name in all_aliases:
                    # Reference the alias by name
                    content_items.append(member_name)
                elif member_addr:
                    # Use the address directly
                    content_items.append(member_addr)

            if not content_items:
                skipped += 1
                continue

            # Join multiple items with newline
            content = '\n'.join(content_items)

            alias = Alias(
                enabled=True,
                name=name,
                type=Alias.AliasesAliasTypeEnum.NETWORKGROUP,
                content=content,
                categories=[category_uuid] if category_uuid else [],
                description=group.get('comment', '')[:255] if group.get('comment') else f"Sophos network group: {group['name']}"
            )

            result = client.firewall_alias_add_item(alias)
            if result and hasattr(result, 'uuid') and result.uuid:
                imported[group['ref_id']] = result.uuid
                print(f"  + Network group: {name} ({len(content_items)} members)")
            else:
                print(f"  ! Failed to import network group: {name}")
                errors += 1
        except Exception as e:
            print(f"  ! Error importing network group {name}: {e}")
            errors += 1

    print(f"  Network groups: {len(imported)} imported, {skipped} skipped, {errors} errors")
    return imported


def import_service_groups(client: Client, existing_aliases: dict, service_map: dict, category_uuid: str = None) -> dict:
    """Import service groups as port-type aliases with multiple ports."""
    groups = load_json(INPUT_DIR / 'service_groups.json')
    print(f"\n=== Importing {len(groups)} service groups ===")

    imported = {}
    skipped = 0
    errors = 0

    # Get updated existing aliases
    all_aliases = get_existing_aliases(client)

    for group in groups:
        name = slugify(group['name'])
        members = group.get('members', [])

        if not name:
            skipped += 1
            continue

        # Skip empty groups
        if not members:
            skipped += 1
            continue

        # Skip if already exists
        if name in existing_aliases:
            imported[group['ref_id']] = existing_aliases[name]
            skipped += 1
            continue

        try:
            # Collect member ports
            content_items = []

            for member in members:
                member_port = member.get('port', '')
                member_name = slugify(member.get('name', ''))
                dst_low = member.get('dst_low')
                dst_high = member.get('dst_high')

                # Check if member was imported as an alias
                if member_name in all_aliases:
                    content_items.append(member_name)
                elif dst_low and dst_high and dst_low != dst_high:
                    content_items.append(f"{dst_low}:{dst_high}")
                elif member_port:
                    content_items.append(str(member_port))

            if not content_items:
                skipped += 1
                continue

            # Join multiple items with newline
            content = '\n'.join(content_items)

            alias = Alias(
                enabled=True,
                name=name,
                type=Alias.AliasesAliasTypeEnum.PORT,
                content=content,
                categories=[category_uuid] if category_uuid else [],
                description=group.get('comment', '')[:255] if group.get('comment') else f"Sophos service group: {group['name']}"
            )

            result = client.firewall_alias_add_item(alias)
            if result and hasattr(result, 'uuid') and result.uuid:
                imported[group['ref_id']] = result.uuid
                print(f"  + Service group: {name} ({len(content_items)} ports)")
            else:
                print(f"  ! Failed to import service group: {name}")
                errors += 1
        except Exception as e:
            print(f"  ! Error importing service group {name}: {e}")
            errors += 1

    print(f"  Service groups: {len(imported)} imported, {skipped} skipped, {errors} errors")
    return imported


def main():
    print("=" * 60)
    print("OPNsense Alias Import")
    print("=" * 60)

    # Connect to OPNsense
    print(f"\nConnecting to OPNsense at {OPNSENSE_URL}...")
    client = Client(
        base_url=OPNSENSE_URL,
        api_key=OPNSENSE_KEY,
        api_secret=OPNSENSE_SECRET,
        verify_cert=False
    )

    # Delete existing aliases first
    delete_all_aliases(client)

    # Ensure categories exist
    category_uuids = ensure_categories(client)

    # Get existing aliases (should be mostly empty now, except system aliases)
    print("\nFetching existing aliases...")
    existing_aliases = get_existing_aliases(client)
    print(f"Found {len(existing_aliases)} existing aliases")

    # Import in order (hosts/networks first, then groups that reference them)
    host_map = import_hosts(client, existing_aliases, category_uuids.get('Hosts'))
    network_map = import_networks(client, existing_aliases, category_uuids.get('Networks'))
    service_map = import_services(client, existing_aliases, category_uuids.get('Ports'))

    # Refresh existing aliases after importing base items
    existing_aliases = get_existing_aliases(client)

    # Import groups
    network_group_map = import_network_groups(client, existing_aliases, host_map, network_map, category_uuids.get('NetworkGroups'))
    service_group_map = import_service_groups(client, existing_aliases, service_map, category_uuids.get('ServiceGroups'))

    # Apply changes
    print("\n=== Applying configuration ===")
    try:
        # Use the reconfigure endpoint via POST
        result = client._post('firewall/alias/reconfigure', {})
        print("  Configuration applied successfully")
    except Exception as e:
        print(f"  Note: Reconfigure step skipped: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"  Categories created:      {len(category_uuids)}")
    print(f"  Hosts imported:          {len(host_map)}")
    print(f"  Networks imported:       {len(network_map)}")
    print(f"  Services imported:       {len(service_map)}")
    print(f"  Network groups imported: {len(network_group_map)}")
    print(f"  Service groups imported: {len(service_group_map)}")
    print(f"  Total aliases:           {len(host_map) + len(network_map) + len(service_map) + len(network_group_map) + len(service_group_map)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
