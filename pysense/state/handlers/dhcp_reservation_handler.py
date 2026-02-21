"""
Handler for Kea DHCP reservations.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.KeaDhcpv4 import Reservation

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class DhcpReservationHandler(EntityHandler):
    """
    Handler for Kea DHCPv4 reservation entities.

    Manages static DHCP leases/reservations in OPNsense's Kea DHCP server.
    """

    @property
    def entity_type(self) -> str:
        return "dhcp_reservation"

    @property
    def primary_key(self) -> str:
        return "hw_address"  # MAC address is unique identifier

    @property
    def secondary_keys(self) -> List[str]:
        return ["ip_address", "hostname"]

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "subnet",
            "ip_address",
            "hw_address",
            "hostname",
            "description"
        ]

    def get_primary_key_value(self, entity: Any) -> str:
        """
        Get the primary key value (MAC address), normalized to lowercase.

        Args:
            entity: Reservation entity

        Returns:
            Normalized MAC address
        """
        hw_address = getattr(entity, 'hw_address', '') or ''
        # Normalize MAC address to lowercase for consistent comparison
        return hw_address.lower()

    def fetch_all(self, client: 'BaseClient') -> List[Reservation]:
        """
        Fetch all DHCP reservations from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of Reservation entities
        """
        result = client.kea_dhcpv4_search_reservation()
        return result.rows

    def create(self, client: 'BaseClient', entity: Reservation) -> Any:
        """
        Create a new DHCP reservation.

        Args:
            client: OPNsense API client
            entity: Reservation entity to create

        Returns:
            API Result object
        """
        return client.kea_dhcpv4_add_reservation(entity)

    def update(self, client: 'BaseClient', uuid: str, entity: Reservation) -> Any:
        """
        Update an existing DHCP reservation.

        Args:
            client: OPNsense API client
            uuid: UUID of the reservation to update
            entity: Updated Reservation entity

        Returns:
            API Result object
        """
        return client.kea_dhcpv4_set_reservation(uuid, entity)

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a DHCP reservation.

        Args:
            client: OPNsense API client
            uuid: UUID of the reservation to delete

        Returns:
            API Result object
        """
        return client.kea_dhcpv4_del_reservation(uuid)

    def match(self, desired: Any, actual_list: List[Any]) -> tuple:
        """
        Override match to normalize MAC addresses before comparison.

        Args:
            desired: The desired reservation
            actual_list: List of actual reservations

        Returns:
            Tuple of (match_type, matched_entity, alternatives)
        """
        desired_mac = self.get_primary_key_value(desired)

        # Primary key match (MAC address)
        for actual in actual_list:
            actual_mac = self.get_primary_key_value(actual)
            if actual_mac and desired_mac and actual_mac == desired_mac:
                return ('exact', actual, [])

        # Secondary key matches
        alternatives = []
        for actual in actual_list:
            for key in self.secondary_keys:
                desired_val = getattr(desired, key, None)
                actual_val = getattr(actual, key, None)

                # Normalize values for comparison
                if desired_val is not None and actual_val is not None:
                    if str(desired_val).lower() == str(actual_val).lower():
                        if actual not in alternatives:
                            alternatives.append(actual)
                        break

        if len(alternatives) == 1:
            return ('secondary', alternatives[0], [])
        elif len(alternatives) > 1:
            return ('ambiguous', None, alternatives)

        return ('none', None, [])

    def create_entity(self, hw_address: str, ip_address: str,
                      hostname: Optional[str] = None,
                      subnet: Optional[str] = None,
                      description: Optional[str] = None,
                      **kwargs) -> Reservation:
        """
        Create a new Reservation entity instance.

        Args:
            hw_address: MAC address (e.g., 'aa:bb:cc:dd:ee:ff')
            ip_address: IP address to reserve
            hostname: Optional hostname
            subnet: Optional subnet UUID
            description: Optional description

        Returns:
            Reservation entity
        """
        entity_kwargs = {
            'hw_address': hw_address.lower(),  # Normalize to lowercase
            'ip_address': ip_address,
        }

        if hostname is not None:
            entity_kwargs['hostname'] = hostname
        if subnet is not None:
            entity_kwargs['subnet'] = subnet
        if description is not None:
            entity_kwargs['description'] = description

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return Reservation(**entity_kwargs)
