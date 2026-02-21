from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin


class Frontend(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Frontend for plugin HAProxy
    """
    class FrontendsFrontendModeEnum(str, Enum):
        HTTP = "http"
        SSL = "ssl"
        TCP = "tcp"

    class FrontendsFrontendSslBindoptionsEnum(str, Enum):
        NO_SSLV3 = "no-sslv3"
        NO_TLSV10 = "no-tlsv10"
        NO_TLSV11 = "no-tlsv11"
        NO_TLSV12 = "no-tlsv12"
        NO_TLSV13 = "no-tlsv13"
        NO_TLS_TICKETS = "no-tls-tickets"
        FORCE_SSLV3 = "force-sslv3"
        FORCE_TLSV10 = "force-tlsv10"
        FORCE_TLSV11 = "force-tlsv11"
        FORCE_TLSV12 = "force-tlsv12"
        FORCE_TLSV13 = "force-tlsv13"
        PREFER_CLIENT_CIPHERS = "prefer-client-ciphers"
        STRICT_SNI = "strict-sni"

    class FrontendsFrontendSslMinversionEnum(str, Enum):
        SSLV3 = "SSLv3"
        TLSV1_0 = "TLSv1.0"
        TLSV1_1 = "TLSv1.1"
        TLSV1_2 = "TLSv1.2"
        TLSV1_3 = "TLSv1.3"

    class FrontendsFrontendSslMaxversionEnum(str, Enum):
        SSLV3 = "SSLv3"
        TLSV1_0 = "TLSv1.0"
        TLSV1_1 = "TLSv1.1"
        TLSV1_2 = "TLSv1.2"
        TLSV1_3 = "TLSv1.3"

    class FrontendsFrontendSslClientauthverifyEnum(str, Enum):
        NONE = "none"
        OPTIONAL = "optional"
        REQUIRED = "required"

    class FrontendsFrontendStickinessPatternEnum(str, Enum):
        IPV4 = "ipv4"
        IPV6 = "ipv6"
        INTEGER = "integer"
        STRING = "string"
        BINARY = "binary"

    class FrontendsFrontendStickinessDatatypesEnum(str, Enum):
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

    class FrontendsFrontendAdvertisedProtocolsEnum(str, Enum):
        H2 = "h2"
        HTTP11 = "http11"
        HTTP10 = "http10"

    class FrontendsFrontendConnectionbehaviourEnum(str, Enum):
        HTTP_KEEP_ALIVE = "http-keep-alive"
        HTTPCLOSE = "httpclose"
        HTTP_SERVER_CLOSE = "http-server-close"

    id: Optional[str] = None
    enabled: bool = Field(default=True)
    name: str = Field(..., pattern=r"^([0-9a-zA-Z._\-]){1,255}$", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = Field(default=None, pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    bind: List[str] = Field(..., description="Please provide a valid listen address, i.e. 127.0.0.1:8080, [::1]:8080, www.example.com:443 or unix@socket-name. Port range as start-end, i.e. 127.0.0.1:1220-1240.")
    bindOptions: Optional[str] = None
    mode: FrontendsFrontendModeEnum = Field(default=FrontendsFrontendModeEnum.HTTP)
    defaultBackend: Optional[str] = Field(default=None, description="Related backend item not found")
    ssl_enabled: bool = Field(default=False)
    ssl_certificates: List[str] = Field(default_factory=list, description="Please select a valid certificate from the list.")
    ssl_default_certificate: Optional[str] = Field(default=None, description="Please select a valid certificate from the list.")
    ssl_customOptions: Optional[str] = None
    ssl_advancedEnabled: bool = Field(default=False)
    ssl_bindOptions: List[FrontendsFrontendSslBindoptionsEnum] = Field(default=[FrontendsFrontendSslBindoptionsEnum.PREFER_CLIENT_CIPHERS])
    ssl_minVersion: FrontendsFrontendSslMinversionEnum = Field(default=FrontendsFrontendSslMinversionEnum.TLSV1_2)
    ssl_maxVersion: Optional[FrontendsFrontendSslMaxversionEnum] = None
    ssl_cipherList: str = Field(default="ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256")
    ssl_cipherSuites: str = Field(default="TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256")
    ssl_hstsEnabled: bool = Field(default=True)
    ssl_hstsIncludeSubDomains: bool = Field(default=False)
    ssl_hstsPreload: bool = Field(default=False)
    ssl_hstsMaxAge: int = Field(default=15768000, ge=1, le=1000000000, description="Please specify a value between 1 and 1000000000.")
    ssl_clientAuthEnabled: bool = Field(default=False)
    ssl_clientAuthVerify: FrontendsFrontendSslClientauthverifyEnum = Field(default=FrontendsFrontendSslClientauthverifyEnum.NONE)
    ssl_clientAuthCAs: List[str] = Field(default_factory=list, description="Please select a valid CA from the list.")
    ssl_clientAuthCRLs: List[str] = Field(default_factory=list, description="Please select a valid CA from the list.")
    basicAuthEnabled: bool = Field(default=False)
    basicAuthUsers: List[str] = Field(default_factory=list, description="Related user not found")
    basicAuthGroups: List[str] = Field(default_factory=list, description="Related group not found")
    tuning_maxConnections: Optional[int] = Field(default=None, ge=0, le=10000000, description="Please specify a value between 0 and 10000000.")
    tuning_timeoutClient: Optional[str] = Field(default=None, pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    tuning_timeoutHttpReq: Optional[str] = Field(default=None, pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    tuning_timeoutHttpKeepAlive: Optional[str] = Field(default=None, pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    linkedCpuAffinityRules: List[str] = Field(default_factory=list, description="Related CPU affinity rule not found")
    tuning_shards: Optional[int] = Field(default=None, ge=2, le=1000, description="Please specify a value between 2 and 1000.")
    logging_dontLogNull: bool = Field(default=False)
    logging_dontLogNormal: bool = Field(default=False)
    logging_logSeparateErrors: bool = Field(default=False)
    logging_detailedLog: bool = Field(default=False)
    logging_socketStats: bool = Field(default=False)
    stickiness_pattern: Optional[FrontendsFrontendStickinessPatternEnum] = None
    stickiness_dataTypes: List[FrontendsFrontendStickinessDatatypesEnum] = Field(default_factory=list)
    stickiness_expire: str = Field(default="30m", pattern=r"^([0-9]{1,5}(?:ms|s|m|h|d)?)", description="Should be a number between 1 and 5 characters followed by either \"d\", \"h\", \"m\", \"s\" or \"ms\".")
    stickiness_size: str = Field(default="50k", pattern=r"^([0-9]{1,5}[k|m|g]{1})*", description="Should be a number between 1 and 5 characters followed by either \"k\", \"m\" or \"g\".")
    stickiness_counter: bool = Field(default=True)
    stickiness_counter_key: str = Field(default="src", pattern=r"^([0-9a-zA-Z._]){1,32}$", description="Should be a string between 1 and 32 characters.")
    stickiness_length: Optional[int] = Field(default=None, ge=1, le=16384, description="Please specify a value between 1 and 16384.")
    stickiness_connRatePeriod: str = Field(default="10s", pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    stickiness_sessRatePeriod: str = Field(default="10s", pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    stickiness_httpReqRatePeriod: str = Field(default="10s", pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    stickiness_httpErrRatePeriod: str = Field(default="10s", pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    stickiness_bytesInRatePeriod: str = Field(default="1m", pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    stickiness_bytesOutRatePeriod: str = Field(default="1m", pattern=r"^([0-9]{1,8}(?:us|ms|s|m|h|d)?)", description="Should be a number between 1 and 8 characters, optionally followed by either \"d\", \"h\", \"m\", \"s\", \"ms\" or \"us\".")
    http2Enabled: bool = Field(default=True)
    http2Enabled_nontls: bool = Field(default=False)
    advertised_protocols: List[FrontendsFrontendAdvertisedProtocolsEnum] = Field(default=[FrontendsFrontendAdvertisedProtocolsEnum.H2,FrontendsFrontendAdvertisedProtocolsEnum.HTTP11])
    prometheus_enabled: bool = Field(default=False)
    prometheus_path: str = Field(default="/metrics", pattern=r"^.{1,2048}$", description="Should be a string between 1 and 2048 characters.")
    connectionBehaviour: FrontendsFrontendConnectionbehaviourEnum = Field(default=FrontendsFrontendConnectionbehaviourEnum.HTTP_KEEP_ALIVE)
    customOptions: Optional[str] = None
    linkedActions: List[str] = Field(default_factory=list, description="Related action item not found")
    linkedErrorfiles: List[str] = Field(default_factory=list, description="Related error file item not found")

    def get_port(self):
        return self.bind[0].split(':')[-1]