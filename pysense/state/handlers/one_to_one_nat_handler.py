"""
Handler for 1:1 NAT (One-to-One NAT) rules.

1:1 NAT rules map external IPs to internal hosts bidirectionally.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.OneToOneRule import Rule as OneToOneRule

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class OneToOneNatHandler(EntityHandler):
    """
    Handler for 1:1 NAT (One-to-One NAT) rule entities.

    1:1 NAT rules can be fully managed via the OPNsense API, including
    create, update, and delete operations.
    """

    @property
    def entity_type(self) -> str:
        return "one_to_one_nat"

    @property
    def primary_key(self) -> str:
        return "description"

    @property
    def secondary_keys(self) -> List[str]:
        return ["external", "source_net", "interface"]

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "enabled",
            "log",
            "sequence",
            "interface",
            "type",
            "source_net",
            "source_not",
            "destination_net",
            "destination_not",
            "external",
            "natreflection",
            "description",
        ]

    def fetch_all(self, client: 'BaseClient') -> List[OneToOneRule]:
        """
        Fetch all 1:1 NAT rules from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of OneToOneRule entities
        """
        result = client.firewall_one_to_one_search_rule()
        return result.rows

    def create(self, client: 'BaseClient', entity: OneToOneRule) -> Any:
        """
        Create a new 1:1 NAT rule.

        Args:
            client: OPNsense API client
            entity: OneToOneRule entity to create

        Returns:
            API Result object
        """
        result = client.firewall_one_to_one_add_rule(entity)
        # Apply changes
        client.firewall_one_to_one_apply()
        return result

    def update(self, client: 'BaseClient', uuid: str, entity: OneToOneRule) -> Any:
        """
        Update an existing 1:1 NAT rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the 1:1 NAT rule to update
            entity: Updated OneToOneRule entity

        Returns:
            API Result object
        """
        result = client.firewall_one_to_one_set_rule(uuid, entity)
        # Apply changes
        client.firewall_one_to_one_apply()
        return result

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a 1:1 NAT rule.

        Args:
            client: OPNsense API client
            uuid: UUID of the 1:1 NAT rule to delete

        Returns:
            API Result object
        """
        result = client.firewall_one_to_one_del_rule(uuid)
        # Apply changes
        client.firewall_one_to_one_apply()
        return result

    def create_entity(self,
                      external: str,
                      source_net: str,
                      interface: str = 'wan',
                      enabled: bool = True,
                      nat_type: str = 'binat',
                      destination_net: str = 'any',
                      source_not: bool = False,
                      destination_not: bool = False,
                      natreflection: str = '',
                      log: bool = False,
                      sequence: int = 1,
                      description: str = None,
                      **kwargs) -> OneToOneRule:
        """
        Create a new OneToOneRule entity instance.

        Args:
            external: External IP address for NAT mapping
            source_net: Internal network/host (e.g., '192.168.1.100')
            interface: External interface (e.g., 'wan')
            enabled: Whether rule is enabled
            nat_type: NAT type ('binat' for bidirectional, 'nat' for unidirectional)
            destination_net: Destination filter (usually 'any')
            source_not: Invert source match
            destination_not: Invert destination match
            natreflection: NAT reflection ('', 'enable', 'disable')
            log: Log matched packets
            sequence: Rule order (1-99999)
            description: Rule description (used for matching)

        Returns:
            OneToOneRule entity
        """
        entity_kwargs = {
            'enabled': enabled,
            'log': log,
            'sequence': sequence,
            'interface': interface,
            'source_net': source_net,
            'source_not': source_not,
            'destination_net': destination_net,
            'destination_not': destination_not,
            'external': external,
        }

        # Set NAT type
        try:
            entity_kwargs['type'] = OneToOneRule.TypeEnum(nat_type)
        except ValueError:
            entity_kwargs['type'] = OneToOneRule.TypeEnum.BINAT

        # Set NAT reflection
        try:
            entity_kwargs['natreflection'] = OneToOneRule.NatReflectionEnum(natreflection)
        except ValueError:
            entity_kwargs['natreflection'] = OneToOneRule.NatReflectionEnum.DEFAULT

        if description is not None:
            entity_kwargs['description'] = description

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return OneToOneRule(**entity_kwargs)
