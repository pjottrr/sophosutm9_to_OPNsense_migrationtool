from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Acl(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Acl for OPNsense
    """

    class AclsAclActionEnum(str, Enum):
        ALLOW = "allow"
        DENY = "deny"
        REFUSE = "refuse"
        ALLOW_SNOOP = "allow_snoop"
        DENY_NON_LOCAL = "deny_non_local"
        REFUSE_NON_LOCAL = "refuse_non_local"
    
    enabled: bool = Field(default=True)
    name: Optional[str] = Field(default=None, description="An Access list name is required.")
    action: AclsAclActionEnum = Field(default=AclsAclActionEnum.ALLOW)
    networks: List[str] = Field(default_factory=list, description="Please specify a one or more valid network segment in CIDR notation (Ipv4/IPv6).")
    description: Optional[str] = None



class Acls(UIAwareMixin):
    """
    Generated model for Acls for OPNsense
    """

    class AclsAclsDefaultActionEnum(str, Enum):
        ALLOW = "allow"
        DENY = "deny"
        REFUSE = "refuse"
    
    default_action: AclsAclsDefaultActionEnum = Field(default=AclsAclsDefaultActionEnum.ALLOW)



class Advanced(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Advanced for OPNsense
    """

    class AdvancedAdvancedLogverbosityEnum(str, Enum):
        X0 = "0"
        X1 = "1"
        X2 = "2"
        X3 = "3"
        X4 = "4"
        X5 = "5"

    class AdvancedAdvancedValloglevelEnum(str, Enum):
        X0 = "0"
        X1 = "1"
        X2 = "2"
    
    hideidentity: Optional[bool] = None
    hideversion: Optional[bool] = None
    prefetch: Optional[bool] = None
    prefetchkey: Optional[bool] = None
    dnssecstripped: Optional[bool] = None
    aggressivensec: bool = Field(default=True)
    serveexpired: Optional[bool] = None
    serveexpiredreplyttl: Optional[int] = None
    serveexpiredttl: Optional[int] = None
    serveexpiredttlreset: Optional[bool] = None
    serveexpiredclienttimeout: Optional[int] = None
    qnameminstrict: Optional[bool] = None
    extendedstatistics: Optional[bool] = None
    logqueries: Optional[bool] = None
    logreplies: Optional[bool] = None
    logtagqueryreply: Optional[bool] = None
    logservfail: Optional[bool] = None
    loglocalactions: Optional[bool] = None
    logverbosity: AdvancedAdvancedLogverbosityEnum = Field(default=AdvancedAdvancedLogverbosityEnum.X1)
    valloglevel: AdvancedAdvancedValloglevelEnum = Field(default=AdvancedAdvancedValloglevelEnum.X0)
    privatedomain: List[str] = Field(default_factory=list)
    privateaddress: str = Field(default="0.0.0.0/8,10.0.0.0/8,100.64.0.0/10,169.254.0.0/16,172.16.0.0/12,192.0.2.0/24,192.168.0.0/16,198.18.0.0/15,198.51.100.0/24,203.0.113.0/24,233.252.0.0/24,::1/128,2001:db8::/32,fc00::/8,fd00::/8,fe80::/10")
    insecuredomain: List[str] = Field(default_factory=list)
    msgcachesize: Optional[str] = Field(default=None, pattern=r"[0-9]+[kmg]?", description="The cache size should be numeric, optionally appended with 'k', 'm', or 'g'.")
    rrsetcachesize: Optional[str] = Field(default=None, pattern=r"[0-9]+[kmg]?", description="The cache size should be numeric, optionally appended with 'k', 'm', or 'g'.")
    outgoingnumtcp: Optional[int] = None
    incomingnumtcp: Optional[int] = None
    numqueriesperthread: Optional[int] = None
    outgoingrange: Optional[int] = None
    jostletimeout: Optional[int] = None
    discardtimeout: Optional[int] = None
    cachemaxttl: Optional[int] = None
    cachemaxnegativettl: Optional[int] = None
    cacheminttl: Optional[int] = None
    infrahostttl: Optional[int] = None
    infrakeepprobing: Optional[bool] = None
    infracachenumhosts: Optional[int] = None
    unwantedreplythreshold: Optional[int] = None



class Alias(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Alias for OPNsense
    """

    enabled: bool = Field(default=True)
    host: Optional[str] = None
    hostname: Optional[str] = None
    domain: Optional[str] = Field(default=None, pattern=r"^(?:(?:[a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*(?:[a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$", description="A valid domain must be specified.")
    description: Optional[str] = None



class Blocklist(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Blocklist for OPNsense
    """

    class DnsblBlocklistTypeEnum(str, Enum):
        ATF = "atf"
        AG = "ag"
        EL = "el"
        EP = "ep"
        HGZ001 = "hgz001"
        HGZ002 = "hgz002"
        HGZ003 = "hgz003"
        HGZ004 = "hgz004"
        HGZ005 = "hgz005"
        HGZ006 = "hgz006"
        HGZ007 = "hgz007"
        HGZ008 = "hgz008"
        HGZ009 = "hgz009"
        HGZ010 = "hgz010"
        HGZ011 = "hgz011"
        HGZ012 = "hgz012"
        HGZ013 = "hgz013"
        HGZ014 = "hgz014"
        HGZ015 = "hgz015"
        HGZ016 = "hgz016"
        HGZ017 = "hgz017"
        HGZ018 = "hgz018"
        HGZ019 = "hgz019"
        HGZ020 = "hgz020"
        HGZ021 = "hgz021"
        OISD0 = "oisd0"
        OISD1 = "oisd1"
        OISD2 = "oisd2"
        SB = "sb"
        YY = "yy"
    
    enabled: bool = Field(default=True)
    type: List[DnsblBlocklistTypeEnum] = Field(default_factory=list)
    lists: List[str] = Field(default_factory=list)
    allowlists: List[str] = Field(default_factory=list)
    blocklists: List[str] = Field(default_factory=list)
    wildcards: List[str] = Field(default_factory=list, description="A valid domain must be specified.")
    source_nets: List[str] = Field(default_factory=list, description="Please specify a valid network segment or address (IPv4/IPv6). If a mask is provided, please omit the host bits.")
    address: Optional[str] = None
    nxdomain: Optional[bool] = None
    cache_ttl: int = Field(default=72000)
    description: Optional[str] = Field(default=None, description="To keep track of which policies are applicable to source networks, a description should be provided. It should be a string between 1 and 255 characters.")



class Dot(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Dot for OPNsense
    """

    class DotsDotTypeEnum(str, Enum):
        DOT = "dot"
        FORWARD = "forward"
    
    enabled: bool = Field(default=True)
    type: DotsDotTypeEnum = Field(default=DotsDotTypeEnum.DOT)
    domain: Optional[str] = Field(default=None, description="A valid domain must be specified.")
    server: Optional[str] = None
    port: Optional[int] = None
    verify: Optional[str] = None
    forward_tcp_upstream: bool = Field(default=False)
    forward_first: bool = Field(default=False)
    description: Optional[str] = None



class Forwarding(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Forwarding for OPNsense
    """
    
    enabled: Optional[bool] = None



class General(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for General for OPNsense
    """

    class GeneralGeneralLocalZoneTypeEnum(str, Enum):
        TRANSPARENT = "transparent"
        ALWAYS_NXDOMAIN = "always_nxdomain"
        ALWAYS_REFUSE = "always_refuse"
        ALWAYS_TRANSPARENT = "always_transparent"
        DENY = "deny"
        INFORM = "inform"
        INFORM_DENY = "inform_deny"
        NODEFAULT = "nodefault"
        REFUSE = "refuse"
        STATIC = "static"
        TYPETRANSPARENT = "typetransparent"
    
    enabled: bool = Field(default=False)
    port: int = Field(default=53)
    stats: Optional[bool] = None
    dnssec: Optional[bool] = None
    dns64: Optional[bool] = None
    dns64prefix: Optional[str] = None
    noarecords: Optional[bool] = None
    regdhcp: Optional[bool] = None
    regdhcpdomain: Optional[str] = Field(default=None, pattern=r"^(?:(?:[a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*(?:[a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$", description="A valid domain must be specified.")
    regdhcpstatic: Optional[bool] = None
    noreglladdr6: Optional[bool] = None
    noregrecords: Optional[bool] = None
    txtsupport: Optional[bool] = None
    cacheflush: Optional[bool] = None
    safesearch: Optional[bool] = None
    local_zone_type: GeneralGeneralLocalZoneTypeEnum = Field(default=GeneralGeneralLocalZoneTypeEnum.TRANSPARENT)
    enable_wpad: Optional[bool] = None



class Host(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Host for OPNsense
    """

    class HostsHostRrEnum(str, Enum):
        A = "A"
        AAAA = "AAAA"
        MX = "MX"
        TXT = "TXT"
    
    enabled: bool = Field(default=True)
    hostname: Optional[str] = None
    domain: Optional[str] = Field(default=None, pattern=r"^(?:(?:[a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*(?:[a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$", description="A valid domain must be specified.")
    rr: HostsHostRrEnum = Field(default=HostsHostRrEnum.A)
    mxprio: Optional[int] = None
    mx: Optional[str] = None
    ttl: Optional[int] = Field(default=None, ge=0, le=2147483647)
    server: Optional[str] = None
    txtdata: Optional[str] = None
    aliascount: Optional[str] = None
    description: Optional[str] = None


class UnboundSettings(UIAwareMixin):
    """
    Wrapper model for all Unbound settings.
    Used by unbound_get() and unbound_set() methods.
    """
    general: Optional[General] = None
    advanced: Optional[Advanced] = None
    acls: Optional[Acls] = None
    forwarding: Optional[Forwarding] = None

    @classmethod
    def from_ui_dict(cls, data: Dict[str, Any]) -> 'UnboundSettings':
        """Parse UnboundSettings from API response"""
        # Handle wrapped response: {"unbound": {...}}
        if 'unbound' in data:
            data = data['unbound']

        result = {}
        if 'general' in data:
            result['general'] = General.from_ui_dict({'general': data['general']})
        if 'advanced' in data:
            result['advanced'] = Advanced.from_ui_dict({'advanced': data['advanced']})
        if 'acls' in data:
            result['acls'] = Acls.from_ui_dict({'acls': data['acls']})
        if 'forwarding' in data:
            result['forwarding'] = Forwarding.from_ui_dict({'forwarding': data['forwarding']})

        return cls(**result)

    def to_simple_dict(self, exclude_field_names=None) -> Dict[str, Any]:
        """Serialize to API format"""
        result = {}
        if self.general is not None:
            general_dict = self.general.to_simple_dict(exclude_field_names)
            result['general'] = general_dict.get('general', general_dict)
        if self.advanced is not None:
            advanced_dict = self.advanced.to_simple_dict(exclude_field_names)
            result['advanced'] = advanced_dict.get('advanced', advanced_dict)
        if self.acls is not None:
            acls_dict = self.acls.to_simple_dict(exclude_field_names)
            result['acls'] = acls_dict.get('acls', acls_dict)
        if self.forwarding is not None:
            forwarding_dict = self.forwarding.to_simple_dict(exclude_field_names)
            result['forwarding'] = forwarding_dict.get('forwarding', forwarding_dict)
        return {'unbound': result}

