from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

"""
API documentation is not yet complete for this model. 
Current design is based on the json responses observed
This may get implemented in the 26.1 release 
"""

class StatusEnum(str, Enum):
    UP = "up"
    DOWN = "down"


class LinkTypeEnum(str, Enum):
    DHCP = "dhcp"
    STATIC = "static"
    PPPOE = "pppoe"
    PPTP = "pptp"
    L2TP = "l2tp"
    NONE = "none"


class Nd6(BaseModel):
    flags: List[str] = Field(default_factory=list)


class InterfaceStatistics(BaseModel):
    device: Optional[str] = None
    driver: Optional[str] = None
    index: Optional[int] = None
    flags: Optional[str] = None
    promiscuous_listeners: Optional[int] = Field(default=None, alias="promiscuous listeners")
    send_queue_length: Optional[int] = Field(default=None, alias="send queue length")
    send_queue_max_length: Optional[int] = Field(default=None, alias="send queue max length")
    send_queue_drops: Optional[int] = Field(default=None, alias="send queue drops")
    type: Optional[str] = None
    address_length: Optional[int] = Field(default=None, alias="address length")
    header_length: Optional[int] = Field(default=None, alias="header length")
    link_state: Optional[int] = Field(default=None, alias="link state")
    vhid: Optional[int] = None
    datalen: Optional[int] = None
    mtu: Optional[int] = None
    metric: Optional[int] = None
    line_rate: Optional[str] = Field(default=None, alias="line rate")
    packets_received: Optional[int] = Field(default=None, alias="packets received")
    input_errors: Optional[int] = Field(default=None, alias="input errors")
    packets_transmitted: Optional[int] = Field(default=None, alias="packets transmitted")
    output_errors: Optional[int] = Field(default=None, alias="output errors")
    collisions: Optional[int] = None
    bytes_received: Optional[int] = Field(default=None, alias="bytes received")
    bytes_transmitted: Optional[int] = Field(default=None, alias="bytes transmitted")
    multicasts_received: Optional[int] = Field(default=None, alias="multicasts received")
    multicasts_transmitted: Optional[int] = Field(default=None, alias="multicasts transmitted")
    input_queue_drops: Optional[int] = Field(default=None, alias="input queue drops")
    packets_for_unknown_protocol: Optional[int] = Field(default=None, alias="packets for unknown protocol")
    hw_offload_capabilities: Optional[str] = Field(default=None, alias="HW offload capabilities")
    uptime_at_attach_or_stat_reset: Optional[int] = Field(default=None, alias="uptime at attach or stat reset")


class InterfaceConfig(BaseModel):
    interface: Optional[str] = Field(default=None, alias="if")
    descr: Optional[str] = None
    enable: Optional[str] = None
    spoofmac: Optional[str] = None
    blockbogons: Optional[str] = None
    ipaddr: Optional[str] = None
    subnet: Optional[str] = None
    ipaddrv6: Optional[str] = None
    subnetv6: Optional[str] = None
    dhcphostname: Optional[str] = None
    alias_address: Optional[str] = Field(default=None, alias="alias-address")
    alias_subnet: Optional[str] = Field(default=None, alias="alias-subnet")
    dhcprejectfrom: Optional[str] = None
    track6_interface: Optional[str] = Field(default=None, alias="track6-interface")
    track6_prefix_id: Optional[str] = Field(default=None, alias="track6-prefix-id")
    identifier: Optional[str] = None
    internal_dynamic: Optional[str] = None
    type: Optional[str] = None
    virtual: Optional[str] = None

    class Config:
        populate_by_name = True


class IPv4Address(BaseModel):
    ipaddr: Optional[str] = None


class IPv6Address(BaseModel):
    ipaddr: Optional[str] = None


class Interface(BaseModel):
    """Single interface from OPNsense interface export"""
    flags: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    options: List[str] = Field(default_factory=list)
    macaddr: Optional[str] = None
    macaddr_hw: Optional[str] = None
    supported_media: List[str] = Field(default_factory=list)
    is_physical: bool = False
    device: Optional[str] = None
    mtu: Optional[int] = None
    media: Optional[str] = None
    media_raw: Optional[str] = None
    status: Optional[StatusEnum] = None
    nd6: Optional[Nd6] = None
    statistics: Optional[InterfaceStatistics] = None
    routes: List[str] = Field(default_factory=list)
    config: Optional[InterfaceConfig] = None
    groups: List[str] = Field(default_factory=list)
    ifctl_nameserver: List[str] = Field(default_factory=list, alias="ifctl.nameserver")
    ifctl_router: List[str] = Field(default_factory=list, alias="ifctl.router")
    ifctl_searchdomain: List[str] = Field(default_factory=list, alias="ifctl.searchdomain")
    identifier: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = False
    link_type: Optional[LinkTypeEnum] = None
    addr4: Optional[str] = None
    addr6: Optional[str] = None
    ipv4: List[IPv4Address] = Field(default_factory=list)
    ipv6: List[IPv6Address] = Field(default_factory=list)
    vlan_tag: Optional[int] = None
    gateways: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


