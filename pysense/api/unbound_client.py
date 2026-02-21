from typing import List

from pysense.base_client import BaseClient
from pysense.pydantic.Unbound import Acl, Blocklist, Dot, Alias, Host, General, Advanced, UnboundSettings
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import (
    UnboundAclSearchResult, UnboundBlocklistSearchResult, UnboundDotSearchResult,
    UnboundAliasSearchResult, UnboundHostSearchResult
)


class UnboundClient(BaseClient):
    """API client for Unbound DNS operations"""

    # ACL operations
    def unbound_search_acl(self, search: SearchRequest = None) -> UnboundAclSearchResult:
        """Search Unbound ACLs"""
        data = self._search('unbound/settings/searchAcl', search)
        return UnboundAclSearchResult.from_ui_dict(data, Acl)

    def unbound_get_acl(self, uuid: str = None) -> Acl:
        """Get an ACL by UUID, or get defaults for new item if uuid is None"""
        data = self._get('unbound/settings/getAcl' + self._get_arg_formatter(uuid))
        return Acl.from_ui_dict(data)

    def unbound_add_acl(self, acl: Acl) -> Result:
        """Add a new ACL"""
        data = self._post('unbound/settings/addAcl', acl)
        return Result(**data)

    def unbound_set_acl(self, uuid: str, acl: Acl) -> Result:
        """Update an existing ACL"""
        data = self._post(f'unbound/settings/setAcl/{uuid}', acl)
        return Result(**data)

    def unbound_del_acl(self, uuid: str) -> Result:
        """Delete an ACL"""
        data = self._post(f'unbound/settings/delAcl/{uuid}', '')
        return Result(**data)

    def unbound_toggle_acl(self, uuid: str, enabled: bool = None) -> Result:
        """Toggle an ACL's enabled state"""
        endpoint = f'unbound/settings/toggleAcl/{uuid}'
        if enabled is not None:
            endpoint += f'/{1 if enabled else 0}'
        data = self._post(endpoint, '')
        return Result(**data)

    # DNSBL (Blocklist) operations
    def unbound_search_dnsbl(self, search: SearchRequest = None) -> UnboundBlocklistSearchResult:
        """Search Unbound DNS blocklists"""
        data = self._search('unbound/settings/searchDnsbl', search)
        return UnboundBlocklistSearchResult.from_ui_dict(data, Blocklist)

    def unbound_get_dnsbl(self, uuid: str = None) -> Blocklist:
        """Get a blocklist by UUID, or get defaults for new item if uuid is None"""
        data = self._get('unbound/settings/getDnsbl' + self._get_arg_formatter(uuid))
        return Blocklist.from_ui_dict(data)

    def unbound_add_dnsbl(self, blocklist: Blocklist) -> Result:
        """Add a new DNS blocklist"""
        data = self._post('unbound/settings/addDnsbl', blocklist)
        return Result(**data)

    def unbound_set_dnsbl(self, uuid: str, blocklist: Blocklist) -> Result:
        """Update an existing DNS blocklist"""
        data = self._post(f'unbound/settings/setDnsbl/{uuid}', blocklist)
        return Result(**data)

    def unbound_del_dnsbl(self, uuid: str) -> Result:
        """Delete a DNS blocklist"""
        data = self._post(f'unbound/settings/delDnsbl/{uuid}', '')
        return Result(**data)

    def unbound_toggle_dnsbl(self, uuid: str, enabled: bool = None) -> Result:
        """Toggle a DNS blocklist's enabled state"""
        endpoint = f'unbound/settings/toggleDnsbl/{uuid}'
        if enabled is not None:
            endpoint += f'/{1 if enabled else 0}'
        data = self._post(endpoint, '')
        return Result(**data)

    def unbound_update_blocklist(self) -> Result:
        """Update/download DNS blocklists"""
        data = self._post('unbound/settings/updateBlocklist', '')
        return Result(**data)

    # Forward (DoT) operations
    def unbound_search_forward(self, search: SearchRequest = None) -> UnboundDotSearchResult:
        """Search Unbound forwarding/DoT entries"""
        data = self._search('unbound/settings/searchForward', search)
        return UnboundDotSearchResult.from_ui_dict(data, Dot)

    def unbound_get_forward(self, uuid: str = None) -> Dot:
        """Get a forward entry by UUID, or get defaults for new item if uuid is None"""
        data = self._get('unbound/settings/getForward' + self._get_arg_formatter(uuid))
        return Dot.from_ui_dict(data)

    def unbound_add_forward(self, forward: Dot) -> Result:
        """Add a new forwarding/DoT entry"""
        data = self._post('unbound/settings/addForward', forward)
        return Result(**data)

    def unbound_set_forward(self, uuid: str, forward: Dot) -> Result:
        """Update an existing forwarding/DoT entry"""
        data = self._post(f'unbound/settings/setForward/{uuid}', forward)
        return Result(**data)

    def unbound_del_forward(self, uuid: str) -> Result:
        """Delete a forwarding/DoT entry"""
        data = self._post(f'unbound/settings/delForward/{uuid}', '')
        return Result(**data)

    def unbound_toggle_forward(self, uuid: str, enabled: bool = None) -> Result:
        """Toggle a forwarding entry's enabled state"""
        endpoint = f'unbound/settings/toggleForward/{uuid}'
        if enabled is not None:
            endpoint += f'/{1 if enabled else 0}'
        data = self._post(endpoint, '')
        return Result(**data)

    # Host Alias operations
    def unbound_search_host_alias(self, search: SearchRequest = None) -> UnboundAliasSearchResult:
        """Search Unbound host aliases"""
        data = self._search('unbound/settings/searchHostAlias', search)
        return UnboundAliasSearchResult.from_ui_dict(data, Alias)

    def unbound_get_host_alias(self, uuid: str = None) -> Alias:
        """Get a host alias by UUID, or get defaults for new item if uuid is None"""
        data = self._get('unbound/settings/getHostAlias' + self._get_arg_formatter(uuid))
        return Alias.from_ui_dict(data)

    def unbound_add_host_alias(self, alias: Alias) -> Result:
        """Add a new host alias"""
        data = self._post('unbound/settings/addHostAlias', alias)
        return Result(**data)

    def unbound_set_host_alias(self, uuid: str, alias: Alias) -> Result:
        """Update an existing host alias"""
        data = self._post(f'unbound/settings/setHostAlias/{uuid}', alias)
        return Result(**data)

    def unbound_del_host_alias(self, uuid: str) -> Result:
        """Delete a host alias"""
        data = self._post(f'unbound/settings/delHostAlias/{uuid}', '')
        return Result(**data)

    def unbound_toggle_host_alias(self, uuid: str, enabled: bool = None) -> Result:
        """Toggle a host alias's enabled state"""
        endpoint = f'unbound/settings/toggleHostAlias/{uuid}'
        if enabled is not None:
            endpoint += f'/{1 if enabled else 0}'
        data = self._post(endpoint, '')
        return Result(**data)

    # Host Override operations
    def unbound_search_host_override(self, search: SearchRequest = None) -> UnboundHostSearchResult:
        """Search Unbound host overrides"""
        data = self._search('unbound/settings/searchHostOverride', search)
        return UnboundHostSearchResult.from_ui_dict(data, Host)

    def unbound_get_host_override(self, uuid: str = None) -> Host:
        """Get a host override by UUID, or get defaults for new item if uuid is None"""
        data = self._get('unbound/settings/getHostOverride' + self._get_arg_formatter(uuid))
        return Host.from_ui_dict(data)

    def unbound_add_host_override(self, host: Host) -> Result:
        """Add a new host override"""
        data = self._post('unbound/settings/addHostOverride', host)
        return Result(**data)

    def unbound_set_host_override(self, uuid: str, host: Host) -> Result:
        """Update an existing host override"""
        data = self._post(f'unbound/settings/setHostOverride/{uuid}', host)
        return Result(**data)

    def unbound_del_host_override(self, uuid: str) -> Result:
        """Delete a host override"""
        data = self._post(f'unbound/settings/delHostOverride/{uuid}', '')
        return Result(**data)

    def unbound_toggle_host_override(self, uuid: str, enabled: bool = None) -> Result:
        """Toggle a host override's enabled state"""
        endpoint = f'unbound/settings/toggleHostOverride/{uuid}'
        if enabled is not None:
            endpoint += f'/{1 if enabled else 0}'
        data = self._post(endpoint, '')
        return Result(**data)

    # General settings
    def unbound_get(self) -> UnboundSettings:
        """Get all Unbound settings"""
        data = self._get('unbound/settings/get')
        return UnboundSettings.from_ui_dict(data)

    def unbound_set(self, settings: UnboundSettings) -> Result:
        """Set Unbound settings"""
        result = self._post('unbound/settings/set', settings)
        return Result(**result)

    def unbound_get_nameservers(self) -> List[str]:
        """Get configured nameservers"""
        return self._get('unbound/settings/getNameservers')
