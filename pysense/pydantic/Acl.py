from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Acl(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Acl for plugin HAProxy
    """

    class AclsAclExpressionEnum(str, Enum):
        HTTP_AUTH = "http_auth"
        HDR_BEG = "hdr_beg"
        HDR_END = "hdr_end"
        HDR = "hdr"
        HDR_REG = "hdr_reg"
        HDR_SUB = "hdr_sub"
        PATH_BEG = "path_beg"
        PATH_END = "path_end"
        PATH = "path"
        PATH_REG = "path_reg"
        PATH_DIR = "path_dir"
        PATH_SUB = "path_sub"
        CUST_HDR_BEG = "cust_hdr_beg"
        CUST_HDR_END = "cust_hdr_end"
        CUST_HDR = "cust_hdr"
        CUST_HDR_REG = "cust_hdr_reg"
        CUST_HDR_SUB = "cust_hdr_sub"
        URL_PARAM = "url_param"
        SSL_C_VERIFY = "ssl_c_verify"
        SSL_C_VERIFY_CODE = "ssl_c_verify_code"
        SSL_C_CA_COMMONNAME = "ssl_c_ca_commonname"
        SSL_HELLO_TYPE = "ssl_hello_type"
        SRC = "src"
        SRC_IS_LOCAL = "src_is_local"
        SRC_PORT = "src_port"
        SRC_BYTES_IN_RATE = "src_bytes_in_rate"
        SRC_BYTES_OUT_RATE = "src_bytes_out_rate"
        SRC_KBYTES_IN = "src_kbytes_in"
        SRC_KBYTES_OUT = "src_kbytes_out"
        SRC_CONN_CNT = "src_conn_cnt"
        SRC_CONN_CUR = "src_conn_cur"
        SRC_CONN_RATE = "src_conn_rate"
        SRC_HTTP_ERR_CNT = "src_http_err_cnt"
        SRC_HTTP_ERR_RATE = "src_http_err_rate"
        SRC_HTTP_REQ_CNT = "src_http_req_cnt"
        SRC_HTTP_REQ_RATE = "src_http_req_rate"
        SRC_SESS_CNT = "src_sess_cnt"
        SRC_SESS_RATE = "src_sess_rate"
        NBSRV = "nbsrv"
        TRAFFIC_IS_HTTP = "traffic_is_http"
        TRAFFIC_IS_SSL = "traffic_is_ssl"
        SSL_FC = "ssl_fc"
        SSL_FC_SNI = "ssl_fc_sni"
        SSL_SNI = "ssl_sni"
        SSL_SNI_SUB = "ssl_sni_sub"
        SSL_SNI_BEG = "ssl_sni_beg"
        SSL_SNI_END = "ssl_sni_end"
        SSL_SNI_REG = "ssl_sni_reg"
        CUSTOM_ACL = "custom_acl"

    class AclsAclSslHelloTypeEnum(str, Enum):
        X0 = "x0"
        X1 = "x1"
        X2 = "x2"

    class AclsAclSrcBytesInRateComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcBytesOutRateComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcConnCntComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcConnCurComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcConnRateComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcHttpErrCntComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcHttpErrRateComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcHttpReqCntComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcHttpReqRateComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcKbytesInComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcKbytesOutComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcPortComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcSessCntComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    class AclsAclSrcSessRateComparisonEnum(str, Enum):
        GT = "gt"
        GE = "ge"
        EQ = "eq"
        LT = "lt"
        LE = "le"

    id: Optional[str] = None
    name: str = Field(..., pattern=r"[^\t^,^;^\.^\[^\]^\{^\}]{1,255}", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = None
    expression: AclsAclExpressionEnum = Field(...)
    negate: bool = Field(default=False, description="Negate the result of the expression.")
    caseSensitive: bool = False
    hdr_beg: Optional[str] = None
    hdr_end: Optional[str] = None
    hdr: Optional[str] = None
    hdr_reg: Optional[str] = None
    hdr_sub: Optional[str] = None
    path_beg: Optional[str] = None
    path_end: Optional[str] = None
    path: Optional[str] = None
    path_reg: Optional[str] = None
    path_dir: Optional[str] = None
    path_sub: Optional[str] = None
    cust_hdr_beg_name: Optional[str] = None
    cust_hdr_beg: Optional[str] = None
    cust_hdr_end_name: Optional[str] = None
    cust_hdr_end: Optional[str] = None
    cust_hdr_name: Optional[str] = None
    cust_hdr: Optional[str] = None
    cust_hdr_reg_name: Optional[str] = None
    cust_hdr_reg: Optional[str] = None
    cust_hdr_sub_name: Optional[str] = None
    cust_hdr_sub: Optional[str] = None
    url_param: Optional[str] = None
    url_param_value: Optional[str] = None
    ssl_c_verify_code: Optional[int] = None
    ssl_c_ca_commonname: Optional[str] = None
    ssl_hello_type: AclsAclSslHelloTypeEnum = "x1"
    src: Optional[str] = None
    src_bytes_in_rate_comparison: AclsAclSrcBytesInRateComparisonEnum = "gt"
    src_bytes_in_rate: Optional[int] = None
    src_bytes_out_rate_comparison: AclsAclSrcBytesOutRateComparisonEnum = "gt"
    src_bytes_out_rate: Optional[int] = None
    src_conn_cnt_comparison: AclsAclSrcConnCntComparisonEnum = "gt"
    src_conn_cnt: Optional[int] = None
    src_conn_cur_comparison: AclsAclSrcConnCurComparisonEnum = "gt"
    src_conn_cur: Optional[int] = None
    src_conn_rate_comparison: AclsAclSrcConnRateComparisonEnum = "gt"
    src_conn_rate: Optional[int] = None
    src_http_err_cnt_comparison: AclsAclSrcHttpErrCntComparisonEnum = "gt"
    src_http_err_cnt: Optional[int] = None
    src_http_err_rate_comparison: AclsAclSrcHttpErrRateComparisonEnum = "gt"
    src_http_err_rate: Optional[int] = None
    src_http_req_cnt_comparison: AclsAclSrcHttpReqCntComparisonEnum = "gt"
    src_http_req_cnt: Optional[int] = None
    src_http_req_rate_comparison: AclsAclSrcHttpReqRateComparisonEnum = "gt"
    src_http_req_rate: Optional[int] = None
    src_kbytes_in_comparison: AclsAclSrcKbytesInComparisonEnum = "gt"
    src_kbytes_in: Optional[int] = None
    src_kbytes_out_comparison: AclsAclSrcKbytesOutComparisonEnum = "gt"
    src_kbytes_out: Optional[int] = None
    src_port_comparison: AclsAclSrcPortComparisonEnum = "gt"
    src_port: Optional[int] = None
    src_sess_cnt_comparison: AclsAclSrcSessCntComparisonEnum = "gt"
    src_sess_cnt: Optional[int] = None
    src_sess_rate_comparison: AclsAclSrcSessRateComparisonEnum = "gt"
    src_sess_rate: Optional[int] = None
    nbsrv: Optional[int] = None
    nbsrv_backend: Optional[str] = None
    ssl_fc_sni: Optional[str] = None
    ssl_sni: Optional[str] = None
    ssl_sni_sub: Optional[str] = None
    ssl_sni_beg: Optional[str] = None
    ssl_sni_end: Optional[str] = None
    ssl_sni_reg: Optional[str] = None
    custom_acl: Optional[str] = None
    urlparam: Optional[str] = None
    queryBackend: Optional[str] = None
    allowedUsers: List[str] = Field(default_factory=list)
    allowedGroups: List[str] = Field(default_factory=list)