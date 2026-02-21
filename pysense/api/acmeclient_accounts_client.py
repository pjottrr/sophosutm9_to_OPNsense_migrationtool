from pysense.base_client import BaseClient
from pysense.pydantic.Account import Account
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import AccountSearchResult


class AcmeclientAccountsClient(BaseClient):

    def acmeclient_accounts_search(self, search: SearchRequest = None) -> AccountSearchResult:
        s = search
        if s is not None:
            s = s.__dict__
        data = self._post('acmeclient/accounts/search', s)
        # print(data)
        return AccountSearchResult.from_basic_dict(data, Account)
