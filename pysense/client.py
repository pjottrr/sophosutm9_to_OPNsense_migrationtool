from pysense.api.acmeclient_accounts_client import AcmeclientAccountsClient
from pysense.api.acmeclient_validations_client import AcmeclientValidationsClient
from pysense.api.auth_group_client import AuthGroup
from pysense.api.auth_user_client import AuthUser
from pysense.api.firewall_alias_client import FirewallAliasClient
from pysense.api.firewall_category_client import FirewallCategoryClient
from pysense.api.firewall_filter_client import FirewallFilterClient
from pysense.api.firewall_snat_client import FirewallSnatClient
from pysense.api.firewall_one_to_one_client import FirewallOneToOneClient
from pysense.api.firewall_dnat_client import FirewallDnatClient
from pysense.api.haproxy import Haproxy
from pysense.api.haproxy_export_client import HaproxyExportClient
from pysense.api.haproxy_settings_client import HaproxySettingsClient
from pysense.api.interfaces_overview_client import InterfacesOverviewClient
from pysense.api.interfaces_vlan_client import InterfacesVlanClient
from pysense.api.kea_dhcpv4_client import KeaDhcpv4Client
from pysense.api.unbound_client import UnboundClient
from pysense.api.trust import Trust
from pysense.base_client import BaseClient
from pysense.api.core_backup_client import CoreBackupClient
from pysense.api.core_firmware_client import CoreFirmwareClient


class Client(UnboundClient, KeaDhcpv4Client, InterfacesVlanClient, InterfacesOverviewClient, FirewallDnatClient, FirewallOneToOneClient, FirewallSnatClient, FirewallFilterClient, FirewallCategoryClient, FirewallAliasClient, Haproxy, AuthGroup, AuthUser, CoreBackupClient, CoreFirmwareClient, Trust, HaproxyExportClient, HaproxySettingsClient,
             AcmeclientAccountsClient, AcmeclientValidationsClient, BaseClient):

    def state(self) -> 'StateManager':
        """
        Get a StateManager for desired state configuration.

        The StateManager provides a declarative interface to define
        desired network state and compare/apply changes to OPNsense.

        Example:
            >>> state = client.state()
            >>> state.dns_host(hostname='server1', domain='lan', ip='192.168.1.100')
            >>> changes = state.plan()
            >>> state.apply(auto_approve=True)

        Returns:
            StateManager instance bound to this client
        """
        from pysense.state import StateManager
        return StateManager(self)
