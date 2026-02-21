from pysense.base_client import BaseClient
from pysense.pydantic.InterfaceOverview import InterfaceExport


class InterfacesOverviewClient(BaseClient):

    def interface_overview_export(self) -> InterfaceExport:
        """
        Get interface overview information.

        Returns an InterfaceExport object with query methods:
            - get_by_identifier('wan') - by OPNsense identifier
            - get_by_device('vmx0') - by device name
            - get_by_description('WAN') - by description
            - get_by_mac('00:0c:29:...') - by MAC address
            - get_by_ip('192.168.1.1') - by IP address
            - get_physical() - all physical interfaces
            - get_virtual() - all virtual interfaces
            - get_enabled() - all enabled interfaces
            - get_up() / get_down() - by status
            - get_vlans() - all VLAN interfaces
            - get_assigned() / get_unassigned() - by assignment status
        """
        data = self._get('interfaces/overview/export')
        return InterfaceExport.from_api_response(data)
