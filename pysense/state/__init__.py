"""
Desired state configuration system for OPNsense.

This module provides a declarative way to define desired network state
and automatically compare/apply changes to OPNsense.

Example:
    >>> from pysense.client import Client
    >>> from pysense.state import StateManager
    >>>
    >>> client = Client(base_url='https://opnsense.local/api', ...)
    >>> state = StateManager(client)
    >>>
    >>> # Declare desired state
    >>> state.dns_host(hostname='server1', domain='lan', ip='192.168.1.100')
    >>> state.dhcp_reservation(mac='aa:bb:cc:dd:ee:ff', ip='192.168.1.50')
    >>>
    >>> # Plan and review changes
    >>> changes = state.plan()
    >>> print(state.format_plan(changes))
    >>>
    >>> # Apply changes
    >>> state.apply(auto_approve=True)
"""
from pysense.state.state_manager import StateManager, StateChange, ChangeType

__all__ = [
    'StateManager',
    'StateChange',
    'ChangeType',
]
