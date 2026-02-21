#!/usr/bin/env python3
"""
Sophos UTM 9 Configuration Parser

Parses webadmin-sanitized.xml and exports configuration to separate JSON files:
- interfaces.json
- hosts.json
- networks.json
- network_groups.json
- services.json
- service_groups.json
- firewall_rules.json
- nat_rules.json (SNAT/masquerading + DNAT)
- waf_frontends.json
- waf_backends.json
"""

import json
import re
from pathlib import Path
from typing import Any

try:
    from lxml import etree as ET
    USING_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    USING_LXML = False


class ReferenceResolver:
    """Builds and resolves REF_* references to actual names/values."""

    def __init__(self):
        self.refs: dict[str, dict[str, Any]] = {}

    def add(self, ref_id: str, data: dict[str, Any]):
        """Add a reference to the lookup table."""
        self.refs[ref_id] = data

    def get_name(self, ref_id: str) -> str:
        """Get the name for a reference, or return the ref_id if not found."""
        if ref_id in self.refs:
            return self.refs[ref_id].get('name', ref_id)
        return ref_id

    def get(self, ref_id: str) -> dict[str, Any] | None:
        """Get full data for a reference."""
        return self.refs.get(ref_id)

    def get_object(self, ref_id: str) -> dict[str, Any]:
        """Get full object for a reference, or minimal object if not found."""
        if ref_id in self.refs:
            return self.refs[ref_id].copy()
        return {'ref_id': ref_id, 'name': ref_id}

    def resolve_ref_list(self, ref_ids: list[str]) -> list[str]:
        """Resolve a list of references to their names."""
        return [self.get_name(ref_id) for ref_id in ref_ids]

    def resolve_ref_list_to_objects(self, ref_ids: list[str]) -> list[dict[str, Any]]:
        """Resolve a list of references to their full objects."""
        return [self.get_object(ref_id) for ref_id in ref_ids]


