"""
Handler for network interfaces (compare-only).

Interfaces require manual configuration changes in OPNsense.
This handler only supports comparing desired vs actual state.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.InterfaceOverview import Interface

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class InterfaceHandler(EntityHandler):
    """
    Handler for network interface entities (compare-only).

    Interfaces cannot be automatically created/updated/deleted via API.
    This handler supports comparison only - changes must be applied
    manually through the OPNsense web UI.
    """

    @property
    def entity_type(self) -> str:
        return "interface"

    @property
    def primary_key(self) -> str:
        return "identifier"

    @property
    def secondary_keys(self) -> List[str]:
        return ["device", "description"]

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "identifier",
            "description",
            "device",
            "enabled",
            "link_type",
            "addr4",
            "addr6",
            "mtu",
        ]

    @property
    def read_only(self) -> bool:
        """Interfaces are read-only - changes require manual intervention."""
        return True

    def fetch_all(self, client: 'BaseClient') -> List[Interface]:
        """
        Fetch all interfaces from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of Interface entities (assigned interfaces only)
        """
        interfaces = client.interface_overview_export()
        return interfaces.get_assigned()

    def create(self, client: 'BaseClient', entity: Interface) -> Any:
        """
        Not supported - interfaces must be configured manually.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "Interface creation requires manual configuration in OPNsense. "
            "Please configure the interface through the web UI: "
            "Interfaces > Assignments"
        )

    def update(self, client: 'BaseClient', uuid: str, entity: Interface) -> Any:
        """
        Not supported - interfaces must be configured manually.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "Interface updates require manual configuration in OPNsense. "
            "Please modify the interface through the web UI: "
            f"Interfaces > [{entity.identifier or entity.description}]"
        )

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Not supported - interfaces must be configured manually.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "Interface deletion requires manual configuration in OPNsense. "
            "Please remove the interface through the web UI: "
            "Interfaces > Assignments"
        )

    def get_uuid(self, entity: Any) -> Optional[str]:
        """
        Interfaces don't have UUIDs - use identifier as unique key.

        Args:
            entity: Interface entity

        Returns:
            Identifier as pseudo-UUID
        """
        return getattr(entity, 'identifier', None)

    def create_entity(self,
                      identifier: str,
                      description: str = None,
                      device: str = None,
                      enabled: bool = True,
                      link_type: str = None,
                      addr4: str = None,
                      addr6: str = None,
                      mtu: int = None,
                      **kwargs) -> Interface:
        """
        Create a new Interface entity instance for comparison.

        Args:
            identifier: Interface identifier (e.g., 'lan', 'wan', 'opt1')
            description: Display name (e.g., 'LAN', 'WAN', 'DMZ')
            device: Physical device (e.g., 'vmx0', 'em0')
            enabled: Whether interface is enabled
            link_type: Address type ('static', 'dhcp', etc.)
            addr4: IPv4 address with CIDR (e.g., '192.168.1.1/24')
            addr6: IPv6 address with prefix
            mtu: Maximum transmission unit

        Returns:
            Interface entity
        """
        from pysense.pydantic.InterfaceOverview import LinkTypeEnum

        entity_kwargs = {
            'identifier': identifier,
            'enabled': enabled,
        }

        if description is not None:
            entity_kwargs['description'] = description
        if device is not None:
            entity_kwargs['device'] = device
        if link_type is not None:
            try:
                entity_kwargs['link_type'] = LinkTypeEnum(link_type)
            except ValueError:
                entity_kwargs['link_type'] = link_type
        if addr4 is not None:
            entity_kwargs['addr4'] = addr4
        if addr6 is not None:
            entity_kwargs['addr6'] = addr6
        if mtu is not None:
            entity_kwargs['mtu'] = mtu

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return Interface(**entity_kwargs)