# Backwards compatibility alias
InterfaceOverview = Interface


class InterfaceExport(BaseModel):
    """
    Collection of interfaces from OPNsense interface export API.
    Provides query methods to find interfaces by various criteria.
    """
    interfaces: List[Interface] = Field(default_factory=list)

    @classmethod
    def from_api_response(cls, data: List[dict]) -> 'InterfaceExport':
        """Create InterfaceExport from API response list"""
        interfaces = [Interface(**iface) for iface in data]
        return cls(interfaces=interfaces)

    def __iter__(self):
        """Allow iteration over interfaces"""
        return iter(self.interfaces)

    def __len__(self):
        """Return number of interfaces"""
        return len(self.interfaces)

    def __getitem__(self, index):
        """Allow indexing"""
        return self.interfaces[index]

    def get_by_identifier(self, identifier: str) -> Optional[Interface]:
        """Get interface by OPNsense identifier (e.g., 'wan', 'lan', 'opt1')"""
        for iface in self.interfaces:
            if iface.identifier == identifier:
                return iface
        return None

    def get_by_device(self, device: str) -> Optional[Interface]:
        """Get interface by device name (e.g., 'vmx0', 'em0', 'igb0')"""
        for iface in self.interfaces:
            if iface.device == device:
                return iface
        return None

    def get_by_description(self, description: str) -> Optional[Interface]:
        """Get interface by description (e.g., 'WAN', 'LAN')"""
        for iface in self.interfaces:
            if iface.description == description:
                return iface
        return None

    def get_by_mac(self, mac: str) -> Optional[Interface]:
        """Get interface by MAC address"""
        mac_lower = mac.lower()
        for iface in self.interfaces:
            if iface.macaddr and iface.macaddr.lower() == mac_lower:
                return iface
        return None

    def get_by_ip(self, ip: str) -> Optional[Interface]:
        """Get interface by IPv4 or IPv6 address (without CIDR)"""
        for iface in self.interfaces:
            if iface.addr4 and iface.addr4.split('/')[0] == ip:
                return iface
            if iface.addr6 and iface.addr6.split('/')[0] == ip:
                return iface
        return None

    def get_physical(self) -> List[Interface]:
        """Get all physical interfaces"""
        return [iface for iface in self.interfaces if iface.is_physical]

    def get_virtual(self) -> List[Interface]:
        """Get all virtual interfaces (non-physical)"""
        return [iface for iface in self.interfaces if not iface.is_physical]

    def get_enabled(self) -> List[Interface]:
        """Get all enabled interfaces"""
        return [iface for iface in self.interfaces if iface.enabled]

    def get_up(self) -> List[Interface]:
        """Get all interfaces with status 'up'"""
        return [iface for iface in self.interfaces if iface.status == StatusEnum.UP]

    def get_down(self) -> List[Interface]:
        """Get all interfaces with status 'down'"""
        return [iface for iface in self.interfaces if iface.status == StatusEnum.DOWN]

    def get_by_vlan_tag(self, tag: int) -> Optional[Interface]:
        """Get interface by VLAN tag"""
        for iface in self.interfaces:
            if iface.vlan_tag == tag:
                return iface
        return None

    def get_vlans(self) -> List[Interface]:
        """Get all VLAN interfaces"""
        return [iface for iface in self.interfaces if iface.vlan_tag is not None]

    def get_assigned(self) -> List[Interface]:
        """Get all assigned interfaces (have an identifier)"""
        return [iface for iface in self.interfaces if iface.identifier]

    def get_unassigned(self) -> List[Interface]:
        """Get all unassigned interfaces (no identifier)"""
        return [iface for iface in self.interfaces if not iface.identifier]

    def filter_by_group(self, group: str) -> List[Interface]:
        """Get all interfaces belonging to a specific group"""
        return [iface for iface in self.interfaces if group in iface.groups]

    def filter_by_link_type(self, link_type: LinkTypeEnum) -> List[Interface]:
        """Get all interfaces with a specific link type"""
        return [iface for iface in self.interfaces if iface.link_type == link_type]
