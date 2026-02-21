from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin


class DhcpSocketTypeEnum(str, Enum):
    UDP = "udp"
    RAW = "raw"


class General(BoolAsIntMixin, UIAwareMixin):
    """
    Model for Kea DHCPv4 General Settings
    """
    enabled: bool = Field(default=False)
    manual_config: bool = Field(default=False)
    interfaces: Optional[List[str]] = Field(default_factory=list)
    valid_lifetime: int = Field(default=4000)
    fwrules: bool = Field(default=True)
    dhcp_socket_type: DhcpSocketTypeEnum = Field(default=DhcpSocketTypeEnum.RAW)
