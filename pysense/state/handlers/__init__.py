"""
Entity handlers for state management.
"""
from pysense.state.handlers.base_handler import EntityHandler
from pysense.state.handlers.dns_host_handler import DnsHostHandler
from pysense.state.handlers.dhcp_reservation_handler import DhcpReservationHandler
from pysense.state.handlers.firewall_alias_handler import FirewallAliasHandler
from pysense.state.handlers.firewall_rule_handler import FirewallRuleHandler

__all__ = [
    'EntityHandler',
    'DnsHostHandler',
    'DhcpReservationHandler',
    'FirewallAliasHandler',
    'FirewallRuleHandler',
]
