"""
Handler for Source NAT (Outbound NAT) rules.

SNAT rules control how outgoing traffic is translated/masqueraded.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.SNATRule import Rule as SNATRule

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class SnatHandler(EntityHandler):
    """
    Handler for Source NAT (Outbound NAT) rule entities.

    SNAT rules can be fully managed via the OPNsense API, including
    create, update, and delete operations.
    """

    @property
    def entity_type(self) -> str:
        return "snat_rule"

    @property
    def primary_key(self) -> str:
        return "description"

    @property
    def secondary_keys(self) -> List[str]:
        return ["source_net", "destination_net", "interface", "target"]

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "enabled",
            "nonat",
            "sequence",
            "interface",
            "ipprotocol",
            "protocol",
            "source_net",
            "source_not",
            "source_port",
            "destination_net",
            "destination_not",
            "destination_port",
            "target",
            "target_port",
            "log",
            "description",
        ]

    def fetch_all(self, client: 'BaseClient') -> List[SNATRule]:
        """
        Fetch all SNAT rules from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of SNATRule entities
        """
        result = client.firewall_snat_search_rule()
        return result.rows

    def create(self, client: 'BaseClient', entity: SNATRule) -> Any:
        """
        Create a new SNAT rule.

        Args:
            client: OPNsense API client
            entity: SNATRule entity to create

        Returns:
            API Result object
        """
        result = client.firewall_snat_add_rule(entity)
        # Apply changes
        client.firewall_snat_apply()
        return result

    def update(self, client: 'BaseClient', uuid: str, entity: SNATRule) -> Any:
        """
        Update an existing SNAT rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the SNAT rule to update
            entity: Updated SNATRule entity

        Returns:
            API Result object
        """
        result = client.firewall_snat_set_rule(uuid, entity)
        # Apply changes
        client.firewall_snat_apply()
        return result

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a SNAT rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the SNAT rule to delete

        Returns:
            API Result object
        """
        result = client.firewall_snat_del_rule(uuid)
        # Apply changes
        client.firewall_snat_apply()
        return result

    def create_entity(self,
                      interface: str = 'wan',
                      source_net: str = 'any',
                      destination_net: str = 'any',
                      target: str = 'wanip',
                      enabled: bool = True,
                      nonat: bool = False,
                      protocol: str = 'any',
                      source_port: str = None,
                      destination_port: str = None,
                      target_port: str = None,
                      sequence: int = 1,
                      ipprotocol: str = 'inet',
                      source_not: bool = False,
                      destination_not: bool = False,
                      log: bool = False,
                      description: str = None,
                      **kwargs) -> SNATRule:
        """
        Create a new SNATRule entity instance.

        Args:
            interface: Outbound interface (e.g., 'wan')
            source_net: Source network/host/alias (e.g., '192.168.1.0/24', 'lan')
            destination_net: Destination network/host/alias
            target: NAT target ('wanip', 'any', specific IP, or alias)
            enabled: Whether rule is enabled
            nonat: If True, disable NAT for matched traffic
            protocol: Protocol ('any', 'tcp', 'udp', etc.)
            source_port: Source port filter
            destination_port: Destination port filter
            target_port: Target port for port translation
            sequence: Rule order (1-99999)
            ipprotocol: IP version ('inet' for IPv4, 'inet6' for IPv6)
            source_not: Invert source match
            destination_not: Invert destination match
            log: Log matched packets
            description: Rule description (used for matching)

        Returns:
            SNATRule entity
        """
        entity_kwargs = {
            'enabled': enabled,
            'nonat': nonat,
            'sequence': sequence,
            'interface': interface,
            'protocol': protocol,
            'source_net': source_net,
            'source_not': source_not,
            'destination_net': destination_net,
            'destination_not': destination_not,
            'target': target,
            'log': log,
        }

        # Set IP protocol
        try:
            entity_kwargs['ipprotocol'] = SNATRule.SnatrulesRuleIpprotocolEnum(ipprotocol)
        except ValueError:
            entity_kwargs['ipprotocol'] = SNATRule.SnatrulesRuleIpprotocolEnum.INET

        if source_port is not None:
            entity_kwargs['source_port'] = source_port
        if destination_port is not None:
            entity_kwargs['destination_port'] = destination_port
        if target_port is not None:
            entity_kwargs['target_port'] = target_port
        if description is not None:
            entity_kwargs['description'] = description

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return SNATRule(**entity_kwargs)
