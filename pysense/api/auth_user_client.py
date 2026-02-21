from pysense.base_client import BaseClient
from pysense.pydantic.ApiUser import ApiUser
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import ApiUserSearchResult, UserSearchResult
from pysense.pydantic.User import User


class AuthUser(BaseClient):

    def auth_user_search_api_key(self, search: SearchRequest = None) -> ApiUserSearchResult:
        if search is not None:
            data = self._post('auth/user/search_api_key', search.__dict__)
        else:
            data = self._get('auth/user/search_api_key')
        return ApiUserSearchResult.from_ui_dict(data, ApiUser)

    def auth_user_search(self, search: SearchRequest = None) -> UserSearchResult:
        if search is not None:
            data = self._post('auth/user/search', search.__dict__)
        else:
            data = self._get('auth/user/search')
        return UserSearchResult.from_ui_dict(data, User)
