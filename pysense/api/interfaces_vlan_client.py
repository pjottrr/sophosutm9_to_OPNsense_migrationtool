from pysense.base_client import BaseClient
from pysense.pydantic.Vlan import Vlan
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import VlanSearchResult


class InterfacesVlanClient(BaseClient):

    def vlan_search_item(self, search: SearchRequest = None) -> VlanSearchResult:
        """Search VLAN items"""
        data = self._search('interfaces/vlan_settings/searchItem', search)
        return VlanSearchResult.from_ui_dict(data, Vlan)

    def vlan_get_item(self, uuid: str = None) -> Vlan:
        """Get a VLAN item by UUID, or get defaults for new item if uuid is None"""
        data = self._get('interfaces/vlan_settings/getItem' + self._get_arg_formatter(uuid))
        return Vlan.from_ui_dict(data)

    def vlan_add_item(self, vlan: Vlan) -> Result:
        """Add a new VLAN item"""
        data = self._post('interfaces/vlan_settings/addItem', vlan)
        return Result(**data)

    def vlan_set_item(self, uuid: str, vlan: Vlan) -> Result:
        """Update an existing VLAN item"""
        data = self._post(f'interfaces/vlan_settings/setItem/{uuid}', vlan)
        return Result(**data)

    def vlan_del_item(self, uuid: str) -> Result:
        """Delete a VLAN item"""
        data = self._post(f'interfaces/vlan_settings/delItem/{uuid}', '')
        return Result(**data)

    def vlan_get(self) -> dict:
        """Get all VLAN settings"""
        return self._get('interfaces/vlan_settings/get')

    def vlan_set(self, data: dict) -> Result:
        """Set VLAN settings"""
        result = self._post('interfaces/vlan_settings/set', data)
        return Result(**result)

    def vlan_reconfigure(self) -> dict:
        """Apply VLAN configuration changes"""
        return self._post('interfaces/vlan_settings/reconfigure', '')
