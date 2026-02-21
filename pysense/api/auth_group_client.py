from pysense.base_client import BaseClient
from pysense.pydantic.Group import Group
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import GroupSearchResult


class AuthGroup(BaseClient):

    def auth_group_search(self, search: SearchRequest = None) -> GroupSearchResult:
        if search is not None:
            data = self._post('auth/group/search', search.__dict__)
        else:
            data = self._get('auth/group/search')
        return GroupSearchResult.from_ui_dict(data, Group)

    def auth_group_get(self, uuid: str = None) -> Group:
        data = self._get('auth/group/get' + self._get_arg_formatter(uuid))
        return Group.from_ui_dict(data)
