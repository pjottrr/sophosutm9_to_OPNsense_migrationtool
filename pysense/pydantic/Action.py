from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Action(UIAwareMixin):
    """
    Generated model for Action for plugin HAProxy
    """

    class ActionsActionTesttypeEnum(str, Enum):
        IF = "if"
        UNLESS = "unless"

    class ActionsActionOperatorEnum(str, Enum):
        AND = "and"
        OR = "or"

    class ActionsActionTypeEnum(str, Enum):
        USE_BACKEND = "use_backend"
        USE_SERVER = "use_server"
        MAP_USE_BACKEND = "map_use_backend"
        FCGI_PASS_HEADER = "fcgi_pass_header"
        FCGI_SET_PARAM = "fcgi_set_param"
        HTTP_REQUEST_ALLOW = "http-request_allow"
        HTTP_REQUEST_DENY = "http-request_deny"
        HTTP_REQUEST_TARPIT = "http-request_tarpit"
        HTTP_REQUEST_AUTH = "http-request_auth"
        HTTP_REQUEST_REDIRECT = "http-request_redirect"
        HTTP_REQUEST_LUA = "http-request_lua"
        HTTP_REQUEST_USE_SERVICE = "http-request_use-service"
        HTTP_REQUEST_ADD_HEADER = "http-request_add-header"
        HTTP_REQUEST_SET_HEADER = "http-request_set-header"
        HTTP_REQUEST_DEL_HEADER = "http-request_del-header"
        HTTP_REQUEST_REPLACE_HEADER = "http-request_replace-header"
        HTTP_REQUEST_REPLACE_VALUE = "http-request_replace-value"
        HTTP_REQUEST_SET_PATH = "http-request_set-path"
        HTTP_REQUEST_SET_VAR = "http-request_set-var"
        HTTP_RESPONSE_ALLOW = "http-response_allow"
        HTTP_RESPONSE_DENY = "http-response_deny"
        HTTP_RESPONSE_LUA = "http-response_lua"
        HTTP_RESPONSE_ADD_HEADER = "http-response_add-header"
        HTTP_RESPONSE_SET_HEADER = "http-response_set-header"
        HTTP_RESPONSE_DEL_HEADER = "http-response_del-header"
        HTTP_RESPONSE_REPLACE_HEADER = "http-response_replace-header"
        HTTP_RESPONSE_REPLACE_VALUE = "http-response_replace-value"
        HTTP_RESPONSE_SET_STATUS = "http-response_set-status"
        HTTP_RESPONSE_SET_VAR = "http-response_set-var"
        MONITOR_FAIL = "monitor_fail"
        TCP_REQUEST_CONNECTION_ACCEPT = "tcp-request_connection_accept"
        TCP_REQUEST_CONNECTION_REJECT = "tcp-request_connection_reject"
        TCP_REQUEST_CONTENT_ACCEPT = "tcp-request_content_accept"
        TCP_REQUEST_CONTENT_REJECT = "tcp-request_content_reject"
        TCP_REQUEST_CONTENT_LUA = "tcp-request_content_lua"
        TCP_REQUEST_CONTENT_USE_SERVICE = "tcp-request_content_use-service"
        TCP_REQUEST_INSPECT_DELAY = "tcp-request_inspect-delay"
        TCP_RESPONSE_CONTENT_ACCEPT = "tcp-response_content_accept"
        TCP_RESPONSE_CONTENT_CLOSE = "tcp-response_content_close"
        TCP_RESPONSE_CONTENT_REJECT = "tcp-response_content_reject"
        TCP_RESPONSE_CONTENT_LUA = "tcp-response_content_lua"
        TCP_RESPONSE_INSPECT_DELAY = "tcp-response_inspect-delay"
        CUSTOM = "custom"

    class ActionsActionHttpRequestSetVarScopeEnum(str, Enum):
        PROC = "proc"
        SESS = "sess"
        TXN = "txn"
        REQ = "req"
        RES = "res"

    class ActionsActionHttpResponseSetVarScopeEnum(str, Enum):
        PROC = "proc"
        SESS = "sess"
        TXN = "txn"
        REQ = "req"
        RES = "res"

    name: str = Field(..., pattern=r"^[^\t^,^;^\.^\[^\]^\{^\}]{1,255}$", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = Field(default=None, pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    testType: ActionsActionTesttypeEnum = Field(default=ActionsActionTesttypeEnum.IF)
    linkedAcls: List[str|UUID] = Field(default_factory=list, description="Related ACL item not found")
    operator: Optional[ActionsActionOperatorEnum] = Field(default=ActionsActionOperatorEnum.AND)
    type: ActionsActionTypeEnum = Field(...)
    use_backend: Optional[str|UUID] = Field(default=None, description="Related backend item not found")
    use_server: Optional[str|UUID] = Field(default=None, description="Related server item not found")
    fcgi_pass_header: Optional[str] = Field(default=None, pattern=r"^.{1,1024}$", description="Should be a string between 1 and 1024 characters.")
    fcgi_set_param: Optional[str] = Field(default=None, pattern=r"^.{1,1024}$", description="Should be a string between 1 and 1024 characters.")
    http_request_auth: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_redirect: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_lua: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_use_service: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_add_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_add_header_content: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_set_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_set_header_content: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_del_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_replace_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_replace_header_regex: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_replace_value_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_replace_value_regex: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_set_path: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_set_var_scope: ActionsActionHttpRequestSetVarScopeEnum = Field(default=ActionsActionHttpRequestSetVarScopeEnum.TXN)
    http_request_set_var_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_request_set_var_expr: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_lua: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_add_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_add_header_content: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_set_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_set_header_content: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_del_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_replace_header_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_replace_header_regex: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_replace_value_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_replace_value_regex: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_set_status_code: Optional[int] = Field(default=None, ge=100, le=999, description="Please specify a value between 100 and 999.")
    http_response_set_status_reason: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_set_var_scope: ActionsActionHttpResponseSetVarScopeEnum = Field(default=ActionsActionHttpResponseSetVarScopeEnum.TXN)
    http_response_set_var_name: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    http_response_set_var_expr: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    monitor_fail_uri: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    tcp_request_content_lua: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    tcp_request_content_use_service: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    tcp_request_inspect_delay: Optional[str] = Field(default=None, pattern=r"^.{1,32}$")
    tcp_response_content_lua: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    tcp_response_inspect_delay: Optional[str] = Field(default=None, pattern=r"^.{1,32}$")
    custom: Optional[str] = Field(default=None, pattern=r"^.{1,4096}$")
    useServer: List[str] = Field(default_factory=list, description="Related server item not found")
    actionName: Optional[str] = None
    actionFind: Optional[str] = None
    actionValue: Optional[str] = None
    map_use_backend_file: Optional[str] = Field(default=None, description="Related map file item not found")
    map_use_backend_default: Optional[str] = Field(default=None, description="Related backend pool item not found")

