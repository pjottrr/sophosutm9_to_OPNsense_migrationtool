from pysense.base_client import BaseClient
from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.SearchResult import BaseObjectSearchResult, ValidationSearchResult
from pysense.pydantic.Validation import Validation


class AcmeclientValidationsClient(BaseClient):

    def acmeclient_validations_search(self, search: SearchRequest = None) -> ValidationSearchResult:
        s = search
        if s is not None:
            s = s.__dict__
        data = self._post('acmeclient/validations/search', s)
        # print(data)
        return ValidationSearchResult.from_basic_dict(data, Validation)
