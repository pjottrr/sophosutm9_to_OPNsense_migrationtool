"""
Desired state configuration system for OPNsense.

This module provides a declarative way to define desired network state
and automatically compare/apply changes to OPNsense.

Supports loading state from YAML files. See export_yaml() for format documentation.
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union, TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pysense.base_client import BaseClient
    from pysense.state.handlers.base_handler import EntityHandler


class ChangeType(Enum):
    """Types of state changes detected during planning."""
    CREATE = "create"       # Entity needs to be created
    UPDATE = "update"       # Entity exists but needs updates
    DELETE = "delete"       # Entity should be deleted (future use)
    MATCH = "match"         # Entity already in desired state
    AMBIGUOUS = "ambiguous" # Multiple potential matches found


@dataclass
class StateChange:
    """
    Represents a detected change between desired and actual state.

    Attributes:
        entity_type: Type of entity (e.g., 'dns_host', 'dhcp_reservation')
        name: Primary identifier for the entity
        change_type: Type of change (CREATE, UPDATE, MATCH, AMBIGUOUS)
        current: Current state from OPNsense (None if CREATE)
        desired: Desired state (None if DELETE)
        diff: Dictionary of field changes {field: (old_value, new_value)}
        alternatives: For AMBIGUOUS: list of potential matching entities
        uuid: UUID of the current entity (if matched)
    """
    entity_type: str
    name: str
    change_type: ChangeType
    current: Any = None
    desired: Any = None
    diff: Dict[str, tuple] = field(default_factory=dict)
    alternatives: List[Any] = field(default_factory=list)
    uuid: Optional[str] = None


class StateManager:
    """
    Manages desired state configuration for OPNsense.

    Provides a fluent interface to declare desired state and compare
    it against actual state in OPNsense.

    Example:
        >>> state = StateManager(client)
        >>> state.dns_host(hostname='server1', domain='lan', ip='192.168.1.100')
        >>> state.dhcp_reservation(mac='aa:bb:cc:dd:ee:ff', ip='192.168.1.50')
        >>> changes = state.plan()
        >>> state.apply()
    """

    def __init__(self, client: 'BaseClient'):
        """
        Initialize the StateManager.

        Args:
            client: OPNsense API client instance
        """
        self.client = client
        self._desired_state: Dict[str, List[Any]] = {}
        self._handlers: Dict[str, 'EntityHandler'] = {}
        self._actual_cache: Dict[str, List[Any]] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all available entity handlers."""
        from pysense.state.handlers.dns_host_handler import DnsHostHandler
        from pysense.state.handlers.dhcp_reservation_handler import DhcpReservationHandler
        from pysense.state.handlers.firewall_alias_handler import FirewallAliasHandler
        from pysense.state.handlers.firewall_rule_handler import FirewallRuleHandler
        from pysense.state.handlers.interface_handler import InterfaceHandler
        from pysense.state.handlers.vlan_handler import VlanHandler
        from pysense.state.handlers.snat_handler import SnatHandler
        from pysense.state.handlers.one_to_one_nat_handler import OneToOneNatHandler
        from pysense.state.handlers.dnat_handler import DnatHandler

        handlers = [
            DnsHostHandler(),
            DhcpReservationHandler(),
            FirewallAliasHandler(),
            FirewallRuleHandler(),
            InterfaceHandler(),
            VlanHandler(),
            SnatHandler(),
            OneToOneNatHandler(),
            DnatHandler(),
        ]

        for handler in handlers:
            self._handlers[handler.entity_type] = handler

    def _add_desired(self, entity_type: str, entity: Any) -> 'StateManager':
        """
        Add an entity to the desired state.

        Args:
            entity_type: Type of entity
            entity: Entity object to add

        Returns:
            Self for method chaining
        """
        if entity_type not in self._desired_state:
            self._desired_state[entity_type] = []
        self._desired_state[entity_type].append(entity)
        return self

    def dns_host(self, hostname: str, domain: str, ip: str, **kwargs) -> 'StateManager':
        """
        Declare a desired DNS host override.

        Args:
            hostname: Hostname (e.g., 'server1')
            domain: Domain (e.g., 'lan')
            ip: IP address (e.g., '192.168.1.100')
            **kwargs: Additional fields (enabled, rr, description, etc.)

        Returns:
            Self for method chaining
        """
        handler = self._handlers['dns_host']
        entity = handler.create_entity(
            hostname=hostname,
            domain=domain,
            server=ip,
            **kwargs
        )
        return self._add_desired('dns_host', entity)

    def dhcp_reservation(self, mac: str, ip: str, hostname: str = None,
                         subnet: str = None, **kwargs) -> 'StateManager':
        """
        Declare a desired DHCP reservation.

        Args:
            mac: MAC address (e.g., 'aa:bb:cc:dd:ee:ff')
            ip: IP address to reserve
            hostname: Optional hostname for the reservation
            subnet: Optional subnet UUID (if not provided, may need to be set)
            **kwargs: Additional fields (description, etc.)

        Returns:
            Self for method chaining
        """
        handler = self._handlers['dhcp_reservation']
        entity = handler.create_entity(
            hw_address=mac,
            ip_address=ip,
            hostname=hostname,
            subnet=subnet,
            **kwargs
        )
        return self._add_desired('dhcp_reservation', entity)

    def firewall_alias(self, name: str, type: str, content: List[str],
                       **kwargs) -> 'StateManager':
        """
        Declare a desired firewall alias.

        Args:
            name: Alias name (e.g., 'webservers')
            type: Alias type ('host', 'network', 'port', etc.)
            content: List of content items (IPs, networks, ports)
            **kwargs: Additional fields (enabled, description, categories, etc.)

        Returns:
            Self for method chaining
        """
        handler = self._handlers['firewall_alias']
        entity = handler.create_entity(
            name=name,
            type=type,
            content=content,
            **kwargs
        )
        return self._add_desired('firewall_alias', entity)

    def firewall_rule(self, action: str = 'pass',
                      interface: List[str] = None,
                      source: str = 'any',
                      destination: str = 'any',
                      protocol: str = 'any',
                      destination_port: str = None,
                      description: str = None,
                      **kwargs) -> 'StateManager':
        """
        Declare a desired firewall rule.

        Note: Rules are matched by description (if provided) or by
        source/destination/action combination. Always provide a
        unique description for reliable matching.

        Args:
            action: Rule action ('pass', 'block', 'reject')
            interface: List of interfaces (e.g., ['lan'])
            source: Source network/alias (e.g., 'any', '192.168.1.0/24')
            destination: Destination network/alias
            protocol: Protocol ('any', 'tcp', 'udp', 'icmp')
            destination_port: Destination port(s) (e.g., '80', '443', '80,443')
            description: Rule description (recommended for matching)
            **kwargs: Additional fields (log, quick, enabled, etc.)

        Returns:
            Self for method chaining
        """
        handler = self._handlers['firewall_rule']
        entity = handler.create_entity(
            action=action,
            interface=interface,
            source=source,
            destination=destination,
            protocol=protocol,
            destination_port=destination_port,
            description=description,
            **kwargs
        )
        return self._add_desired('firewall_rule', entity)

    def interface(self, identifier: str, description: str = None,
                  device: str = None, enabled: bool = True,
                  link_type: str = None, addr4: str = None,
                  addr6: str = None, mtu: int = None,
                  **kwargs) -> 'StateManager':
        """
        Declare a desired interface configuration (compare-only).

        NOTE: Interfaces cannot be automatically modified via API.
        Changes will be shown in the plan but must be applied manually
        through the OPNsense web UI.

        Args:
            identifier: Interface identifier (e.g., 'lan', 'wan', 'opt1')
            description: Display name (e.g., 'LAN', 'WAN', 'DMZ')
            device: Physical device name (e.g., 'vmx0', 'em0', 'igb0')
            enabled: Whether interface should be enabled
            link_type: Address configuration type ('static', 'dhcp', etc.)
            addr4: IPv4 address with CIDR (e.g., '192.168.1.1/24')
            addr6: IPv6 address with prefix
            mtu: Maximum transmission unit
            **kwargs: Additional fields

        Returns:
            Self for method chaining
        """
        handler = self._handlers['interface']
        entity = handler.create_entity(
            identifier=identifier,
            description=description,
            device=device,
            enabled=enabled,
            link_type=link_type,
            addr4=addr4,
            addr6=addr6,
            mtu=mtu,
            **kwargs
        )
        return self._add_desired('interface', entity)

    def vlan(self, interface: str, tag: int, description: str = None,
             pcp: int = 0, proto: str = '802.1q', **kwargs) -> 'StateManager':
        """
        Declare a desired VLAN interface.

        VLANs can be fully managed via API (create, update, delete).

        Args:
            interface: Parent interface device name (e.g., 'vmx0', 'em0', 'igb0')
            tag: VLAN tag (1-4094)
            description: VLAN description
            pcp: Priority Code Point (0-7, default 0)
            proto: VLAN protocol ('802.1q' or '802.1ad', default '802.1q')
            **kwargs: Additional fields

        Returns:
            Self for method chaining
        """
        handler = self._handlers['vlan']
        entity = handler.create_entity(
            interface=interface,
            tag=tag,
            description=description,
            pcp=pcp,
            proto=proto,
            **kwargs
        )
        return self._add_desired('vlan', entity)

    def snat_rule(self, interface: str = 'wan', source_net: str = 'any',
                  destination_net: str = 'any', target: str = 'wanip',
                  enabled: bool = True, nonat: bool = False,
                  protocol: str = 'any', source_port: str = None,
                  destination_port: str = None, target_port: str = None,
                  description: str = None, **kwargs) -> 'StateManager':
        """
        Declare a desired Source NAT (Outbound NAT) rule.

        SNAT rules control how outgoing traffic is translated/masqueraded.

        Args:
            interface: Outbound interface (e.g., 'wan')
            source_net: Source network/host/alias (e.g., '192.168.1.0/24', 'lan')
            destination_net: Destination network/host/alias
            target: NAT target ('wanip', 'any', specific IP, or alias)
            enabled: Whether rule is enabled
            nonat: If True, disable NAT for matched traffic (pass-through)
            protocol: Protocol ('any', 'tcp', 'udp', etc.)
            source_port: Source port filter
            destination_port: Destination port filter
            target_port: Target port for port translation
            description: Rule description (recommended for matching)
            **kwargs: Additional fields (sequence, ipprotocol, log, etc.)

        Returns:
            Self for method chaining
        """
        handler = self._handlers['snat_rule']
        entity = handler.create_entity(
            interface=interface,
            source_net=source_net,
            destination_net=destination_net,
            target=target,
            enabled=enabled,
            nonat=nonat,
            protocol=protocol,
            source_port=source_port,
            destination_port=destination_port,
            target_port=target_port,
            description=description,
            **kwargs
        )
        return self._add_desired('snat_rule', entity)

    def one_to_one_nat(self, external: str, source_net: str,
                       interface: str = 'wan', enabled: bool = True,
                       nat_type: str = 'binat', destination_net: str = 'any',
                       natreflection: str = '', description: str = None,
                       **kwargs) -> 'StateManager':
        """
        Declare a desired 1:1 NAT (One-to-One NAT) rule.

        1:1 NAT maps external IPs to internal hosts bidirectionally.

        Args:
            external: External IP address for NAT mapping
            source_net: Internal network/host (e.g., '192.168.1.100')
            interface: External interface (e.g., 'wan')
            enabled: Whether rule is enabled
            nat_type: NAT type ('binat' for bidirectional, 'nat' for unidirectional)
            destination_net: Destination filter (usually 'any')
            natreflection: NAT reflection ('', 'enable', 'disable')
            description: Rule description (recommended for matching)
            **kwargs: Additional fields (sequence, log, etc.)

        Returns:
            Self for method chaining
        """
        handler = self._handlers['one_to_one_nat']
        entity = handler.create_entity(
            external=external,
            source_net=source_net,
            interface=interface,
            enabled=enabled,
            nat_type=nat_type,
            destination_net=destination_net,
            natreflection=natreflection,
            description=description,
            **kwargs
        )
        return self._add_desired('one_to_one_nat', entity)

    def dnat_rule(self, target: str, local_port: int = None,
                  interface: List[str] = None, disabled: bool = False,
                  nordr: bool = False, protocol: str = None,
                  ipprotocol: str = 'inet', natreflection: str = None,
                  log: bool = False, sequence: int = 1,
                  descr: str = None, **kwargs) -> 'StateManager':
        """
        Declare a desired DNAT (Destination NAT / Port Forward) rule.

        DNAT rules forward incoming traffic from external ports to internal hosts.

        Args:
            target: Internal IP address to forward to
            local_port: Internal port to forward to
            interface: List of interfaces (e.g., ['wan'])
            disabled: Whether rule is disabled
            nordr: If True, disable redirection (pass-through)
            protocol: Protocol ('tcp', 'udp', 'tcp/udp', etc.)
            ipprotocol: IP version ('inet' for IPv4, 'inet6' for IPv6, 'inet46' for both)
            natreflection: NAT reflection mode ('purenat', 'disable')
            log: Log matched packets
            sequence: Rule order (1-999999)
            descr: Rule description (recommended for matching)
            **kwargs: Additional fields

        Returns:
            Self for method chaining
        """
        handler = self._handlers['dnat_rule']
        entity = handler.create_entity(
            target=target,
            local_port=local_port,
            interface=interface,
            disabled=disabled,
            nordr=nordr,
            protocol=protocol,
            ipprotocol=ipprotocol,
            natreflection=natreflection,
            log=log,
            sequence=sequence,
            descr=descr,
            **kwargs
        )
        return self._add_desired('dnat_rule', entity)

    def clear_cache(self) -> None:
        """Clear the cached actual state from OPNsense."""
        self._actual_cache.clear()

    def clear_desired(self) -> None:
        """Clear all declared desired state."""
        self._desired_state.clear()

    def plan(self, detect_deletes: bool = False) -> List[StateChange]:
        """
        Compare desired state with actual state and return list of changes.

        This method fetches current state from OPNsense and compares
        each desired entity against actual entities.

        Args:
            detect_deletes: If True, also detect entities that exist in OPNsense
                           but are not in the desired state (potential deletes)

        Returns:
            List of StateChange objects describing required changes
        """
        changes: List[StateChange] = []
        matched_uuids: Dict[str, set] = {}  # Track matched entities per type

        for entity_type, desired_list in self._desired_state.items():
            handler = self._handlers.get(entity_type)
            if not handler:
                continue

            # Fetch actual state (with caching)
            if entity_type not in self._actual_cache:
                self._actual_cache[entity_type] = handler.fetch_all(self.client)
            actual_list = self._actual_cache[entity_type]

            # Track matched UUIDs for delete detection
            if entity_type not in matched_uuids:
                matched_uuids[entity_type] = set()

            # Compare each desired entity
            for desired in desired_list:
                change = self._compare_entity(handler, desired, actual_list)
                changes.append(change)

                # Track matched UUID
                if change.uuid:
                    matched_uuids[entity_type].add(change.uuid)

        # Detect deletes: entities in OPNsense but not in desired state
        if detect_deletes:
            for entity_type, desired_list in self._desired_state.items():
                handler = self._handlers.get(entity_type)
                if not handler:
                    continue

                actual_list = self._actual_cache.get(entity_type, [])
                matched = matched_uuids.get(entity_type, set())

                for actual in actual_list:
                    uuid = handler.get_uuid(actual)
                    if uuid and uuid not in matched:
                        name = handler.get_primary_key_value(actual)
                        changes.append(StateChange(
                            entity_type=entity_type,
                            name=name,
                            change_type=ChangeType.DELETE,
                            current=actual,
                            desired=None,
                            uuid=uuid
                        ))

        return changes

    def _compare_entity(self, handler: 'EntityHandler', desired: Any,
                        actual_list: List[Any]) -> StateChange:
        """
        Compare a single desired entity against actual entities.

        Args:
            handler: The entity handler
            desired: The desired entity state
            actual_list: List of actual entities from OPNsense

        Returns:
            StateChange describing the result
        """
        entity_type = handler.entity_type
        name = handler.get_primary_key_value(desired)

        # Match against actual entities
        match_type, matched, alternatives = handler.match(desired, actual_list)

        if match_type == 'none':
            # No match found - needs to be created
            return StateChange(
                entity_type=entity_type,
                name=name,
                change_type=ChangeType.CREATE,
                current=None,
                desired=desired,
                diff={}
            )

        elif match_type == 'ambiguous':
            # Multiple potential matches - needs user resolution
            return StateChange(
                entity_type=entity_type,
                name=name,
                change_type=ChangeType.AMBIGUOUS,
                current=None,
                desired=desired,
                diff={},
                alternatives=alternatives
            )

        else:
            # Found a match (exact or secondary) - check for differences
            diff = handler.compute_diff(desired, matched)
            uuid = handler.get_uuid(matched)

            if diff:
                return StateChange(
                    entity_type=entity_type,
                    name=name,
                    change_type=ChangeType.UPDATE,
                    current=matched,
                    desired=desired,
                    diff=diff,
                    uuid=uuid
                )
            else:
                return StateChange(
                    entity_type=entity_type,
                    name=name,
                    change_type=ChangeType.MATCH,
                    current=matched,
                    desired=desired,
                    diff={},
                    uuid=uuid
                )

    def apply(self, auto_approve: bool = False,
              on_change: Optional[Callable[[StateChange, bool], bool]] = None,
              skip_ambiguous: bool = True,
              skip_deletes: bool = True,
              detect_deletes: bool = False) -> List[StateChange]:
        """
        Apply changes to reach desired state.

        Args:
            auto_approve: If True, apply all changes without confirmation.
                         If False and no on_change callback, skip all changes.
            on_change: Optional callback called before each change.
                      Receives (change, auto_approve) and returns bool to proceed.
                      If not provided and not auto_approve, changes are skipped.
            skip_ambiguous: If True, skip ambiguous matches (default).
            skip_deletes: If True, skip delete operations (default).
            detect_deletes: If True, detect entities not in desired state.

        Returns:
            List of applied changes
        """
        changes = self.plan(detect_deletes=detect_deletes)
        applied: List[StateChange] = []

        for change in changes:
            # Skip matches (already in desired state)
            if change.change_type == ChangeType.MATCH:
                continue

            # Skip ambiguous unless callback can resolve
            if change.change_type == ChangeType.AMBIGUOUS:
                if skip_ambiguous:
                    continue

            # Skip deletes unless explicitly enabled
            if change.change_type == ChangeType.DELETE:
                if skip_deletes:
                    continue

            # Determine whether to proceed
            proceed = auto_approve
            if on_change:
                proceed = on_change(change, auto_approve)

            if not proceed:
                continue

            # Apply the change
            handler = self._handlers.get(change.entity_type)
            if not handler:
                continue

            # Check if handler is read-only (e.g., interfaces)
            if getattr(handler, 'read_only', False):
                change.error = (
                    f"Manual action required: {change.entity_type} changes "
                    "cannot be applied automatically. Please configure "
                    "through the OPNsense web UI."
                )
                continue

            try:
                if change.change_type == ChangeType.CREATE:
                    handler.create(self.client, change.desired)
                    applied.append(change)

                elif change.change_type == ChangeType.UPDATE:
                    if change.uuid:
                        handler.update(self.client, change.uuid, change.desired)
                        applied.append(change)

                elif change.change_type == ChangeType.DELETE:
                    if change.uuid:
                        handler.delete(self.client, change.uuid)
                        applied.append(change)

            except NotImplementedError as e:
                # Handler doesn't support this operation (read-only)
                change.error = str(e)

            except Exception as e:
                # Store error but continue with other changes
                change.error = str(e)

        # Clear cache after applying changes
        self.clear_cache()

        return applied

    def format_plan(self, changes: List[StateChange] = None) -> str:
        """
        Format a plan as a human-readable string.

        Args:
            changes: List of changes to format (if None, calls plan())

        Returns:
            Formatted string representation of the plan
        """
        if changes is None:
            changes = self.plan()

        lines = []
        lines.append("State Plan:")
        lines.append("=" * 50)

        # Separate read-only entity changes
        def is_read_only(change):
            handler = self._handlers.get(change.entity_type)
            return handler and getattr(handler, 'read_only', False)

        creates = [c for c in changes if c.change_type == ChangeType.CREATE and not is_read_only(c)]
        updates = [c for c in changes if c.change_type == ChangeType.UPDATE and not is_read_only(c)]
        deletes = [c for c in changes if c.change_type == ChangeType.DELETE and not is_read_only(c)]
        matches = [c for c in changes if c.change_type == ChangeType.MATCH]
        ambiguous = [c for c in changes if c.change_type == ChangeType.AMBIGUOUS]

        # Manual changes (read-only entities)
        manual_creates = [c for c in changes if c.change_type == ChangeType.CREATE and is_read_only(c)]
        manual_updates = [c for c in changes if c.change_type == ChangeType.UPDATE and is_read_only(c)]
        manual_deletes = [c for c in changes if c.change_type == ChangeType.DELETE and is_read_only(c)]

        if creates:
            lines.append(f"\nTo create ({len(creates)}):")
            for c in creates:
                lines.append(f"  + {c.entity_type}: {c.name}")

        if updates:
            lines.append(f"\nTo update ({len(updates)}):")
            for c in updates:
                lines.append(f"  ~ {c.entity_type}: {c.name}")
                for field, (old, new) in c.diff.items():
                    lines.append(f"      {field}: {old!r} -> {new!r}")

        if deletes:
            lines.append(f"\nTo delete ({len(deletes)}):")
            for c in deletes:
                lines.append(f"  - {c.entity_type}: {c.name}")

        # Manual changes section
        manual_total = len(manual_creates) + len(manual_updates) + len(manual_deletes)
        if manual_total > 0:
            lines.append(f"\nManual changes required ({manual_total}):")
            lines.append("  (These cannot be applied automatically - configure via OPNsense web UI)")

            for c in manual_creates:
                lines.append(f"  [MANUAL] + {c.entity_type}: {c.name}")

            for c in manual_updates:
                lines.append(f"  [MANUAL] ~ {c.entity_type}: {c.name}")
                for field, (old, new) in c.diff.items():
                    lines.append(f"      {field}: {old!r} -> {new!r}")

            for c in manual_deletes:
                lines.append(f"  [MANUAL] - {c.entity_type}: {c.name}")

        if ambiguous:
            lines.append(f"\nAmbiguous ({len(ambiguous)}):")
            for c in ambiguous:
                lines.append(f"  ? {c.entity_type}: {c.name}")
                lines.append(f"      Found {len(c.alternatives)} potential matches")

        if matches:
            lines.append(f"\nAlready matching ({len(matches)}):")
            for c in matches:
                lines.append(f"  = {c.entity_type}: {c.name}")

        lines.append("")
        summary_parts = [
            f"{len(creates)} to create",
            f"{len(updates)} to update",
        ]
        if deletes:
            summary_parts.append(f"{len(deletes)} to delete")
        if manual_total > 0:
            summary_parts.append(f"{manual_total} manual")
        summary_parts.extend([
            f"{len(matches)} matching",
            f"{len(ambiguous)} ambiguous"
        ])
        lines.append(f"Summary: {', '.join(summary_parts)}")

        return "\n".join(lines)

    def export(self, entity_types: List[str] = None) -> str:
        """
        Export current OPNsense state as Python code.

        Generates Python code that recreates the current state using
        StateManager's fluent API.

        Args:
            entity_types: List of entity types to export.
                         If None, exports all registered types.

        Returns:
            Python code string that can recreate the current state
        """
        if entity_types is None:
            entity_types = list(self._handlers.keys())

        lines = [
            "# Generated state configuration",
            "# Copy this code to declare your desired state",
            "",
            "from pysense.client import Client",
            "",
            "# client = Client(...)",
            "# state = client.state()",
            "",
        ]

        for entity_type in entity_types:
            handler = self._handlers.get(entity_type)
            if not handler:
                continue

            # Fetch actual state
            if entity_type not in self._actual_cache:
                self._actual_cache[entity_type] = handler.fetch_all(self.client)
            actual_list = self._actual_cache[entity_type]

            if not actual_list:
                continue

            lines.append(f"# {entity_type} ({len(actual_list)} items)")

            for entity in actual_list:
                code = self._entity_to_code(entity_type, handler, entity)
                if code:
                    lines.append(code)

            lines.append("")

        return "\n".join(lines)

    def _entity_to_code(self, entity_type: str, handler: 'EntityHandler',
                        entity: Any) -> Optional[str]:
        """
        Convert an entity to Python code.

        Args:
            entity_type: Type of entity
            handler: Entity handler
            entity: Entity to convert

        Returns:
            Python code string or None if conversion not supported
        """
        if entity_type == 'dns_host':
            hostname = getattr(entity, 'hostname', None)
            domain = getattr(entity, 'domain', None)
            server = getattr(entity, 'server', None)
            description = getattr(entity, 'description', None)

            if not hostname or not domain:
                return None

            parts = [
                f"hostname={hostname!r}",
                f"domain={domain!r}",
                f"ip={server!r}",
            ]
            if description:
                parts.append(f"description={description!r}")

            return f"state.dns_host({', '.join(parts)})"

        elif entity_type == 'dhcp_reservation':
            hw_address = getattr(entity, 'hw_address', None)
            ip_address = getattr(entity, 'ip_address', None)
            hostname = getattr(entity, 'hostname', None)
            description = getattr(entity, 'description', None)

            if not hw_address or not ip_address:
                return None

            parts = [
                f"mac={hw_address!r}",
                f"ip={ip_address!r}",
            ]
            if hostname:
                parts.append(f"hostname={hostname!r}")
            if description:
                parts.append(f"description={description!r}")

            return f"state.dhcp_reservation({', '.join(parts)})"

        elif entity_type == 'firewall_alias':
            name = getattr(entity, 'name', None)
            alias_type = getattr(entity, 'type', None)
            content = getattr(entity, 'content', None)
            description = getattr(entity, 'description', None)

            # Skip internal/external aliases
            if alias_type and hasattr(alias_type, 'value'):
                type_val = alias_type.value
            else:
                type_val = str(alias_type) if alias_type else None

            if type_val in ('internal', 'external'):
                return f"# state.firewall_alias(name={name!r}, ...)  # skipped: {type_val} alias"

            if not name:
                return None

            # Parse content
            if isinstance(content, str):
                content_list = [c.strip() for c in content.split('\n') if c.strip()]
            elif isinstance(content, list):
                content_list = content
            else:
                content_list = []

            parts = [
                f"name={name!r}",
                f"type={type_val!r}",
                f"content={content_list!r}",
            ]
            if description:
                parts.append(f"description={description!r}")

            return f"state.firewall_alias({', '.join(parts)})"

        elif entity_type == 'firewall_rule':
            action = getattr(entity, 'action', None)
            interface = getattr(entity, 'interface', None)
            source_net = getattr(entity, 'source_net', None)
            destination_net = getattr(entity, 'destination_net', None)
            protocol = getattr(entity, 'protocol', None)
            destination_port = getattr(entity, 'destination_port', None)
            description = getattr(entity, 'description', None)
            enabled = getattr(entity, 'enabled', True)
            log = getattr(entity, 'log', False)

            # Get action value
            if hasattr(action, 'value'):
                action_val = action.value
            else:
                action_val = str(action) if action else 'pass'

            parts = [f"action={action_val!r}"]

            if interface:
                parts.append(f"interface={interface!r}")

            # Source
            if source_net:
                if isinstance(source_net, list) and len(source_net) == 1:
                    parts.append(f"source={source_net[0]!r}")
                else:
                    parts.append(f"source={source_net!r}")

            # Destination
            if destination_net:
                if isinstance(destination_net, list) and len(destination_net) == 1:
                    parts.append(f"destination={destination_net[0]!r}")
                else:
                    parts.append(f"destination={destination_net!r}")

            if protocol and protocol != 'any':
                parts.append(f"protocol={protocol!r}")

            if destination_port:
                parts.append(f"destination_port={destination_port!r}")

            if description:
                parts.append(f"description={description!r}")

            if not enabled:
                parts.append("enabled=False")

            if log:
                parts.append("log=True")

            return f"state.firewall_rule({', '.join(parts)})"

        return None

    def export_to_file(self, filename: str, entity_types: List[str] = None) -> None:
        """
        Export current OPNsense state to a Python file.

        Args:
            filename: Path to output file
            entity_types: List of entity types to export (None = all)
        """
        code = self.export(entity_types)
        with open(filename, 'w') as f:
            f.write(code)

    # =========================================================================
    # YAML Support
    # =========================================================================

    def load_yaml(self, yaml_file: Union[str, Path]) -> 'StateManager':
        """
        Load desired state from a YAML file.

        The YAML file should follow this structure:

        ```yaml
        # DNS host overrides
        dns_hosts:
          - hostname: server1
            domain: lan
            ip: 192.168.1.100
            description: Main server  # optional

        # DHCP reservations
        dhcp_reservations:
          - mac: aa:bb:cc:dd:ee:ff
            ip: 192.168.1.50
            hostname: printer  # optional
            description: Office printer  # optional

        # Firewall aliases
        firewall_aliases:
          - name: webservers
            type: host
            content:
              - 10.0.0.1
              - 10.0.0.2
            description: Web server pool  # optional

        # Firewall rules
        firewall_rules:
          - action: pass
            interface:
              - lan
            source: any
            destination: any
            protocol: tcp
            destination_port: "443"
            description: Allow HTTPS  # recommended for matching
            enabled: true  # optional, default true
            log: false  # optional, default false
        ```

        Args:
            yaml_file: Path to YAML file

        Returns:
            Self for method chaining
        """
        yaml_path = Path(yaml_file)
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            return self

        self._load_yaml_data(data)
        return self

    def load_yaml_string(self, yaml_string: str) -> 'StateManager':
        """
        Load desired state from a YAML string.

        Args:
            yaml_string: YAML content as string

        Returns:
            Self for method chaining
        """
        data = yaml.safe_load(yaml_string)
        if data:
            self._load_yaml_data(data)
        return self

    def _load_yaml_data(self, data: Dict[str, Any]) -> None:
        """
        Internal method to load parsed YAML data.

        Args:
            data: Parsed YAML dictionary
        """
        # Load DNS hosts
        for item in data.get('dns_hosts', []):
            self.dns_host(
                hostname=item['hostname'],
                domain=item['domain'],
                ip=item['ip'],
                **{k: v for k, v in item.items()
                   if k not in ('hostname', 'domain', 'ip')}
            )

        # Load DHCP reservations
        for item in data.get('dhcp_reservations', []):
            self.dhcp_reservation(
                mac=item['mac'],
                ip=item['ip'],
                hostname=item.get('hostname'),
                **{k: v for k, v in item.items()
                   if k not in ('mac', 'ip', 'hostname')}
            )

        # Load firewall aliases
        for item in data.get('firewall_aliases', []):
            self.firewall_alias(
                name=item['name'],
                type=item['type'],
                content=item.get('content', []),
                **{k: v for k, v in item.items()
                   if k not in ('name', 'type', 'content')}
            )

        # Load firewall rules
        for item in data.get('firewall_rules', []):
            self.firewall_rule(
                action=item.get('action', 'pass'),
                interface=item.get('interface'),
                source=item.get('source', 'any'),
                destination=item.get('destination', 'any'),
                protocol=item.get('protocol', 'any'),
                destination_port=item.get('destination_port'),
                description=item.get('description'),
                **{k: v for k, v in item.items()
                   if k not in ('action', 'interface', 'source', 'destination',
                               'protocol', 'destination_port', 'description')}
            )

        # Load interfaces (compare-only)
        for item in data.get('interfaces', []):
            self.interface(
                identifier=item['identifier'],
                description=item.get('description'),
                device=item.get('device'),
                enabled=item.get('enabled', True),
                link_type=item.get('link_type'),
                addr4=item.get('addr4'),
                addr6=item.get('addr6'),
                mtu=item.get('mtu'),
                **{k: v for k, v in item.items()
                   if k not in ('identifier', 'description', 'device', 'enabled',
                               'link_type', 'addr4', 'addr6', 'mtu')}
            )

        # Load VLANs
        for item in data.get('vlans', []):
            self.vlan(
                interface=item['interface'],
                tag=item['tag'],
                description=item.get('description'),
                pcp=item.get('pcp', 0),
                proto=item.get('proto', '802.1q'),
                **{k: v for k, v in item.items()
                   if k not in ('interface', 'tag', 'description', 'pcp', 'proto')}
            )

        # Load SNAT rules (Outbound NAT)
        for item in data.get('snat_rules', []):
            self.snat_rule(
                interface=item.get('interface', 'wan'),
                source_net=item.get('source_net', 'any'),
                destination_net=item.get('destination_net', 'any'),
                target=item.get('target', 'wanip'),
                enabled=item.get('enabled', True),
                nonat=item.get('nonat', False),
                protocol=item.get('protocol', 'any'),
                source_port=item.get('source_port'),
                destination_port=item.get('destination_port'),
                target_port=item.get('target_port'),
                description=item.get('description'),
                **{k: v for k, v in item.items()
                   if k not in ('interface', 'source_net', 'destination_net', 'target',
                               'enabled', 'nonat', 'protocol', 'source_port',
                               'destination_port', 'target_port', 'description')}
            )

        # Load 1:1 NAT rules
        for item in data.get('one_to_one_nat_rules', []):
            self.one_to_one_nat(
                external=item['external'],
                source_net=item['source_net'],
                interface=item.get('interface', 'wan'),
                enabled=item.get('enabled', True),
                nat_type=item.get('nat_type', 'binat'),
                destination_net=item.get('destination_net', 'any'),
                natreflection=item.get('natreflection', ''),
                description=item.get('description'),
                **{k: v for k, v in item.items()
                   if k not in ('external', 'source_net', 'interface', 'enabled',
                               'nat_type', 'destination_net', 'natreflection', 'description')}
            )

        # Load DNAT rules (Port Forward)
        for item in data.get('dnat_rules', []):
            self.dnat_rule(
                target=item.get('target'),
                local_port=item.get('local_port'),
                interface=item.get('interface'),
                disabled=item.get('disabled', False),
                nordr=item.get('nordr', False),
                protocol=item.get('protocol'),
                ipprotocol=item.get('ipprotocol', 'inet'),
                natreflection=item.get('natreflection'),
                log=item.get('log', False),
                sequence=item.get('sequence', 1),
                descr=item.get('descr'),
                **{k: v for k, v in item.items()
                   if k not in ('target', 'local_port', 'interface', 'disabled',
                               'nordr', 'protocol', 'ipprotocol', 'natreflection',
                               'log', 'sequence', 'descr')}
            )

    def export_yaml(self, entity_types: List[str] = None) -> str:
        """
        Export current OPNsense state as YAML.

        YAML Structure:
        ===============

        The exported YAML follows this structure:

        ```yaml
        # DNS Host Overrides
        # Maps hostnames to IP addresses for local DNS resolution
        dns_hosts:
          - hostname: server1      # Required: hostname without domain
            domain: lan            # Required: domain name
            ip: 192.168.1.100      # Required: IP address
            description: My server # Optional: description

        # DHCP Reservations
        # Static IP assignments based on MAC address
        dhcp_reservations:
          - mac: aa:bb:cc:dd:ee:ff # Required: MAC address
            ip: 192.168.1.50       # Required: reserved IP
            hostname: printer      # Optional: hostname
            description: Office    # Optional: description

        # Firewall Aliases
        # Named groups of IPs, networks, or ports for use in rules
        firewall_aliases:
          - name: webservers       # Required: unique alias name
            type: host             # Required: host, network, port, url, etc.
            content:               # Required: list of items
              - 10.0.0.1
              - 10.0.0.2
            description: Web pool  # Optional: description

        # Firewall Rules
        # Traffic filtering rules (order matters!)
        firewall_rules:
          - action: pass           # Required: pass, block, reject
            interface:             # Optional: list of interfaces
              - lan
            source: any            # Optional: source network/alias
            destination: any       # Optional: destination network/alias
            protocol: tcp          # Optional: any, tcp, udp, icmp, etc.
            destination_port: "443" # Optional: port number(s)
            description: HTTPS     # Recommended: unique description
            enabled: true          # Optional: default true
            log: false             # Optional: default false
        ```

        Field Details:
        ==============

        dns_hosts:
          - hostname: Host portion of FQDN
          - domain: Domain portion (e.g., 'lan', 'local', 'home.arpa')
          - ip: IPv4 or IPv6 address

        dhcp_reservations:
          - mac: MAC address (formats: aa:bb:cc:dd:ee:ff or AA-BB-CC-DD-EE-FF)
          - ip: IPv4 address to reserve
          - hostname: Optional hostname to assign via DHCP

        firewall_aliases:
          - type values: host, network, port, url, urltable, geoip, asn,
                        dynipv6host, authgroup, internal, external
          - content: List of IPs, networks, ports, URLs depending on type

        firewall_rules:
          - action: pass (allow), block (silent drop), reject (drop with response)
          - interface: List of interface names (lan, wan, opt1, etc.)
          - source/destination: 'any', CIDR notation, or alias name
          - protocol: 'any', 'tcp', 'udp', 'tcp/udp', 'icmp', etc.
          - destination_port: Single port, range (80-443), or comma-separated

        Args:
            entity_types: List of entity types to export.
                         If None, exports all registered types.

        Returns:
            YAML string representation of current state
        """
        if entity_types is None:
            entity_types = list(self._handlers.keys())

        output: Dict[str, List[Dict]] = {}

        for entity_type in entity_types:
            handler = self._handlers.get(entity_type)
            if not handler:
                continue

            # Fetch actual state
            if entity_type not in self._actual_cache:
                self._actual_cache[entity_type] = handler.fetch_all(self.client)
            actual_list = self._actual_cache[entity_type]

            if not actual_list:
                continue

            items = []
            for entity in actual_list:
                item = self._entity_to_yaml_dict(entity_type, handler, entity)
                if item:
                    items.append(item)

            if items:
                yaml_key = self._get_yaml_key(entity_type)
                output[yaml_key] = items

        return yaml.dump(output, default_flow_style=False, sort_keys=False,
                        allow_unicode=True)

    def _get_yaml_key(self, entity_type: str) -> str:
        """Map entity type to YAML key name."""
        mapping = {
            'dns_host': 'dns_hosts',
            'dhcp_reservation': 'dhcp_reservations',
            'firewall_alias': 'firewall_aliases',
            'firewall_rule': 'firewall_rules',
            'interface': 'interfaces',
            'vlan': 'vlans',
            'snat_rule': 'snat_rules',
            'one_to_one_nat': 'one_to_one_nat_rules',
            'dnat_rule': 'dnat_rules',
        }
        return mapping.get(entity_type, entity_type + 's')

    def _entity_to_yaml_dict(self, entity_type: str, handler: 'EntityHandler',
                             entity: Any) -> Optional[Dict[str, Any]]:
        """
        Convert an entity to a YAML-compatible dictionary.

        Args:
            entity_type: Type of entity
            handler: Entity handler
            entity: Entity to convert

        Returns:
            Dictionary for YAML serialization or None
        """
        # Get UUID if available
        uuid = getattr(entity, 'uuid', None)
        if uuid:
            uuid = str(uuid)

        if entity_type == 'dns_host':
            hostname = getattr(entity, 'hostname', None)
            domain = getattr(entity, 'domain', None)
            server = getattr(entity, 'server', None)
            description = getattr(entity, 'description', None)

            if not hostname or not domain:
                return None

            item = {}
            if uuid:
                item['uuid'] = uuid
            item['hostname'] = hostname
            item['domain'] = domain
            item['ip'] = server
            if description:
                item['description'] = description
            return item

        elif entity_type == 'dhcp_reservation':
            hw_address = getattr(entity, 'hw_address', None)
            ip_address = getattr(entity, 'ip_address', None)
            hostname = getattr(entity, 'hostname', None)
            description = getattr(entity, 'description', None)

            if not hw_address or not ip_address:
                return None

            item = {}
            if uuid:
                item['uuid'] = uuid
            item['mac'] = hw_address
            item['ip'] = ip_address
            if hostname:
                item['hostname'] = hostname
            if description:
                item['description'] = description
            return item

        elif entity_type == 'firewall_alias':
            name = getattr(entity, 'name', None)
            alias_type = getattr(entity, 'type', None)
            content = getattr(entity, 'content', None)
            description = getattr(entity, 'description', None)

            # Get type value
            if hasattr(alias_type, 'value'):
                type_val = alias_type.value
            else:
                type_val = str(alias_type) if alias_type else None

            # Skip internal/external aliases
            if type_val in ('internal', 'external'):
                return None

            if not name:
                return None

            # Parse content
            if isinstance(content, str):
                content_list = [c.strip() for c in content.split('\n') if c.strip()]
            elif isinstance(content, list):
                content_list = content
            else:
                content_list = []

            item = {}
            if uuid:
                item['uuid'] = uuid
            item['name'] = name
            item['type'] = type_val
            item['content'] = content_list
            if description:
                item['description'] = description
            return item

        elif entity_type == 'firewall_rule':
            action = getattr(entity, 'action', None)
            interface = getattr(entity, 'interface', None)
            source_net = getattr(entity, 'source_net', None)
            destination_net = getattr(entity, 'destination_net', None)
            protocol = getattr(entity, 'protocol', None)
            destination_port = getattr(entity, 'destination_port', None)
            description = getattr(entity, 'description', None)
            enabled = getattr(entity, 'enabled', True)
            log = getattr(entity, 'log', False)

            # Get action value
            if hasattr(action, 'value'):
                action_val = action.value
            else:
                action_val = str(action) if action else 'pass'

            item = {}
            if uuid:
                item['uuid'] = uuid
            item['action'] = action_val

            if interface:
                item['interface'] = interface

            # Source
            if source_net:
                if isinstance(source_net, list) and len(source_net) == 1:
                    item['source'] = source_net[0]
                else:
                    item['source'] = source_net

            # Destination
            if destination_net:
                if isinstance(destination_net, list) and len(destination_net) == 1:
                    item['destination'] = destination_net[0]
                else:
                    item['destination'] = destination_net

            if protocol and protocol != 'any':
                item['protocol'] = protocol

            if destination_port:
                item['destination_port'] = str(destination_port)

            if description:
                item['description'] = description

            if not enabled:
                item['enabled'] = False

            if log:
                item['log'] = True

            return item

        elif entity_type == 'interface':
            identifier = getattr(entity, 'identifier', None)
            description = getattr(entity, 'description', None)
            device = getattr(entity, 'device', None)
            enabled = getattr(entity, 'enabled', True)
            link_type = getattr(entity, 'link_type', None)
            addr4 = getattr(entity, 'addr4', None)
            addr6 = getattr(entity, 'addr6', None)
            mtu = getattr(entity, 'mtu', None)

            if not identifier:
                return None

            # Use identifier as pseudo-UUID for interfaces
            item = {'identifier': identifier}

            if description:
                item['description'] = description
            if device:
                item['device'] = device

            item['enabled'] = enabled

            if link_type:
                if hasattr(link_type, 'value'):
                    item['link_type'] = link_type.value
                else:
                    item['link_type'] = str(link_type)

            if addr4:
                item['addr4'] = addr4
            if addr6:
                item['addr6'] = addr6
            if mtu:
                item['mtu'] = mtu

            return item

        elif entity_type == 'vlan':
            interface = getattr(entity, 'interface', None)
            tag = getattr(entity, 'tag', None)
            descr = getattr(entity, 'descr', None)
            pcp = getattr(entity, 'pcp', None)
            proto = getattr(entity, 'proto', None)
            vlanif = getattr(entity, 'vlanif', None)

            if not interface or not tag:
                return None

            item = {}
            if uuid:
                item['uuid'] = uuid
            item['interface'] = interface
            item['tag'] = tag

            if descr:
                item['description'] = descr
            if vlanif:
                item['vlanif'] = vlanif

            # PCP
            if pcp:
                if hasattr(pcp, 'value'):
                    item['pcp'] = int(pcp.value)
                else:
                    item['pcp'] = int(pcp) if pcp else 0

            # Protocol
            if proto:
                if hasattr(proto, 'value'):
                    item['proto'] = proto.value
                else:
                    item['proto'] = str(proto)

            return item

        elif entity_type == 'snat_rule':
            interface = getattr(entity, 'interface', None)
            source_net = getattr(entity, 'source_net', None)
            destination_net = getattr(entity, 'destination_net', None)
            target = getattr(entity, 'target', None)
            enabled = getattr(entity, 'enabled', True)
            nonat = getattr(entity, 'nonat', False)
            protocol = getattr(entity, 'protocol', None)
            source_port = getattr(entity, 'source_port', None)
            destination_port = getattr(entity, 'destination_port', None)
            target_port = getattr(entity, 'target_port', None)
            ipprotocol = getattr(entity, 'ipprotocol', None)
            sequence = getattr(entity, 'sequence', None)
            log = getattr(entity, 'log', False)
            description = getattr(entity, 'description', None)

            item = {}
            if uuid:
                item['uuid'] = uuid

            item['interface'] = interface or 'wan'
            item['source_net'] = source_net or 'any'
            item['destination_net'] = destination_net or 'any'
            item['target'] = target or 'wanip'

            if not enabled:
                item['enabled'] = False
            if nonat:
                item['nonat'] = True
            if protocol and protocol != 'any':
                item['protocol'] = protocol
            if source_port:
                item['source_port'] = source_port
            if destination_port:
                item['destination_port'] = destination_port
            if target_port:
                item['target_port'] = target_port
            if ipprotocol:
                if hasattr(ipprotocol, 'value'):
                    item['ipprotocol'] = ipprotocol.value
                else:
                    item['ipprotocol'] = str(ipprotocol)
            if sequence and sequence != 1:
                item['sequence'] = sequence
            if log:
                item['log'] = True
            if description:
                item['description'] = description

            return item

        elif entity_type == 'one_to_one_nat':
            external = getattr(entity, 'external', None)
            source_net = getattr(entity, 'source_net', None)
            interface = getattr(entity, 'interface', None)
            enabled = getattr(entity, 'enabled', True)
            nat_type = getattr(entity, 'type', None)
            destination_net = getattr(entity, 'destination_net', None)
            natreflection = getattr(entity, 'natreflection', None)
            sequence = getattr(entity, 'sequence', None)
            log = getattr(entity, 'log', False)
            description = getattr(entity, 'description', None)

            if not external or not source_net:
                return None

            item = {}
            if uuid:
                item['uuid'] = uuid

            item['external'] = external
            item['source_net'] = source_net
            item['interface'] = interface or 'wan'

            if not enabled:
                item['enabled'] = False

            # NAT type
            if nat_type:
                if hasattr(nat_type, 'value'):
                    item['nat_type'] = nat_type.value
                else:
                    item['nat_type'] = str(nat_type)

            if destination_net and destination_net != 'any':
                item['destination_net'] = destination_net

            # NAT reflection
            if natreflection:
                if hasattr(natreflection, 'value'):
                    refl_val = natreflection.value
                else:
                    refl_val = str(natreflection)
                if refl_val:
                    item['natreflection'] = refl_val

            if sequence and sequence != 1:
                item['sequence'] = sequence
            if log:
                item['log'] = True
            if description:
                item['description'] = description

            return item

        elif entity_type == 'dnat_rule':
            target = getattr(entity, 'target', None)
            local_port = getattr(entity, 'local_port', None)
            interface = getattr(entity, 'interface', None)
            disabled = getattr(entity, 'disabled', False)
            nordr = getattr(entity, 'nordr', False)
            protocol = getattr(entity, 'protocol', None)
            ipprotocol = getattr(entity, 'ipprotocol', None)
            poolopts = getattr(entity, 'poolopts', None)
            natreflection = getattr(entity, 'natreflection', None)
            sequence = getattr(entity, 'sequence', None)
            log = getattr(entity, 'log', False)
            descr = getattr(entity, 'descr', None)

            item = {}
            if uuid:
                item['uuid'] = uuid

            if target:
                item['target'] = target
            if local_port:
                item['local_port'] = local_port

            # Interface
            if interface:
                if isinstance(interface, list):
                    item['interface'] = interface
                else:
                    item['interface'] = [interface]

            if disabled:
                item['disabled'] = True
            if nordr:
                item['nordr'] = True

            if protocol:
                item['protocol'] = protocol

            # IP protocol
            if ipprotocol:
                if hasattr(ipprotocol, 'value'):
                    item['ipprotocol'] = ipprotocol.value
                else:
                    item['ipprotocol'] = str(ipprotocol)

            # Pool options
            if poolopts:
                if hasattr(poolopts, 'value'):
                    item['poolopts'] = poolopts.value
                else:
                    item['poolopts'] = str(poolopts)

            # NAT reflection
            if natreflection:
                if hasattr(natreflection, 'value'):
                    item['natreflection'] = natreflection.value
                else:
                    item['natreflection'] = str(natreflection)

            if sequence:
                seq_val = int(sequence) if isinstance(sequence, str) else sequence
                if seq_val != 1:
                    item['sequence'] = seq_val
            if log:
                item['log'] = True
            if descr:
                item['descr'] = descr

            return item

        return None

    def export_yaml_to_file(self, filename: Union[str, Path],
                            entity_types: List[str] = None) -> None:
        """
        Export current OPNsense state to a YAML file.

        Args:
            filename: Path to output YAML file
            entity_types: List of entity types to export (None = all)
        """
        yaml_content = self.export_yaml(entity_types)
        with open(filename, 'w') as f:
            f.write(yaml_content)
