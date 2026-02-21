from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Vlan(UIAwareMixin):
    """
    Generated model for Vlan for OPNsense
    """

    class VlanVlanPcpEnum(str, Enum):
        PCP1 = "1"
        PCP0 = "0"
        PCP2 = "2"
        PCP3 = "3"
        PCP4 = "4"
        PCP5 = "5"
        PCP6 = "6"
        PCP7 = "7"

    class VlanVlanProtoEnum(str, Enum):
        OPT1 = "802.1q"
        OPT2 = "802.1ad"
    
    interface: Optional[str] = Field(default=None, serialization_alias="if")
    tag: Optional[int] = Field(default=None, ge=1, le=4094)
    pcp: VlanVlanPcpEnum = Field(default=VlanVlanPcpEnum.PCP0)
    proto: Optional[VlanVlanProtoEnum] = None
    descr: Optional[str] = None
    vlanif: Optional[str] = Field(default=None)

