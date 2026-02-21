from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Rule(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Rule for OPNsense
    """

    class SnatrulesRuleIpprotocolEnum(str, Enum):
        INET = "inet"
        INET6 = "inet6"
    
    enabled: bool = Field(default=True)
    nonat: bool = Field(default=False)
    sequence: int = Field(default=1, ge=1, le=99999, description="Provide a valid sequence for sorting.")
    interface: str = Field(default="lan")
    ipprotocol: SnatrulesRuleIpprotocolEnum = Field(default=SnatrulesRuleIpprotocolEnum.INET)
    protocol: str = Field(default="any")
    source_net: str = Field(default="any")
    source_not: bool = Field(default=False)
    source_port: Optional[str] = Field(default=None, description="Please specify a valid portnumber, name, alias or range.")
    destination_net: str = Field(default="any")
    destination_not: bool = Field(default=False)
    destination_port: Optional[str] = Field(default=None, description="Please specify a valid portnumber, name, alias or range.")
    target: str = Field(default="wanip")
    target_port: Optional[str] = None
    log: bool = Field(default=False)
    categories: List[str] = Field(default_factory=list, description="Related category not found.")
    tagged: Optional[str] = Field(default=None, pattern=r"^([0-9a-zA-Z.,_\-]){0,512}$")
    description: Optional[str] = None

