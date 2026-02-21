from pysense.base_client import BaseClient
from pysense.pydantic.Acl import Acl
from pysense.pydantic.Action import Action
from pysense.pydantic.Backend import Backend
from pysense.pydantic.Frontend import Frontend
from pysense.pydantic.Lua import Lua
from pysense.pydantic.Result import Result
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import BaseObjectSearchResult, ActionSearchResult, LuaSearchResult
from pysense.pydantic.Server import Server


class HaproxySettingsClient(BaseClient):

    def haproxy_settings_get(self) -> Backend:
        data = self._get('haproxy/settings/get')
        # print(data)
        return Backend.from_ui_dict(data)

    def haproxy_settings_getBackend(self, uuid=None) -> Backend:
        data = self._get('haproxy/settings/get_backend' + self._get_arg_formatter(uuid))
        # print(data)
        return Backend.from_ui_dict(data)

    def haproxy_settings_getCpu(self) -> Backend:
        data = self._get('haproxy/settings/get_cpu')
        # print(data)
        return Backend.from_ui_dict(data)

    def haproxy_settings_getErrorfile(self) -> Backend:
        data = self._get('haproxy/settings/get_errorfile')
        # print(data)
        return Backend.from_ui_dict(**data)

    def haproxy_settings_getFcgi(self) -> Backend:
        data = self._get('haproxy/settings/get_fcgi')
        # print(data)
        return Backend.from_ui_dict(data)

    def haproxy_settings_getAcl(self, uuid=None) -> Acl:
        data = self._get('haproxy/settings/get_acl' + self._get_arg_formatter(uuid))
        # print(data)
        return Acl.from_ui_dict(data)

    def haproxy_settings_getServer(self, uuid=None) -> Server:
        data = self._get('haproxy/settings/get_server' + self._get_arg_formatter(uuid))
        # print(data)
        return Server.from_ui_dict(data)

    def haproxy_settings_getAction(self, uuid=None) -> Action:
        data = self._get('haproxy/settings/get_action' + self._get_arg_formatter(uuid))
        # print(data)
        return Action.from_ui_dict(data)

    def haproxy_settings_getFrontend(self, uuid=None) -> Frontend:
        data = self._get('haproxy/settings/get_frontend' + self._get_arg_formatter(uuid))
        # print(data)
        return Frontend.from_ui_dict(data)

    def haproxy_settings_getLue(self, uuid=None) -> Lua:
        data = self._get('haproxy/settings/get_lua' + self._get_arg_formatter(uuid))
        # print(data)
        return Lua.from_basic_dict(data)

    def haproxy_settings_searchFrontends(self, search: SearchRequest = None):
        if search is not None:
            data = self._post('haproxy/settings/search_frontends', search.__dict__)
        else:
            data = self._get('haproxy/settings/search_frontends')
        # print(data)
        return BaseObjectSearchResult(**data)

    def haproxy_settings_searchServers(self, search: SearchRequest = None):
        if search is not None:
            data = self._post('haproxy/settings/search_servers', search.__dict__)
        else:
            data = self._get('haproxy/settings/search_servers')
        # print(data)
        return BaseObjectSearchResult(**data)

    def haproxy_settings_searchBackend(self, search: SearchRequest = None):
        if search is not None:
            data = self._post('haproxy/settings/search_backends', search.__dict__)
        else:
            data = self._get('haproxy/settings/search_backends')
        # print(data)
        return BaseObjectSearchResult(**data)

    def haproxy_settings_searchLuas(self, search: SearchRequest = None):
        if search is not None:
            data = self._post('haproxy/settings/search_luas', search.__dict__)
        else:
            data = self._get('haproxy/settings/search_luas')
        return LuaSearchResult.from_basic_dict(data, Lua)

    def haproxy_settings_searchAcls(self, search: SearchRequest = None):
        if search is not None:
            data = self._post('haproxy/settings/search_acls', search.__dict__)
        else:
            data = self._get('haproxy/settings/search_acls')
        # print(data)
        return BaseObjectSearchResult(**data)

    def haproxy_settings_delAcls(self, uuid: str):
        data = self._post(f'haproxy/settings/del_acl/{str(uuid)}', '')
        # print(data)
        return Result(**data)

    def haproxy_settings_delAction(self, uuid: str):
        data = self._post(f'haproxy/settings/del_action/{uuid}', '')
        # print(data)
        return Result(**data)

    def haproxy_settings_delBackend(self, uuid: str):
        data = self._post(f'haproxy/settings/del_backend/{uuid}', '')
        # print(data)
        return Result(**data)

    def haproxy_settings_delServer(self, uuid: str):
        data = self._post(f'haproxy/settings/del_server/{uuid}', '')
        # print(data)
        return Result(**data)

    def haproxy_settings_searchActions(self, search: SearchRequest = None):
        if search is not None:
            data = self._post('haproxy/settings/search_actions', search.__dict__)
        else:
            data = self._get('haproxy/settings/search_actions')
        # print(data)
        return ActionSearchResult.from_basic_dict(data, Action)

    def haproxy_settings_getGroup(self):
        data = self._get('haproxy/settings/get_group')
        # print(data)
        return Acl.from_ui_dict(data)

    def haproxy_settings_getHealthcheck(self):
        data = self._get('haproxy/settings/get_healthcheck')
        # print(data)
        return Acl.from_ui_dict(data)

    def haproxy_settings_getMapfile(self):
        data = self._get('haproxy/settings/get_mapfile')
        # print(data)
        return Acl.from_ui_dict(data)

    def haproxy_settings_addServer(self, name, address, port, description="", ssl=False):
        server = Server(name=name, address=address, port=port, description=description, ssl=ssl)
        result = self.haproxy_settings_add_server(server)
        # print(data)
        return result

    def haproxy_settings_add_server(self, server: Server):
        data = self._post('haproxy/settings/add_server', server)
        # print(data)
        return Result(**data)

    def haproxy_settings_addAction(self, action: Action):
        data = self._post('haproxy/settings/add_action', action)
        # print(data)
        return Result(**data)

    def haproxy_settings_getUser(self):
        data = self._get('haproxy/settings/get_user')
        # print(data)
        return data

    def haproxy_settings_getmailer(self):
        data = self._get('haproxy/settings/getmailer')
        # print(data)
        return data

    def haproxy_settings_getresolver(self):
        data = self._get('haproxy/settings/getresolver')
        # print(data)
        return data

    def haproxy_settings_addAcl(self, acl : Acl):
        data = self._post('haproxy/settings/add_acl', acl)
        # print(data)
        return Result(**data)

    def haproxy_settings_addBackend(self, name, server, description):
        backend = Backend(name=name, description=description, linkedServers=[server])
        data = self._post('haproxy/settings/add_backend', backend)
        # print(data)
        return Result(**data)

    def haproxy_settings_addFrontend(self, name, bind, actions, description):
        frontend = Frontend(name=name, bind=bind, linkedActions=actions, description=description)
        data = self._post('haproxy/settings/add_frontend', frontend)
        # print(data)
        return Result(**data)

    def haproxy_settings_addLua(self, content, name, description, preload=False, filename_scheme: Lua.LuasLuaFilenameSchemeEnum=Lua.LuasLuaFilenameSchemeEnum.ID):
        lua=Lua(
            enabled=True,
            name=name,
            description=description,
            preload=preload,
            filename_scheme=filename_scheme,
            content=content
        )
        data = self._post('haproxy/settings/add_lua/', lua)
        # print(data)
        return Result(**data)

    def haproxy_settings_setFrontend(self, uuid, frontend: Frontend):
        data = self._post(f'haproxy/settings/set_frontend/{uuid}', frontend)
        # print(data)
        return Result(**data)

    def haproxy_settings_setAcl(self, uuid, acl: Acl):
        data = self._post(f'haproxy/settings/set_acl/{uuid}', acl)
        return Result(**data)

    def haproxy_settings_setLua(self, uuid, lua: Lua):
        data = self._post(f'haproxy/settings/set_lua/{uuid}', lua)
        return Result(**data)

    def haproxy_settings_setAction(self, uuid, action: Action):
        data = self._post(f'haproxy/settings/set_action/{uuid}', action)
        return Result(**data)
