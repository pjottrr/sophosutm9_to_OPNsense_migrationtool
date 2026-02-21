from pysense.base_client import BaseClient
from pysense.pydantic.KeaDhcpv4 import Subnet4, Reservation, Peer
from pysense.pydantic.KeaDhcpv4Settings import Dhcpv4
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import Subnet4SearchResult, ReservationSearchResult, PeerSearchResult


class KeaDhcpv4Client(BaseClient):
    """API client for Kea DHCPv4 operations"""

    # Subnet operations
    def kea_dhcpv4_search_subnet(self, search: SearchRequest = None) -> Subnet4SearchResult:
        """Search DHCPv4 subnets"""
        data = self._search('kea/dhcpv4/search_subnet', search)
        return Subnet4SearchResult.from_ui_dict(data, Subnet4)

    def kea_dhcpv4_get_subnet(self, uuid: str = None) -> Subnet4:
        """Get a subnet by UUID, or get defaults for new item if uuid is None"""
        data = self._get('kea/dhcpv4/get_subnet' + self._get_arg_formatter(uuid))
        return Subnet4.from_ui_dict(data)

    def kea_dhcpv4_add_subnet(self, subnet: Subnet4) -> Result:
        """Add a new subnet"""
        data = self._post('kea/dhcpv4/add_subnet', subnet)
        return Result(**data)

    def kea_dhcpv4_set_subnet(self, uuid: str, subnet: Subnet4) -> Result:
        """Update an existing subnet"""
        data = self._post(f'kea/dhcpv4/set_subnet/{uuid}', subnet)
        return Result(**data)

    def kea_dhcpv4_del_subnet(self, uuid: str) -> Result:
        """Delete a subnet"""
        data = self._post(f'kea/dhcpv4/del_subnet/{uuid}', '')
        return Result(**data)

    # Reservation operations
    def kea_dhcpv4_search_reservation(self, search: SearchRequest = None) -> ReservationSearchResult:
        """Search DHCPv4 reservations"""
        data = self._search('kea/dhcpv4/search_reservation', search)
        return ReservationSearchResult.from_ui_dict(data, Reservation)

    def kea_dhcpv4_get_reservation(self, uuid: str = None) -> Reservation:
        """Get a reservation by UUID, or get defaults for new item if uuid is None"""
        data = self._get('kea/dhcpv4/get_reservation' + self._get_arg_formatter(uuid))
        return Reservation.from_ui_dict(data)

    def kea_dhcpv4_add_reservation(self, reservation: Reservation) -> Result:
        """Add a new reservation"""
        data = self._post('kea/dhcpv4/add_reservation', reservation)
        return Result(**data)

    def kea_dhcpv4_set_reservation(self, uuid: str, reservation: Reservation) -> Result:
        """Update an existing reservation"""
        data = self._post(f'kea/dhcpv4/set_reservation/{uuid}', reservation)
        return Result(**data)

    def kea_dhcpv4_del_reservation(self, uuid: str) -> Result:
        """Delete a reservation"""
        data = self._post(f'kea/dhcpv4/del_reservation/{uuid}', '')
        return Result(**data)

    def kea_dhcpv4_download_reservations(self) -> str:
        """Download reservations as CSV"""
        return self._get('kea/dhcpv4/download_reservations', raw=True)

    def kea_dhcpv4_upload_reservations(self, data: dict) -> dict:
        """Upload reservations from CSV"""
        return self._post('kea/dhcpv4/upload_reservations', data)

    # Peer operations (HA)
    def kea_dhcpv4_search_peer(self, search: SearchRequest = None) -> PeerSearchResult:
        """Search DHCPv4 HA peers"""
        data = self._search('kea/dhcpv4/search_peer', search)
        return PeerSearchResult.from_ui_dict(data, Peer)

    def kea_dhcpv4_get_peer(self, uuid: str = None) -> Peer:
        """Get a peer by UUID, or get defaults for new item if uuid is None"""
        data = self._get('kea/dhcpv4/get_peer' + self._get_arg_formatter(uuid))
        return Peer.from_ui_dict(data)

    def kea_dhcpv4_add_peer(self, peer: Peer) -> Result:
        """Add a new HA peer"""
        data = self._post('kea/dhcpv4/add_peer', peer)
        return Result(**data)

    def kea_dhcpv4_set_peer(self, uuid: str, peer: Peer) -> Result:
        """Update an existing HA peer"""
        data = self._post(f'kea/dhcpv4/set_peer/{uuid}', peer)
        return Result(**data)

    def kea_dhcpv4_del_peer(self, uuid: str) -> Result:
        """Delete an HA peer"""
        data = self._post(f'kea/dhcpv4/del_peer/{uuid}', '')
        return Result(**data)

    # General settings
    def kea_dhcpv4_get(self) -> Dhcpv4:
        """Get all DHCPv4 settings"""
        data = self._get('kea/dhcpv4/get')
        return Dhcpv4.from_ui_dict(data)

    def kea_dhcpv4_set(self, settings: Dhcpv4) -> Result:
        """Set DHCPv4 settings"""
        result = self._post('kea/dhcpv4/set', settings)
        return Result(**result)
