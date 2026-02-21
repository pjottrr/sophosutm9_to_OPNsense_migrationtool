from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Rule(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Rule for OPNsense
    """

    class RuleRuleIpprotocolEnum(str, Enum):
        INET = "inet"
        INET6 = "inet6"
        INET46 = "inet46"

    class RuleRulePooloptsEnum(str, Enum):
        RR = "round-robin"
        RRSA = "round-robin sticky-address"
        RANDOM = "random"
        RANDOMSA = "random sticky-address"
        SOURCE_HASH = "source-hash"
        BITMASK = "bitmask"

    class RuleRuleNatreflectionEnum(str, Enum):
        PURENAT = "purenat"
        DISABLE = "disable"

    class RuleRulePassEnum(str, Enum):
        RULE = "rule"
        PASS = "pass"
    
    sequence: int = Field(default=1, ge=1, le=999999, description="Sequence shall be between 1 and 999999.")
    disabled: Optional[bool] = None
    nordr: Optional[bool] = None
    interface: List[str] = Field(default_factory=list)
    ipprotocol: Optional[RuleRuleIpprotocolEnum] = None
    protocol: Optional[str] = None
    target: Optional[str] = None
    local_port: Optional[int] = Field(default=None, description="Please specify a valid port number or alias.", serialization_alias="local-port")
    poolopts: Optional[RuleRulePooloptsEnum] = None
    log: Optional[bool] = None
    category: List[str] = Field(default_factory=list)
    categories: Optional[str] = None
    descr: Optional[str] = None
    tag: Optional[str] = None
    tagged: Optional[str] = None
    nosync: Optional[bool] = None
    natreflection: Optional[RuleRuleNatreflectionEnum] = None
    pass_mode: Optional[RuleRulePassEnum] = Field(default=None, serialization_alias="pass")
    associated_rule_id: Optional[str] = Field(default=None, serialization_alias="associated-rule-id")

