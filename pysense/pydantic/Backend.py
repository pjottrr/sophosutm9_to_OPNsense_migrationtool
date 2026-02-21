from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin


class Backend(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Backend for plugin HAProxy
    """
    class BackendsBackendAlgorithmEnum(str, Enum):
        SOURCE = "source"
        ROUNDROBIN = "roundrobin"
        STATIC_RR = "static-rr"
        LEASTCONN = "leastconn"
        URI = "uri"
        RANDOM = "random"

    class BackendsBackendModeEnum(str, Enum):
        HTTP = "http"
        TCP = "tcp"

    class BackendsBackendPersistenceCookiemodeEnum(str, Enum):
        PIGGYBACK = "piggyback"
        NEW = "new"

    class BackendsBackendPersistenceEnum(str, Enum):
        STICKTABLE = "sticktable"
        COOKIE = "cookie"

    class BackendsBackendTuningHttpreuseEnum(str, Enum):
        NEVER = "never"
        SAFE = "safe"
        AGGRESSIVE = "aggressive"
        ALWAYS = "always"

    class BackendsBackendStickinessPatternEnum(str, Enum):
        SOURCEIPV4 = "sourceipv4"
        SOURCEIPV6 = "sourceipv6"
        COOKIEVALUE = "cookievalue"
        RDPCOOKIE = "rdpcookie"

    class BackendsBackendBaAdvertisedProtocolsEnum(str, Enum):
        H2 = "h2"
        HTTP11 = "http11"
        HTTP10 = "http10"

    class BackendsBackendForwardedheaderparametersEnum(str, Enum):
        PROTO = "proto"
        HOST = "host"
        BY = "by"
        BY_PORT = "by_port"
        FOR = "for"
        FOR_PORT = "for_port"

    class BackendsBackendResolveroptsEnum(str, Enum):
        ALLOW_DUP_IP = "allow-dup-ip"
        IGNORE_WEIGHT = "ignore-weight"
        PREVENT_DUP_IP = "prevent-dup-ip"

    class BackendsBackendResolvepreferEnum(str, Enum):
        IPV4 = "ipv4"
        IPV6 = "ipv6"

    class BackendsBackendProxyprotocolEnum(str, Enum):
        V1 = "v1"
        V2 = "v2"

    class BackendsBackendStickinessDatatypesEnum(str, Enum):
        CONN_CNT = "conn_cnt"
        CONN_CUR = "conn_cur"
        CONN_RATE = "conn_rate"
        SESS_CNT = "sess_cnt"
        SESS_RATE = "sess_rate"
        HTTP_REQ_CNT = "http_req_cnt"
        HTTP_REQ_RATE = "http_req_rate"
        HTTP_ERR_CNT = "http_err_cnt"
        HTTP_ERR_RATE = "http_err_rate"
        BYTES_IN_CNT = "bytes_in_cnt"
        BYTES_IN_RATE = "bytes_in_rate"
        BYTES_OUT_CNT = "bytes_out_cnt"
        BYTES_OUT_RATE = "bytes_out_rate"

    id: Optional[str] = None
    enabled: bool = Field(default=True, description="Enable or disable this backend.")
    name: str = Field(..., pattern=r"([0-9a-zA-Z._\-]){1,255}")
    description: Optional[str] = None
    mode: BackendsBackendModeEnum = BackendsBackendModeEnum.HTTP
    algorithm: BackendsBackendAlgorithmEnum = BackendsBackendAlgorithmEnum.SOURCE
    random_draws: int = Field(default=2, ge=2, le=1000)
    proxyProtocol: BackendsBackendProxyprotocolEnum = Field(default_factory=list)
    linkedServers: List[str] = Field(default_factory=list)
    linkedFcgi: Optional[str] = None
    linkedResolver: Optional[str] = None
    resolverOpts: List[BackendsBackendResolveroptsEnum] = Field(default_factory=list)
    resolvePrefer: BackendsBackendResolvepreferEnum = Field(default_factory=list)
    source: Optional[str] = None
    healthCheckEnabled: bool = Field(default=True)
    healthCheck: Optional[str] = None
    healthCheckLogStatus: bool = False
    checkInterval: Optional[str] = None
    checkDownInterval: Optional[str] = None
    healthCheckFall: Optional[int] = None
    healthCheckRise: Optional[int] = None
    linkedMailer: Optional[str] = None
    http2Enabled: bool = True
    http2Enabled_nontls: bool = False
    ba_advertised_protocols: List[BackendsBackendBaAdvertisedProtocolsEnum] = Field(default_factory=list)
    forwardFor: bool = False
    forwardedHeader: bool = False
    forwardedHeaderParameters: List[BackendsBackendForwardedheaderparametersEnum] = None
    persistence: BackendsBackendPersistenceEnum = BackendsBackendPersistenceEnum.STICKTABLE
    persistence_cookiemode: BackendsBackendPersistenceCookiemodeEnum = Field(default=BackendsBackendPersistenceCookiemodeEnum.PIGGYBACK)
    persistence_cookiename: str = Field(default="SRVCOOKIE")
    persistence_stripquotes: bool = Field(default=True)
    stickiness_pattern: BackendsBackendStickinessPatternEnum = Field(default="sourceipv4")
    stickiness_dataTypes: List[BackendsBackendStickinessDatatypesEnum] = None
    stickiness_expire: str = Field(default='30m')
    stickiness_size: str = Field(default='50k')
    stickiness_cookiename: Optional[str] = None
    stickiness_cookielength: Optional[int] = None
    stickiness_connRatePeriod: str = Field(default="10s")
    stickiness_sessRatePeriod: str = Field(default="10s")
    stickiness_httpReqRatePeriod: str = Field(default="10s")
    stickiness_httpErrRatePeriod: str = Field(default="10s")
    stickiness_bytesInRatePeriod: str = Field(default="1m")
    stickiness_bytesOutRatePeriod: str = Field(default="1m")
    basicAuthEnabled: bool = False
    basicAuthUsers: List[str] = Field(default_factory=list)
    basicAuthGroups: List[str] = Field(default_factory=list)
    tuning_timeoutConnect: Optional[str] = None
    tuning_timeoutCheck: Optional[str] = None
    tuning_timeoutServer: Optional[str] = None
    tuning_retries: Optional[int] = None
    customOptions: Optional[str] = None
    tuning_defaultserver: Optional[str] = None
    tuning_noport: bool = Field(default=False)
    tuning_httpreuse: BackendsBackendTuningHttpreuseEnum = Field(default="safe")
    tuning_caching: bool = False
    linkedActions: List[str] = Field(default_factory=list)
    linkedErrorfiles: List[str] = Field(default_factory=list)
