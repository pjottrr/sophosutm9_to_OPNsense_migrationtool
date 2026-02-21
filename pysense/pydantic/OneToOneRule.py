from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin


class Rule(BoolAsIntMixin, UIAwareMixin):
    """
    OPNsense 1:1 NAT (One-to-One NAT) rule model.

    Maps external IPs to internal IPs bidirectionally (BINAT) or
    unidirectionally (NAT) for inbound traffic.
    """

    class TypeEnum(str, Enum):
        """NAT type: bidirectional or unidirectional"""
        BINAT = "binat"
        NAT = "nat"

    class NatReflectionEnum(str, Enum):
        """NAT reflection setting for hairpin NAT"""
        DEFAULT = ""
        ENABLE = "enable"
        DISABLE = "disable"

    enabled: bool = Field(default=True)
    log: bool = Field(default=False)
    sequence: int = Field(default=1, ge=1, le=99999, description="Provide a valid sequence for sorting.")
    interface: str = Field(default="wan")
    type: TypeEnum = Field(default=TypeEnum.BINAT)
    source_net: str = Field(default="any", description="Internal network/host")
    source_not: bool = Field(default=False)
    destination_net: str = Field(default="any", description="Destination network filter")
    destination_not: bool = Field(default=False)
    external: str = Field(default="", description="External IP address for NAT")
    natreflection: NatReflectionEnum = Field(default=NatReflectionEnum.DEFAULT)
    categories: List[str] = Field(default_factory=list, description="Related category not found.")
    description: Optional[str] = None
