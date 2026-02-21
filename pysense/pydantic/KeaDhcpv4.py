from enum import Enum
from typing import Optional
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin
from pysense.pydantic.General import General, DhcpSocketTypeEnum
from pysense.pydantic.KeaDhcpv4Settings import Dhcpv4


class PeerRoleEnum(str, Enum):
    PRIMARY = "primary"
    STANDBY = "standby"


class Peer(UIAwareMixin):
    """
    Model for Kea DHCPv4 HA Peer
    """
    name: Optional[str] = None
    role: PeerRoleEnum = Field(default=PeerRoleEnum.PRIMARY)
    url: Optional[str] = None


class Reservation(UIAwareMixin):
    """
    Model for Kea DHCPv4 Reservation
    """
    subnet: Optional[str] = Field(default=None, description="Related subnet not found.")
    ip_address: Optional[str] = None
    hw_address: Optional[str] = None
    hostname: Optional[str] = None
    description: Optional[str] = None


class Subnet4(BoolAsIntMixin, UIAwareMixin):
    """
    Model for Kea DHCPv4 Subnet
    """
    subnet: Optional[str] = None
    next_server: Optional[str] = None
    option_data_autocollect: bool = Field(default=True)
    match_client_id: bool = Field(default=True, serialization_alias="match-client-id")
    pools: Optional[str] = None
    description: Optional[str] = None


# Aliases for clearer naming
KeaSubnet4 = Subnet4
KeaReservation = Reservation
KeaPeer = Peer
KeaGeneral = General
KeaDhcpv4 = Dhcpv4
