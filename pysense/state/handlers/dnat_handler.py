"""
Handler for DNAT (Destination NAT / Port Forward) rules.

DNAT rules forward incoming traffic from external ports to internal hosts.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.DNATRule import Rule as DNATRule

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class DnatHandler(EntityHandler):
    """
    Handler for DNAT (Destination NAT / Port Forward) rule entities.

    DNAT rules can be fully managed via the OPNsense API, including
    create, update, and delete operations.
    """

    @property
    def entity_type(self) -> str:
        return "dnat_rule"

    @property
    def primary_key(self) -> str:
        return "descr"

    @property
    def secondary_keys(self) -> List[str]:
        return ["target", "local_port", "interface"]

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "disabled",
            "nordr",
            "sequence",
            "interface",
            "ipprotocol",
            "protocol",
            "target",
            "local_port",
            "poolopts",
            "log",
            "descr",
            "natreflection",
        ]

    def fetch_all(self, client: 'BaseClient') -> List[DNATRule]:
        """
        Fetch all DNAT rules from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of DNATRule entities
        """
        result = client.firewall_dnat_search_rule()
        return result.rows

    def create(self, client: 'BaseClient', entity: DNATRule) -> Any:
        """
        Create a new DNAT rule.

        Args:
            client: OPNsense API client
            entity: DNATRule entity to create

        Returns:
            API Result object
        """
        result = client.firewall_dnat_add_rule(entity)
        # Apply changes
        client.firewall_dnat_apply()
        return result

    def update(self, client: 'BaseClient', uuid: str, entity: DNATRule) -> Any:
        """
        Update an existing DNAT rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the DNAT rule to update
            entity: Updated DNATRule entity

        Returns:
            API Result object
        """
        result = client.firewall_dnat_set_rule(uuid, entity)
        # Apply changes
        client.firewall_dnat_apply()
        return result

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a DNAT rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the DNAT rule to delete

        Returns:
            API Result object
        """
        result = client.firewall_dnat_del_rule(uuid)
        # Apply changes
        client.firewall_dnat_apply()
        return result

    def get_entity_name(self, entity: Any) -> str:
        """
        Get a display name for an entity.

        Args:
            entity: Entity to get name for

        Returns:
            String name for the entity
        """
        # Use description, or target:port as fallback
        descr = getattr(entity, 'descr', None)
        if descr:
            return descr

        target = getattr(entity, 'target', 'unknown')
        local_port = getattr(entity, 'local_port', '')
        if local_port:
            return f"{target}:{local_port}"
        return str(target) if target else 'unnamed'

    def create_entity(self,
                      target: str,
                      local_port: int = None,
                      interface: List[str] = None,
                      disabled: bool = False,
                      nordr: bool = False,
                      protocol: str = None,
                      ipprotocol: str = 'inet',
                      poolopts: str = None,
                      natreflection: str = None,
                      log: bool = False,
                      sequence: int = 1,
                      descr: str = None,
                      **kwargs) -> DNATRule:
        """
        Create a new DNATRule entity instance.

        Args:
            target: Internal IP address to forward to
            local_port: Internal port to forward to
            interface: List of interfaces (e.g., ['wan'])
            disabled: Whether rule is disabled
            nordr: If True, disable redirection (pass-through)
            protocol: Protocol ('tcp', 'udp', 'tcp/udp', etc.)
            ipprotocol: IP version ('inet' for IPv4, 'inet6' for IPv6, 'inet46' for both)
            poolopts: Pool options for multiple targets
            natreflection: NAT reflection mode ('purenat', 'disable')
            log: Log matched packets
            sequence: Rule order (1-999999)
            descr: Rule description (used for matching)

        Returns:
            DNATRule entity
        """
        entity_kwargs = {
            'sequence': sequence,
        }

        if interface is not None:
            entity_kwargs['interface'] = interface if isinstance(interface, list) else [interface]
        else:
            entity_kwargs['interface'] = ['wan']

        if target is not None:
            entity_kwargs['target'] = target

        if local_port is not None:
            entity_kwargs['local_port'] = local_port

        if disabled:
            entity_kwargs['disabled'] = True

        if nordr:
            entity_kwargs['nordr'] = True

        if protocol is not None:
            entity_kwargs['protocol'] = protocol

        # Set IP protocol
        if ipprotocol:
            try:
                entity_kwargs['ipprotocol'] = DNATRule.RuleRuleIpprotocolEnum(ipprotocol)
            except ValueError:
                entity_kwargs['ipprotocol'] = DNATRule.RuleRuleIpprotocolEnum.INET

        # Set pool options
        if poolopts:
            try:
                entity_kwargs['poolopts'] = DNATRule.RuleRulePooloptsEnum(poolopts)
            except ValueError:
                pass

        # Set NAT reflection
        if natreflection:
            try:
                entity_kwargs['natreflection'] = DNATRule.RuleRuleNatreflectionEnum(natreflection)
            except ValueError:
                pass

        if log:
            entity_kwargs['log'] = True

        if descr is not None:
            entity_kwargs['descr'] = descr

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return DNATRule(**entity_kwargs)
