"""
Handler for Unbound DNS host overrides.
"""
from typing import List, Any, Optional, TYPE_CHECKING

from pysense.state.handlers.base_handler import EntityHandler
from pysense.pydantic.Unbound import Host

if TYPE_CHECKING:
    from pysense.base_client import BaseClient


class DnsHostHandler(EntityHandler):
    """
    Handler for Unbound DNS host override entities.

    Manages DNS A/AAAA/MX/TXT records configured as host overrides
    in OPNsense's Unbound DNS resolver.
    """

    @property
    def entity_type(self) -> str:
        return "dns_host"

    @property
    def primary_key(self) -> str:
        # Using composite key via get_primary_key_value override
        return "hostname"

    @property
    def secondary_keys(self) -> List[str]:
        return ["server"]  # IP address as secondary match

    @property
    def comparable_fields(self) -> List[str]:
        return [
            "enabled",
            "hostname",
            "domain",
            "rr",
            "server",
            "mxprio",
            "mx",
            "ttl",
            "txtdata",
            "description"
        ]

    def get_primary_key_value(self, entity: Any) -> str:
        """
        Composite key: hostname.domain

        Args:
            entity: Host entity

        Returns:
            Composite key string (e.g., 'server1.lan')
        """
        hostname = getattr(entity, 'hostname', '') or ''
        domain = getattr(entity, 'domain', '') or ''
        return f"{hostname}.{domain}"

    def fetch_all(self, client: 'BaseClient') -> List[Host]:
        """
        Fetch all DNS host overrides from OPNsense.

        Args:
            client: OPNsense API client

        Returns:
            List of Host entities
        """
        result = client.unbound_search_host_override()
        return result.rows

    def create(self, client: 'BaseClient', entity: Host) -> Any:
        """
        Create a new DNS host override.

        Args:
            client: OPNsense API client
            entity: Host entity to create

        Returns:
            API Result object
        """
        return client.unbound_add_host_override(entity)

    def update(self, client: 'BaseClient', uuid: str, entity: Host) -> Any:
        """
        Update an existing DNS host override.

        Args:
            client: OPNsense API client
            uuid: UUID of the host override to update
            entity: Updated Host entity

        Returns:
            API Result object
        """
        return client.unbound_set_host_override(uuid, entity)

    def delete(self, client: 'BaseClient', uuid: str) -> Any:
        """
        Delete a DNS host override.

        Args:
            client: OPNsense API client
            uuid: UUID of the host override to delete

        Returns:
            API Result object
        """
        return client.unbound_del_host_override(uuid)

    def create_entity(self, hostname: str, domain: str, server: str,
                      enabled: bool = True,
                      rr: Host.HostsHostRrEnum = None,
                      mxprio: Optional[int] = None,
                      mx: Optional[str] = None,
                      ttl: Optional[int] = None,
                      txtdata: Optional[str] = None,
                      description: Optional[str] = None,
                      **kwargs) -> Host:
        """
        Create a new Host entity instance.

        Args:
            hostname: Hostname (e.g., 'server1')
            domain: Domain (e.g., 'lan')
            server: IP address (e.g., '192.168.1.100')
            enabled: Whether the host override is enabled
            rr: Record type (A, AAAA, MX, TXT)
            mxprio: MX priority (for MX records)
            mx: MX target hostname (for MX records)
            ttl: Time-to-live
            txtdata: TXT record data
            description: Description

        Returns:
            Host entity
        """
        entity_kwargs = {
            'enabled': enabled,
            'hostname': hostname,
            'domain': domain,
            'server': server,
        }

        if rr is not None:
            entity_kwargs['rr'] = rr
        if mxprio is not None:
            entity_kwargs['mxprio'] = mxprio
        if mx is not None:
            entity_kwargs['mx'] = mx
        if ttl is not None:
            entity_kwargs['ttl'] = ttl
        if txtdata is not None:
            entity_kwargs['txtdata'] = txtdata
        if description is not None:
            entity_kwargs['description'] = description

        # Include any extra kwargs
        entity_kwargs.update(kwargs)

        return Host(**entity_kwargs)
