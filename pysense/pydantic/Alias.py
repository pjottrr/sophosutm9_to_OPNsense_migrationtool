from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Alias(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Alias for OPNsense
    """

    class AliasesAliasTypeEnum(str, Enum):
        HOST = "host"
        NETWORK = "network"
        PORT = "port"
        URL = "url"
        URLTABLE = "urltable"
        URLJSON = "urljson"
        GEOIP = "geoip"
        NETWORKGROUP = "networkgroup"
        MAC = "mac"
        ASN = "asn"
        DYNIPV6HOST = "dynipv6host"
        AUTHGROUP = "authgroup"
        INTERNAL = "internal"
        EXTERNAL = "external"

    class AliasesAliasProtoEnum(str, Enum):
        IPV4 = "IPv4"
        IPV6 = "IPv6"

    class AliasesAliasAuthtypeEnum(str, Enum):
        BASIC = "Basic"
        BEARER = "Bearer"
        HEADER = "Header"

    enabled: bool = Field(default=True)
    name: str = Field(default="")
    type: AliasesAliasTypeEnum = Field(default=AliasesAliasTypeEnum.HOST)
    path_expression: Optional[str] = None
    proto: List[AliasesAliasProtoEnum] = Field(default_factory=list)
    interface: Optional[str] = None
    counters: Optional[bool] = None
    updatefreq: Optional[str] = None
    """
    content encoding is with \n seperator for multiple items
    """
    content: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
    authtype: Optional[AliasesAliasAuthtypeEnum] = None
    expire: Optional[int] = None
    categories: List[str] = Field(default_factory=list)
    current_items: Optional[int] = None
    last_updated: Optional[str] = None
    eval_nomatch: Optional[int] = None
    eval_match: Optional[int] = None
    in_block_p: Optional[int] = None
    in_block_b: Optional[int] = None
    in_pass_p: Optional[int] = None
    in_pass_b: Optional[int] = None
    out_block_p: Optional[int] = None
    out_block_b: Optional[int] = None
    out_pass_p: Optional[int] = None
    out_pass_b: Optional[int] = None
    description: Optional[str] = None

