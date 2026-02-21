import base64
import re
from pysense.api.acmeclient import Acmeclient
from pysense.api.haproxy_authentik import HaproxyAuthentik
from pysense.api.haproxy_service_client import HaproxyServiceClient
from pysense.api.haproxy_settings_client import HaproxySettingsClient
from pysense.api.helper import Helper
from pysense.base_client import BaseClient
from pysense.pydantic.Acl import Acl
from pysense.pydantic.Action import Action
from pysense.pydantic.Frontend import Frontend
from pysense.pydantic.Lua import Lua
from pysense.pydantic.SearchRequest import SearchRequest


class Haproxy(HaproxySettingsClient, HaproxyServiceClient, Acmeclient, BaseClient, HaproxyAuthentik):

    def haproxy_simple_proxy(self, domain, ip, port, frontend, ssl_provider=None, domain_aliases=None, sso=None, username=None, password=None) -> Acl:
        """
        If SSL provider is None, run on http mode

        :param password:
        :param username:
        :param sso:
        :param domain_aliases:
        :param domain:
        :param ip:
        :param port:
        :param frontend:
        :param ssl_provider:
        :return:
        """
        if self.debug:
            print('haproxy_simple_proxy', domain, ip, port, frontend, ssl_provider, domain_aliases, sso, username, password)

        if domain_aliases is None:
            domain_aliases = []
        if ssl_provider is not None:
            cert = self.acmecient(domain, ssl_provider)
        else:
            cert = None

        domain_aliases_ids = []
        for alias in domain_aliases:
            domain_aliases_ids.append(self.acmecient(alias, ssl_provider))

        frontend_found = self.find_frontend(frontend)
        if frontend_found is None:
            raise Exception("Frontend not found")

        domain_name_safe = self.domain_name_safe(domain)

        # ACL
        acl_search = self.haproxy_settings_searchAcls(SearchRequest.search(f'acl_{domain_name_safe}'))

        acl_uuid_primary = self.getcreate_acl(acl_search, Acl(
            name=f'acl_{domain_name_safe}',
            hdr=domain,
            hdr_beg=domain,
            expression=Acl.AclsAclExpressionEnum.HDR,
            description=f'Acl to host match {domain}')
        )

        acl_uuids = [acl_uuid_primary]

        for domain_alias in domain_aliases:
            acl_uuids.append(self.getcreate_acl(acl_search, Acl(
            name=f'acl_{domain_alias}',
            hdr=domain_alias,
            hdr_beg=domain_alias,
            expression=Acl.AclsAclExpressionEnum.HDR,
            description=f'Acl to host match {domain_alias}')))

        server_uuid = self.getcreate_server(domain, domain_name_safe, ip, port)

        backend_uuid = self.getcreate_backend(domain, domain_name_safe, server_uuid)

        action_uuid = self.getcreate_action(Action(
            linkedAcls=acl_uuids,
            use_backend=str(backend_uuid),
            description=domain,
            name=f'action_{domain_name_safe}',
            type=Action.ActionsActionTypeEnum.USE_BACKEND
        ))

        if cert is not None:
            cert = self.acmeclient_wait_cert_issued(domain, timeout=120)

        # print('get frontend')
        f = self.haproxy_settings_getFrontend(str(frontend_found))
        if action_uuid not in f.linkedActions:
            f.linkedActions.append(action_uuid)

        if cert is not None:
            if cert.certRefId not in f.ssl_certificates:
                f.ssl_certificates.append(cert.certRefId)

        for alias in domain_aliases:
            alias_cert = self.acmeclient_wait_cert_issued(alias, timeout=120)
            if alias_cert.certRefId is not None and alias_cert not in f.ssl_certificates:
                f.ssl_certificates.append(cert.certRefId)

        if username is not None and password is not None:
            auth_action = self.add_basic_auth_backend(acl_uuids, domain_name_safe, username, password)
            f.linkedActions.append(auth_action)

        self.haproxy_check_acl_order(f)

        fresult = self.haproxy_settings_setFrontend(str(frontend_found), f)
        if fresult.result == 'saved':
            f2 = self.haproxy_settings_getFrontend(frontend_found)
            # print(f2.frontend.linkedActions)
        else:
            f2 = None
            print('error updating frontend')

        if sso is not None:
            self.enable_sso(domain, acl_search)

        self.restart_if_possible()
        proto = 'https'
        if ssl_provider is None:
            proto = 'http'
        if f2 is not None:
            print('Service should be running now:')
            print(proto + '://' + domain + ':' + f2.get_port())
        else:
            print('Some error configuring service')
        return acl_uuid_primary

    def getcreate_action(self, action: Action, action_search = None):
        # Action
        if action_search is None:
            action_search = self.haproxy_settings_searchActions(SearchRequest.search(action.name))
        if len(action_search.rows) >= 1:
            for row in action_search.rows:
                if row.name == action.name:
                    return row.uuid
        action_new = self.haproxy_settings_addAction(action)
        return action_new.uuid

    def update_action(self, action_uuid: str, action: Action):
        old_action = self.haproxy_settings_getAction(action_uuid)
        search_actions = self.haproxy_settings_searchActions(SearchRequest.search(old_action.name))
        count = 0
        for action in search_actions.rows:
            if action.name == old_action.name:
                count += 1
        if count == 1:
            if old_action.custom != action.custom:
                self.haproxy_settings_setAction(action_uuid, action)

    def getcreate_backend(self, domain, domain_name_safe, server_uuid):
        name = f'backend_{domain_name_safe}'
        backend_search = self.haproxy_settings_searchBackend(SearchRequest.search(name))
        if len(backend_search.rows) >= 1:
            for row in backend_search.rows:
                if row.name == name:
                    return row.uuid
        else:
            backend_new = self.haproxy_settings_addBackend(name, str(server_uuid),
                                                       f'Backend for {domain}')
            return backend_new.uuid
        raise RuntimeError(f'domain {domain} has multiple backends but no matching backend')

    def getcreate_server(self, domain, domain_name_safe, ip, port):
        # Server
        name = f'server_{domain_name_safe}'
        server_search = self.haproxy_settings_searchServers(SearchRequest.search(name))
        if len(server_search.rows) >= 1:
            for row in server_search.rows:
                if row.name == name:
                    return row.uuid

        server_add = self.haproxy_settings_addServer(name, ip, port, f'Server for {domain}')
        return server_add.uuid

    def find_frontend(self, frontend):
        frontends = self.haproxy_settings_searchFrontends()
        frontend_found = None
        for f in frontends.rows:
            if f.name == frontend or f.uuid == frontend or f.description == frontend:
                frontend_found = f.uuid
        return frontend_found

    def getcreate_acl(self, acl_search, acl: Acl):
        if len(acl_search.rows) >= 1:
            for row in acl_search.rows:
                if row.name == acl.name:
                    return row.uuid
        acl_new = self.haproxy_settings_addAcl(acl)
        return acl_new.uuid

    def restart_if_possible(self):
        configtest = self.haproxy_service_configtest()
        if not Helper.config_has_errors(configtest):
            # print('restarting')
            # print("'", configtest.result, "'")
            self.haproxy_service_reconfigure()
        else:
            # print('config test failed')
            # print("'", configtest.result, "'")
            pass

    def haproxy_simple_remove(self, domain, ip, port, frontend, ssl_provider):
        frontend_found = self.find_frontend(frontend)
        if frontend_found is None:
            raise Exception("Frontend not found")

        domain_name_safe = self.domain_name_safe(domain)

        acl_search = self.haproxy_settings_searchAcls(SearchRequest.search(f'acl{domain_name_safe}'))
        server_search = self.haproxy_settings_searchServers(SearchRequest.search(f'server{domain_name_safe}'))
        backend_search = self.haproxy_settings_searchBackend(SearchRequest.search(f'backend{domain_name_safe}'))
        action_search = self.haproxy_settings_searchActions(SearchRequest.search(f'action{domain_name_safe}'))
        # if (len(action_search.rows) != 1 or len(backend_search.rows) != 1 or
        #         len(server_search.rows) != 1 or len(acl_search.rows) != 1):
        #     raise Exception("Not all data found")

        f = self.haproxy_settings_getFrontend(str(frontend_found))
        if action_search.rows[0].uuid in f.linkedActions:
            f.linkedActions.remove(action_search.rows[0].uuid)
        self.haproxy_settings_setFrontend(str(frontend_found), f)

        self.haproxy_settings_delAction(action_search.rows[0].uuid)
        self.haproxy_settings_delBackend(backend_search.rows[0].uuid)
        self.haproxy_settings_delServer(server_search.rows[0].uuid)
        self.haproxy_settings_delAcls(acl_search.rows[0].uuid)

    def get_https_redirect_rule(self, link_acl_uuid=None) -> Action:
        action_search = self.haproxy_settings_searchActions(SearchRequest.search('https-redirect'))
        if len(action_search.rows) == 0:
            action = Action(name='https-redirect', type=Action.ActionsActionTypeEnum.HTTP_REQUEST_REDIRECT, http_request_redirect='scheme https')
            action_response = self.haproxy_settings_addAction(action)
            action_uuid = action_response.uuid
        elif len(action_search.rows) == 1:
            action_uuid = action_search.rows[0].uuid
        else:
            # print('Error: multiple redirect rules found error')
            raise Exception('Error: multiple redirect rules found error')
        http_redirect_action = self.haproxy_settings_getAction(action_uuid)
        if link_acl_uuid is not None and link_acl_uuid not in http_redirect_action.linkedAcls:
            http_redirect_action.linkedAcls.append(link_acl_uuid)
            self.haproxy_settings_setAction(action_uuid, http_redirect_action)
        return http_redirect_action

    def link_acl_to_https_redirect(self, acl_uuid: str):
        self.get_https_redirect_rule(acl_uuid)

    def getcreate_lua_script(
            self,
            content: str,
            name: str,
            description: str,
            preload: str = '0',
            filename_schema: Lua.LuasLuaFilenameSchemeEnum = Lua.LuasLuaFilenameSchemeEnum.ID
    ) -> str:
        search_result = self.haproxy_settings_searchLuas(SearchRequest.search(name))
        rows = search_result.rows

        matched_row = None
        for row in rows:
            if row.name == name:
                if matched_row is not None:
                    raise RuntimeError('Multiple Lua scripts found with the same name')
                matched_row = row

        if matched_row is None:
            result = self.haproxy_settings_addLua(
                content, name, description, preload, filename_schema
            )
            return result.uuid

        if content != matched_row.content:
            raise ValueError('Lua script content does not match existing script')

        return matched_row.uuid

    def authentik_lua_check(self):
        """
        This method has to verify that all the required lua scripts are present in the config
        :return:
        """
        self.getcreate_lua_script(self.lua_json(), "json", "authentik json.lua for SSO", '0', Lua.LuasLuaFilenameSchemeEnum.NAME)
        self.getcreate_lua_script(self.lua_haproxyluahttp(), "haproxyluahttp", "authentik haproxy-lua-http.json for SSO", '0', Lua.LuasLuaFilenameSchemeEnum.NAME)
        self.getcreate_lua_script(self.lua_authrequest(), "authrequest", "authentik auth-request.lua for SSO", '1', Lua.LuasLuaFilenameSchemeEnum.ID)

    def authentik_acl_check(self, frontend, authentik_domain, authentik_http_ip, authentik_http_port):

        frontend_found = self.find_frontend(frontend)
        if frontend_found is None:
            raise Exception("Frontend not found")


        acl_search = self.haproxy_settings_searchAcls()

        acl_sso = self.acl_sso(acl_search)

        auth_domain = authentik_domain
        auth_ip = authentik_http_ip
        auth_port = authentik_http_port
        auth_domain_safe = self.domain_name_safe(auth_domain)

        auth_server_uuid = self.getcreate_server(auth_domain, auth_domain_safe, auth_ip, auth_port)

        auth_backend_uuid = self.getcreate_backend(auth_domain, auth_domain_safe, auth_server_uuid)
        auth_backend_uuid_str = str(auth_backend_uuid)
        auth_backend = self.haproxy_settings_getBackend(auth_backend_uuid)


        acl_https = self.getcreate_acl(acl_search, Acl(name="https",
                                                  expression=Acl.AclsAclExpressionEnum.SSL_FC,
                                                  description=""))
        acl_https_str = str(acl_https)

        acl_check_x_forward_for = self.getcreate_acl(acl_search, Acl(
            name="check-X-Forwarded-For",
            expression=Acl.AclsAclExpressionEnum.CUSTOM_ACL,
            custom_acl='req.hdr(X-Forwarded-For) -m found',
            description=""
        ))

        acl_check_x_forward_for_str = str(acl_check_x_forward_for)

        # acl_not_auth_response_successful = self.getcreate_acl(acl_search, AclRequest(name="check-X-Forwarded-For",
        #                                           expression="custom_acl",
        #                                           custom_acl='req.hdr(X-Forwarded-For) -m found',
        #                                           description=""))
        acl_not_auth_response_successful = self.getcreate_acl(acl_search, Acl(name="not_auth_response_successful",
                                                  expression=Acl.AclsAclExpressionEnum.CUSTOM_ACL,
                                                  custom_acl='var(txn.auth_response_successful) -m bool',
                                                  negate=True,
                                                  description=""))
        acl_not_auth_response_successful_str = str(acl_not_auth_response_successful)
        acl_auth_response_code_401 = self.getcreate_acl(acl_search, Acl(name="auth_response_code_401",
                                                  expression=Acl.AclsAclExpressionEnum.CUSTOM_ACL,
                                                  custom_acl='var(txn.auth_response_code) -m int 401',
                                                  description=""))
        acl_auth_response_code_401_str = str(acl_auth_response_code_401)
        acl_is_authentikoutpost = self.getcreate_acl(acl_search, Acl(name="is_authentikoutpost",
                                                  expression=Acl.AclsAclExpressionEnum.PATH_REG,
                                                  path_reg='^/outpost.goauthentik.io/',
                                                  description=""))
        acl_is_authentikoutpost_str = str(acl_is_authentikoutpost)
        acl_is_not_authentikoutpost = self.getcreate_acl(acl_search, Acl(name="is_not_authentikoutpost",
                                                  negate=True,
                                                  expression=Acl.AclsAclExpressionEnum.PATH_REG,
                                                  path_reg='^/outpost.goauthentik.io/',
                                                  description=""))
        acl_is_not_authentikoutpost_str = str(acl_is_not_authentikoutpost)

        action_schema_http = self.getcreate_action(Action(
            name='schema-http',
            testType=Action.ActionsActionTesttypeEnum.UNLESS,
            http_request_set_var_expr='str(http)',
            http_request_set_var_name='scheme',
            http_request_set_var_scope=Action.ActionsActionHttpRequestSetVarScopeEnum.REQ,
            http_response_set_var_scope=Action.ActionsActionHttpResponseSetVarScopeEnum.TXN,
            linkedAcls=[acl_https_str],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_VAR
        ))
        action_schema_http_str = str(action_schema_http)

        action_schema_https = self.getcreate_action(Action(
            name='schema-https',
            http_request_set_var_expr='str(https)',
            http_request_set_var_name='scheme',
            http_request_set_var_scope=Action.ActionsActionHttpRequestSetVarScopeEnum.REQ,
            linkedAcls=[acl_https_str],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_VAR
        ))
        action_schema_https_str = str(action_schema_https)

        action_x_forward_for = self.getcreate_action(Action(
            name='X-Forwarded-For',
            http_request_set_header_content='%[src]',
            http_request_set_header_name='X-Forwarded-For',
            linkedAcls=[acl_check_x_forward_for_str],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER
        ))
        action_x_forward_for_str = str(action_x_forward_for)

        action_x_forward_host = self.getcreate_action(Action(
            name='X-Forwarded-Host',
            http_request_set_header_content='%[req.hdr(Host)]',
            http_request_set_header_name='X-Forwarded-Host',
            linkedAcls=[],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER
        ))
        action_x_forward_host_str = str(action_x_forward_host)

        action_x_forward_method = self.getcreate_action(Action(
            name='X-Forwarded-Method',
            http_request_set_header_content='%[method]',
            http_request_set_header_name='X-Forwarded-Method',
            linkedAcls=[],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER
        ))
        action_x_forward_method_str = str(action_x_forward_method)

        action_x_forward_proto = self.getcreate_action(Action(
            name='X-Forwarded-Proto',
            http_request_set_header_content='%[var(req.scheme)]',
            http_request_set_header_name='X-Forwarded-Proto',
            linkedAcls=[],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER
        ))
        action_x_forward_proto_str = str(action_x_forward_proto)

        action_x_forward_uri = self.getcreate_action(Action(
            name='X-Forwarded-URI',
            http_request_set_header_content='%[path]%[var(req.questionmark)]%[query]',
            http_request_set_header_name='X-Forwarded-URI',
            linkedAcls=[],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER
        ))
        action_x_forward_uri_str = str(action_x_forward_uri)

        action_x_original_url = self.getcreate_action(Action(
            name='X-Original-URL',
            http_request_set_header_content='%[url]',
            http_request_set_header_name='X-Original-URL',
            linkedAcls=[],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_SET_HEADER
        ))
        action_x_original_url_str = str(action_x_original_url)

        actionrequest_lua_auth_intercept = Action(
            name='lua-auth-intercept',
            custom='http-request lua.auth-intercept '+ auth_backend.name +' /outpost.goauthentik.io/auth/nginx HEAD x-original-url,x-real-ip,x-forwarded-host,x-forwarded-proto,user-agent,cookie,accept,x-forwarded-method x-authentik-username,x-authentik-uid,x-authentik-email,x-authentik-name,x-authentik-groups -  ',
            linkedAcls=[str(acl_is_not_authentikoutpost), str(acl_not_auth_response_successful), str(acl_sso)],
            type=Action.ActionsActionTypeEnum.CUSTOM
        )
        action_lua_auth_intercept = self.getcreate_action(actionrequest_lua_auth_intercept)
        action_lua_auth_intercept_str = str(action_lua_auth_intercept)
        self.update_action(action_lua_auth_intercept_str, actionrequest_lua_auth_intercept)

        action_auth_deny = self.getcreate_action(Action(
            name='auth-deny',
            custom='http-request deny deny_status 401',
            linkedAcls=[str(acl_is_not_authentikoutpost), str(acl_not_auth_response_successful), str(acl_sso)],
            type=Action.ActionsActionTypeEnum.CUSTOM
        ))
        action_auth_deny_str = str(action_auth_deny)

        action_redirect = self.getcreate_action(Action(
            name='redirect',
            http_request_redirect='code 302 location /outpost.goauthentik.io/start?rd=%[hdr(X-Original-URL)]',
            linkedAcls=[str(acl_auth_response_code_401), str(acl_is_not_authentikoutpost), str(acl_not_auth_response_successful), str(acl_sso)],
            type=Action.ActionsActionTypeEnum.HTTP_REQUEST_REDIRECT
        ))
        action_redirect_str = str(action_redirect)

        action_proxyauth = self.getcreate_action(Action(
            name='proxyauth',
            use_backend=auth_backend_uuid_str,
            linkedAcls=[str(acl_is_authentikoutpost)],
            type=Action.ActionsActionTypeEnum.USE_BACKEND
        ))
        action_proxyauth_str = str(action_proxyauth)

        action_questionmark = self.getcreate_action(Action(
            name='questionmark',
            http_request_set_var_name='req.questionmark',
            http_request_set_var_expr='str(?)',
            # linkedAcls=','.join([str(acl_is_authentikoutpost)]),
            type=Action.ActionsActionTypeEnum.CUSTOM,
            custom='http-request set-var(req.questionmark) str(?)  if  { query -m found }'
        ))
        action_questionmark_str = str(action_questionmark)



        frontend = self.haproxy_settings_getFrontend(frontend_found)
        if action_proxyauth_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_proxyauth_str)
        if action_auth_deny_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_auth_deny_str)
        if action_redirect_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_redirect_str)
        if action_lua_auth_intercept_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_lua_auth_intercept_str)

        if action_x_original_url_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_x_original_url_str)
        if action_x_forward_uri_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_x_forward_uri_str)
        if action_x_forward_proto_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_x_forward_proto_str)
        if action_x_forward_method_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_x_forward_method_str)
        if action_x_forward_host_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_x_forward_host_str)
        if action_x_forward_for_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_x_forward_for_str)

        if action_questionmark_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_questionmark_str)

        if action_schema_https_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_schema_https_str)
        if action_schema_http_str not in frontend.linkedActions:
            frontend.linkedActions.append(action_schema_http_str)

        self.haproxy_settings_setFrontend(frontend_found, frontend)

        return action_lua_auth_intercept_str

    def enable_sso(self, domain, acl_search=None):
        acl_uuid = str(self.acl_sso(acl_search))
        acl = self.haproxy_settings_getAcl(acl_uuid)
        if acl.hdr is None:
            acl.hdr = ""
        if domain not in acl.hdr:
            acl.hdr = f"{acl.hdr} {domain}" if acl.hdr else domain
            acl.expression = Acl.AclsAclExpressionEnum.HDR
            self.haproxy_settings_setAcl(acl_uuid, acl)

    def disable_sso(self, domain, acl_search=None):
        acl_uuid = str(self.acl_sso(acl_search))
        acl = self.haproxy_settings_getAcl(acl_uuid).acl.get_acl()
        if domain in acl.hdr:
            acl.hdr = re.sub(rf'\b{re.escape(domain)}\b\s*', '', acl.hdr).strip()
            acl.expression = "hdr"
            self.haproxy_settings_setAcl(acl_uuid, acl)

    def add_basic_auth_backend(self, acl, domain, username, password):
        action_request = Action(
             description=f'Basic authentication on the backend for {domain} : {username}:{password}',
             http_request_add_header_content='Basic\\ '+base64.b64encode(f'{username}:{password}'.encode()).decode(),
             http_request_add_header_name='Authorization',
             name=f'action_{domain}_auth',
             operator=Action.ActionsActionOperatorEnum.AND,
             testType=Action.ActionsActionTesttypeEnum.IF,
             type=Action.ActionsActionTypeEnum.HTTP_REQUEST_ADD_HEADER,
             linkedAcls=acl
        )
        return self.getcreate_action(action_request)

    def acl_sso(self, acl_search = None):
        acl_search = self.haproxy_settings_searchAcls()
        return self.getcreate_acl(acl_search, Acl(
            name=self.acl_sso_protected_frontends,
            hdr='',
            hdr_beg='',
            expression=Acl.AclsAclExpressionEnum.HDR,
            description=f'All domains that require SSO')
        )

    AUTH_SUBORDER = [
        "schema-http",
        "schema-https",
        "questionmark",
        "X-",
        "lua-auth-intercept",
        "redirect",
        "auth-deny",
        "proxyauth",
    ]

    def _action_sort_key(self, action_name: str) -> tuple:
        # Check for action_*_auth first
        if action_name.endswith("_auth"):
            for index, token in enumerate(self.AUTH_SUBORDER):
                if token in action_name:
                    return (0, index, action_name)  # auth first, ordered by AUTH_SUBORDER
            return (0, len(self.AUTH_SUBORDER), action_name)  # unknown auth, last in auth group

        # Items explicitly in AUTH_SUBORDER
        for index, token in enumerate(self.AUTH_SUBORDER):
            if token in action_name:
                return (1, index, action_name)  # group 1, ordered by AUTH_SUBORDER

        # Other action_* items
        if action_name.startswith("action_"):
            return (2, 0, action_name)

        # Everything else
        return (3, 0, action_name)

    def haproxy_check_acl_order(self, f: Frontend):
        result = self.haproxy_settings_searchActions()
        actions = result.rows
        action_name_by_uuid = {str(a.uuid): a.name for a in actions}

        f.linkedActions.sort(
            key=lambda uuid: self._action_sort_key(action_name_by_uuid.get(uuid, ""))
        )