class SophosParser:
    """Parser for Sophos UTM 9 XML configuration."""

    def __init__(self, xml_path: str):
        self.xml_path = Path(xml_path)

        # Use lxml with recovery mode to handle malformed XML
        if USING_LXML:
            parser = ET.XMLParser(recover=True)
            self.tree = ET.parse(xml_path, parser)
        else:
            # Fallback: try to fix common issues before parsing
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Fix known typo in Sophos exports
            content = content.replace('</liense>', '</license>')
            import io
            self.tree = ET.parse(io.StringIO(content))

        self.root = self.tree.getroot()
        self.resolver = ReferenceResolver()

        # Output containers
        self.interfaces: list[dict] = []
        self.hosts: list[dict] = []
        self.networks: list[dict] = []
        self.network_groups: list[dict] = []
        self.interface_addresses: list[dict] = []
        self.interface_networks: list[dict] = []
        self.services: list[dict] = []
        self.service_groups: list[dict] = []
        self.firewall_rules: list[dict] = []
        self.nat_snat_rules: list[dict] = []
        self.nat_dnat_rules: list[dict] = []
        self.waf_frontends: list[dict] = []
        self.waf_backends: list[dict] = []
        self.waf_locations: list[dict] = []

    def parse_all(self):
        """Parse all configuration sections."""
        # First pass: build reference table
        self._build_reference_table()

        # Second pass: extract with resolved references
        self._parse_interfaces()
        self._parse_network_objects()
        self._parse_services()
        self._parse_firewall_rules()
        self._parse_nat_rules()
        self._parse_waf()

    def _get_content(self, element: ET.Element | None) -> str:
        """Get text content from an element."""
        if element is None:
            return ""
        content = element.find('content')
        if content is not None and content.text:
            return content.text.strip()
        return ""

    def _get_attr_content(self, parent: ET.Element, attr_name: str) -> str:
        """Get content from an attr element by name."""
        elem = parent.find(f".//{attr_name}[@attr='1']")
        if elem is not None:
            content = elem.find('content')
            if content is not None and content.text:
                return content.text.strip()
        return ""

    def _get_array_refs(self, parent: ET.Element, array_name: str) -> list[str]:
        """Get list of REF IDs from an array element."""
        refs = []
        array_elem = parent.find(f".//{array_name}[@array='1']")
        if array_elem is not None:
            for content in array_elem.findall('content'):
                if content.text:
                    refs.append(content.text.strip())
        return refs

    def _get_array_values(self, parent: ET.Element, array_name: str) -> list[str]:
        """Get list of plain values from an array element."""
        values = []
        array_elem = parent.find(f".//{array_name}[@array='1']")
        if array_elem is not None:
            for content in array_elem.findall('content'):
                if content.text:
                    values.append(content.text.strip())
        return values

    def _get_ref_from_attr(self, parent: ET.Element, attr_name: str) -> str:
        """Get a reference ID from an attr element."""
        elem = parent.find(f".//{attr_name}[@attr='1']")
        if elem is not None:
            content = elem.find('content')
            if content is not None and content.text:
                return content.text.strip()
        return ""

    def _build_reference_table(self):
        """First pass: build lookup table of all REF_* objects with full details."""
        # Find all elements with object="1" attribute (these are the actual definitions)
        for obj in self.root.iter():
            if obj.get('object') == '1':
                ref_id = obj.tag
                content = obj.find('content')
                if content is not None:
                    name = self._get_attr_content(content, 'name')
                    address = self._get_attr_content(content, 'address')
                    address6 = self._get_attr_content(content, 'address6')
                    netmask = self._get_attr_content(content, 'netmask')
                    comment = self._get_attr_content(content, 'comment')

                    # Service-specific fields
                    dst_low = self._get_attr_content(content, 'dst_low')
                    dst_high = self._get_attr_content(content, 'dst_high')

                    data = {
                        'ref_id': ref_id,
                        'name': name or ref_id,
                    }

                    # Add address fields if present
                    if address:
                        data['address'] = address
                    if address6:
                        data['address6'] = address6
                    if netmask:
                        data['netmask'] = netmask

                    # Add port fields for services
                    if dst_low:
                        data['dst_low'] = int(dst_low)
                        data['dst_high'] = int(dst_high) if dst_high else int(dst_low)
                        if dst_low == dst_high:
                            data['port'] = dst_low
                        else:
                            data['port'] = f"{dst_low}-{dst_high}"

                    if comment:
                        data['comment'] = comment

                    self.resolver.add(ref_id, data)

    def _parse_interfaces(self):
        """Parse interface definitions."""
        # Find <interface class="1">
        for iface_class in self.root.iter('interface'):
            if iface_class.get('class') != '1':
                continue

            # Find ethernet interfaces
            for eth_type in iface_class.iter('ethernet'):
                if eth_type.get('type') != '1':
                    continue

                for obj in eth_type.findall('./content/*[@object="1"]'):
                    ref_id = obj.tag
                    content = obj.find('content')
                    if content is None:
                        continue

                    name = self._get_attr_content(content, 'name')
                    status = self._get_attr_content(content, 'status')
                    mtu = self._get_attr_content(content, 'mtu')
                    comment = self._get_attr_content(content, 'comment')

                    # Get primary address reference
                    primary_addr_ref = self._get_ref_from_attr(content, 'primary_address')
                    primary_addr = self.resolver.get_name(primary_addr_ref) if primary_addr_ref else ""

                    # Get hardware reference
                    itfhw_ref = self._get_ref_from_attr(content, 'itfhw')

                    self.interfaces.append({
                        'ref_id': ref_id,
                        'name': name,
                        'enabled': status == '1',
                        'mtu': int(mtu) if mtu else 1500,
                        'primary_address_ref': primary_addr_ref,
                        'hardware_ref': itfhw_ref,
                        'comment': comment
                    })

    def _parse_network_objects(self):
        """Parse hosts, networks, groups, and interface addresses."""
        for net_class in self.root.iter('network'):
            if net_class.get('class') != '1':
                continue

            content = net_class.find('content')
            if content is None:
                continue

            # Parse hosts
            for host_type in content.iter('host'):
                if host_type.get('type') != '1':
                    continue
                for obj in host_type.findall('.//content/*[@object="1"]'):
                    self._parse_host(obj)

            # Parse networks
            for net_type in content.iter('network'):
                if net_type.get('type') != '1':
                    continue
                for obj in net_type.findall('.//content/*[@object="1"]'):
                    self._parse_network(obj)

            # Parse network groups
            for group_type in content.iter('group'):
                if group_type.get('type') != '1':
                    continue
                for obj in group_type.findall('.//content/*[@object="1"]'):
                    self._parse_network_group(obj)

            # Parse interface addresses
            for addr_type in content.iter('interface_address'):
                if addr_type.get('type') != '1':
                    continue
                for obj in addr_type.findall('.//content/*[@object="1"]'):
                    self._parse_interface_address(obj)

            # Parse interface networks
            for net_type in content.iter('interface_network'):
                if net_type.get('type') != '1':
                    continue
                for obj in net_type.findall('.//content/*[@object="1"]'):
                    self._parse_interface_network(obj)

    def _parse_host(self, obj: ET.Element):
        """Parse a single host object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        self.hosts.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'address': self._get_attr_content(content, 'address'),
            'address6': self._get_attr_content(content, 'address6'),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_network(self, obj: ET.Element):
        """Parse a single network object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        self.networks.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'address': self._get_attr_content(content, 'address'),
            'netmask': self._get_attr_content(content, 'netmask'),
            'address6': self._get_attr_content(content, 'address6'),
            'netmask6': self._get_attr_content(content, 'netmask6'),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_network_group(self, obj: ET.Element):
        """Parse a single network group object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        member_refs = self._get_array_refs(content, 'members')

        self.network_groups.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'members': self.resolver.resolve_ref_list_to_objects(member_refs),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_interface_address(self, obj: ET.Element):
        """Parse a single interface address object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        self.interface_addresses.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'address': self._get_attr_content(content, 'address'),
            'address6': self._get_attr_content(content, 'address6'),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_interface_network(self, obj: ET.Element):
        """Parse a single interface network object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        self.interface_networks.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'address': self._get_attr_content(content, 'address'),
            'netmask': self._get_attr_content(content, 'netmask'),
            'address6': self._get_attr_content(content, 'address6'),
            'netmask6': self._get_attr_content(content, 'netmask6'),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_services(self):
        """Parse service definitions."""
        for svc_class in self.root.iter('service'):
            if svc_class.get('class') != '1':
                continue

            content = svc_class.find('content')
            if content is None:
                continue

            # Parse TCP services
            for tcp_type in content.iter('tcp'):
                if tcp_type.get('type') != '1':
                    continue
                for obj in tcp_type.findall('.//content/*[@object="1"]'):
                    self._parse_service(obj, 'tcp')

            # Parse UDP services
            for udp_type in content.iter('udp'):
                if udp_type.get('type') != '1':
                    continue
                for obj in udp_type.findall('.//content/*[@object="1"]'):
                    self._parse_service(obj, 'udp')

            # Parse TCP/UDP services
            for tcpudp_type in content.iter('tcpudp'):
                if tcpudp_type.get('type') != '1':
                    continue
                for obj in tcpudp_type.findall('.//content/*[@object="1"]'):
                    self._parse_service(obj, 'tcpudp')

            # Parse service groups
            for group_type in content.iter('group'):
                if group_type.get('type') != '1':
                    continue
                for obj in group_type.findall('.//content/*[@object="1"]'):
                    self._parse_service_group(obj)

    def _parse_service(self, obj: ET.Element, protocol: str):
        """Parse a single service object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        dst_low = self._get_attr_content(content, 'dst_low')
        dst_high = self._get_attr_content(content, 'dst_high')

        # Format port as single port or range
        if dst_low == dst_high:
            port = dst_low
        else:
            port = f"{dst_low}-{dst_high}"

        self.services.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'protocol': protocol,
            'port': port,
            'dst_low': int(dst_low) if dst_low else 0,
            'dst_high': int(dst_high) if dst_high else 0,
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_service_group(self, obj: ET.Element):
        """Parse a single service group object."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        member_refs = self._get_array_refs(content, 'members')

        self.service_groups.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'members': self.resolver.resolve_ref_list_to_objects(member_refs),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_firewall_rules(self):
        """Parse packetfilter (firewall) rules."""
        for pf_class in self.root.iter('packetfilter'):
            if pf_class.get('class') != '1':
                continue

            content = pf_class.find('content')
            if content is None:
                continue

            # Find packetfilter type (firewall rules)
            for pf_type in content.iter('packetfilter'):
                if pf_type.get('type') != '1':
                    continue

                inner_content = pf_type.find('content')
                if inner_content is None:
                    continue

                for obj in inner_content.findall('*[@object="1"]'):
                    self._parse_firewall_rule(obj)

    def _parse_firewall_rule(self, obj: ET.Element):
        """Parse a single firewall rule."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        # Get source, destination, service references
        source_refs = self._get_array_refs(content, 'sources')
        dest_refs = self._get_array_refs(content, 'destinations')
        service_refs = self._get_array_refs(content, 'services')

        self.firewall_rules.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'group') or ref_id,
            'enabled': self._get_attr_content(content, 'status') == '1',
            'action': self._get_attr_content(content, 'action'),
            'sources': self.resolver.resolve_ref_list_to_objects(source_refs),
            'destinations': self.resolver.resolve_ref_list_to_objects(dest_refs),
            'services': self.resolver.resolve_ref_list_to_objects(service_refs),
            'log': self._get_attr_content(content, 'log') == '1',
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_nat_rules(self):
        """Parse NAT rules (masquerading/SNAT and DNAT)."""
        for pf_class in self.root.iter('packetfilter'):
            if pf_class.get('class') != '1':
                continue

            content = pf_class.find('content')
            if content is None:
                continue

            # Parse masquerading (SNAT) rules
            for masq_type in content.iter('masq'):
                if masq_type.get('type') != '1':
                    continue

                inner_content = masq_type.find('content')
                if inner_content is None:
                    continue

                for obj in inner_content.findall('*[@object="1"]'):
                    self._parse_masq_rule(obj)

            # Parse DNAT rules
            for nat_type in content.iter('nat'):
                if nat_type.get('type') != '1':
                    continue

                inner_content = nat_type.find('content')
                if inner_content is None:
                    continue

                for obj in inner_content.findall('*[@object="1"]'):
                    self._parse_dnat_rule(obj)

    def _parse_masq_rule(self, obj: ET.Element):
        """Parse a single masquerading (SNAT) rule."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        source_ref = self._get_ref_from_attr(content, 'source')
        interface_ref = self._get_ref_from_attr(content, 'source_nat_interface')
        additional_addr_ref = self._get_ref_from_attr(content, 'additional_address')

        self.nat_snat_rules.append({
            'ref_id': ref_id,
            'type': 'snat',
            'enabled': self._get_attr_content(content, 'status') == '1',
            'source': self.resolver.get_object(source_ref) if source_ref else None,
            'outgoing_interface': self.resolver.get_object(interface_ref) if interface_ref else None,
            'outgoing_address': self.resolver.get_object(additional_addr_ref) if additional_addr_ref else None,
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_dnat_rule(self, obj: ET.Element):
        """Parse a single DNAT rule."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        source_ref = self._get_ref_from_attr(content, 'source')
        service_ref = self._get_ref_from_attr(content, 'service')
        dest_ref = self._get_ref_from_attr(content, 'destination')
        dest_nat_addr_ref = self._get_ref_from_attr(content, 'destination_nat_address')
        dest_nat_service_ref = self._get_ref_from_attr(content, 'destination_nat_service')

        self.nat_dnat_rules.append({
            'ref_id': ref_id,
            'type': 'dnat',
            'enabled': self._get_attr_content(content, 'status') == '1',
            'group': self._get_attr_content(content, 'group'),
            'source': self.resolver.get_object(source_ref) if source_ref else None,
            'service': self.resolver.get_object(service_ref) if service_ref else None,
            'destination': self.resolver.get_object(dest_ref) if dest_ref else None,
            'nat_destination': self.resolver.get_object(dest_nat_addr_ref) if dest_nat_addr_ref else None,
            'nat_service': self.resolver.get_object(dest_nat_service_ref) if dest_nat_service_ref else None,
            'log': self._get_attr_content(content, 'log') == '1',
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_waf(self):
        """Parse WAF (reverse proxy) configuration."""
        for rp_class in self.root.iter('reverse_proxy'):
            if rp_class.get('class') != '1':
                continue

            content = rp_class.find('content')
            if content is None:
                continue

            # Parse frontends (virtual webservers)
            for frontend_type in content.iter('frontend'):
                if frontend_type.get('type') != '1':
                    continue

                inner_content = frontend_type.find('content')
                if inner_content is None:
                    continue

                for obj in inner_content.findall('*[@object="1"]'):
                    self._parse_waf_frontend(obj)

            # Parse backends (real webservers)
            for backend_type in content.iter('backend'):
                if backend_type.get('type') != '1':
                    continue

                inner_content = backend_type.find('content')
                if inner_content is None:
                    continue

                for obj in inner_content.findall('*[@object="1"]'):
                    self._parse_waf_backend(obj)

            # Parse locations
            for location_type in content.iter('location'):
                if location_type.get('type') != '1':
                    continue

                inner_content = location_type.find('content')
                if inner_content is None:
                    continue

                for obj in inner_content.findall('*[@object="1"]'):
                    self._parse_waf_location(obj)

    def _parse_waf_frontend(self, obj: ET.Element):
        """Parse a single WAF frontend (virtual webserver)."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        address_ref = self._get_ref_from_attr(content, 'address')
        profile_ref = self._get_ref_from_attr(content, 'profile')
        domains = self._get_array_values(content, 'domain')
        exception_refs = self._get_array_refs(content, 'exceptions')

        self.waf_frontends.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'enabled': self._get_attr_content(content, 'status') == '1',
            'type': self._get_attr_content(content, 'type'),
            'port': int(self._get_attr_content(content, 'port') or 443),
            'domains': domains,
            'address': self.resolver.get_object(address_ref) if address_ref else None,
            'profile': self.resolver.get_object(profile_ref) if profile_ref else None,
            'html_rewrite': self._get_attr_content(content, 'htmlrewrite') == '1',
            'implicit_redirect': self._get_attr_content(content, 'implicitredirect') == '1',
            'preserve_host': self._get_attr_content(content, 'preservehost') == '1',
            'exceptions': self.resolver.resolve_ref_list_to_objects(exception_refs),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_waf_backend(self, obj: ET.Element):
        """Parse a single WAF backend (real webserver)."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        host_ref = self._get_ref_from_attr(content, 'host')

        self.waf_backends.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'enabled': self._get_attr_content(content, 'status') == '1',
            'host': self.resolver.get_object(host_ref) if host_ref else None,
            'ssl': self._get_attr_content(content, 'ssl') == '1',
            'port': int(self._get_attr_content(content, 'port') or 80),
            'comment': self._get_attr_content(content, 'comment')
        })

    def _parse_waf_location(self, obj: ET.Element):
        """Parse a single WAF location."""
        ref_id = obj.tag
        content = obj.find('content')
        if content is None:
            return

        # Note: array is named 'backend' not 'backends' in Sophos XML
        backend_refs = self._get_array_refs(content, 'backend')
        allowed_network_refs = self._get_array_refs(content, 'allowed_networks')
        denied_network_refs = self._get_array_refs(content, 'denied_networks')

        self.waf_locations.append({
            'ref_id': ref_id,
            'name': self._get_attr_content(content, 'name'),
            'enabled': self._get_attr_content(content, 'status') == '1',
            'path': self._get_attr_content(content, 'path'),
            'backends': self.resolver.resolve_ref_list_to_objects(backend_refs),
            'sticky_session': self._get_attr_content(content, 'stickysession_status') == '1',
            'hot_standby': self._get_attr_content(content, 'hot_standby') == '1',
            'allowed_networks': self.resolver.resolve_ref_list_to_objects(allowed_network_refs),
            'denied_networks': self.resolver.resolve_ref_list_to_objects(denied_network_refs),
            'comment': self._get_attr_content(content, 'comment')
        })

    def export_json(self, output_dir: str = "."):
        """Export all parsed data to separate JSON files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exports = [
            ('interfaces.json', self.interfaces),
            ('hosts.json', self.hosts),
            ('networks.json', self.networks),
            ('network_groups.json', self.network_groups),
            ('interface_addresses.json', self.interface_addresses),
            ('interface_networks.json', self.interface_networks),
            ('services.json', self.services),
            ('service_groups.json', self.service_groups),
            ('firewall_rules.json', self.firewall_rules),
            ('nat_snat_rules.json', self.nat_snat_rules),
            ('nat_dnat_rules.json', self.nat_dnat_rules),
            ('waf_frontends.json', self.waf_frontends),
            ('waf_backends.json', self.waf_backends),
            ('waf_locations.json', self.waf_locations),
        ]

        for filename, data in exports:
            filepath = output_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Exported {len(data):4d} items to {filepath}")


def main():
    import sys

    xml_file = sys.argv[1] if len(sys.argv) > 1 else "webadmin-sanitized.xml"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

    print(f"Parsing {xml_file}...")
    parser = SophosParser(xml_file)
    parser.parse_all()

    print(f"\nExporting to {output_dir}/...")
    parser.export_json(output_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
