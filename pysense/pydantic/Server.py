from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Server(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Server for OPNsense (HAProxy)
    """

    class ServersServerModeEnum(str, Enum):
        ACTIVE = "active"
        BACKUP = "backup"
        DISABLED = "disabled"

    class ServersServerMultiplexerProtocolEnum(str, Enum):
        UNSPECIFIED = "unspecified"
        FCGI = "fcgi"
        H2 = "h2"
        H1 = "h1"

    class ServersServerTypeEnum(str, Enum):
        STATIC = "static"
        TEMPLATE = "template"
        UNIX = "unix"

    class ServersServerResolveroptsEnum(str, Enum):
        ALLOW_DUP_IP = "allow-dup-ip"
        IGNORE_WEIGHT = "ignore-weight"
        PREVENT_DUP_IP = "prevent-dup-ip"

    class ServersServerResolvepreferEnum(str, Enum):
        IPV4 = "ipv4"
        IPV6 = "ipv6"

    id: str = Field(default='')
    enabled: bool = Field(default=True)
    name: str = Field(..., pattern=r"([0-9a-zA-Z._\-]){1,255}", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = None
    address: Optional[str] = None
    port: Optional[int] = None
    checkport: Optional[int] = None
    mode: ServersServerModeEnum = "active"
    multiplexer_protocol: ServersServerMultiplexerProtocolEnum = "unspecified"
    type: ServersServerTypeEnum = Field(default=ServersServerTypeEnum.STATIC)
    serviceName: Optional[str] = None
    number: Optional[str] = None
    linkedResolver: Optional[str] = None
    resolverOpts: List[ServersServerResolveroptsEnum] = Field(default_factory=list)
    resolvePrefer: Optional[ServersServerResolvepreferEnum] = None
    ssl: bool = Field(default=False)
    sslSNI: Optional[str] = None
    sslVerify: bool = Field(default=True)
    sslCA: List[str] = Field(default_factory=list)
    sslCRL: Optional[str] = None
    sslClientCertificate: Optional[str] = None
    maxConnections: Optional[int] = None
    weight: Optional[int] = None
    checkInterval: Optional[str] = None
    checkDownInterval: Optional[str] = None
    source: Optional[str] = None
    advanced: Optional[str] = None
    unix_socket: Optional[str] = None

