"""
Handler for VLAN interfaces.

VLANs can be fully managed via API (create, update, delete).
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.Vlan import Vlan

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class VlanHandler(EntityHandler):
    """
    Handler for VLAN interface entities.

    VLANs can be fully managed via the OPNsense API, including
    create, update, and delete operations.
    """

    @property
    def entity_type(self) -> str:
        return "vlan"

    @property
    def primary_key(self) -> str:
        return "vlanif"  # The VLAN interface name (e.g., vlan0.100)

    @property
    def secondary_keys(self) -> List[str]:
        return ["tag", "interface"]  # Match by VLAN tag + parent interface

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "interface",
            "tag",
            "pcp",
            "proto",
            "descr",
        ]

    def get_primary_key_value(self, entity: Any) -> str:
        """
        Composite key: parent_interface.tag or vlanif

        Args:
            entity: Vlan entity

        Returns:
            VLAN interface name or composite key
        """
        vlanif = getattr(entity, 'vlanif', None)
        if vlanif:
            return vlanif

        # Fall back to composite: interface.tag
        interface = getattr(entity, 'interface', '') or ''
        tag = getattr(entity, 'tag', '') or ''
        return f"{interface}.{tag}"

    def fetch_all(self, client: 'BaseClient') -> List[Vlan]:
        """
        Fetch all VLANs from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of Vlan entities
        """
        result = client.vlan_search_item()
        return result.rows

    def create(self, client: 'BaseClient', entity: Vlan) -> Any:
        """
        Create a new VLAN.

        Args:
            client: OPNsense API client
            entity: Vlan entity to create

        Returns:
            API Result object
        """
        result = client.vlan_add_item(entity)
        # Apply VLAN configuration
        client.vlan_reconfigure()
        return result

    def update(self, client: 'BaseClient', uuid: str, entity: Vlan) -> Any:
        """
        Update an existing VLAN.

        Args:
            client: OPNsense API client
            uuid: UUID of the VLAN to update
            entity: Updated Vlan entity

        Returns:
            API Result object
        """
        result = client.vlan_set_item(uuid, entity)
        # Apply VLAN configuration
        client.vlan_reconfigure()
        return result

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a VLAN.

        Args:
            client: OPNsense API client
            uuid: UUID of the VLAN to delete

        Returns:
            API Result object
        """
        result = client.vlan_del_item(uuid)
        # Apply VLAN configuration
        client.vlan_reconfigure()
        return result

    def create_entity(self,
                      interface: str,
                      tag: int,
                      description: str = None,
                      pcp: int = 0,
                      proto: str = '802.1q',
                      **kwargs) -> Vlan:
        """
        Create a new Vlan entity instance.

        Args:
            interface: Parent interface device name (e.g., 'vmx0', 'em0')
            tag: VLAN tag (1-4094)
            description: VLAN description
            pcp: Priority Code Point (0-7, default 0)
            proto: VLAN protocol ('802.1q' or '802.1ad', default '802.1q')

        Returns:
            Vlan entity
        """
        entity_kwargs = {
            'interface': interface,
            'tag': tag,
        }

        if description is not None:
            entity_kwargs['descr'] = description

        # Set PCP
        try:
            entity_kwargs['pcp'] = Vlan.VlanVlanPcpEnum(str(pcp))
        except ValueError:
            entity_kwargs['pcp'] = Vlan.VlanVlanPcpEnum.PCP0

        # Set protocol
        if proto:
            try:
                entity_kwargs['proto'] = Vlan.VlanVlanProtoEnum(proto)
            except ValueError:
                entity_kwargs['proto'] = Vlan.VlanVlanProtoEnum.OPT1

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return Vlan(**entity_kwargs)
