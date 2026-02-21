from pysense.base_client import BaseClient
from pysense.pydantic.Cert import Cert
from pysense.pydantic.CertBase import CertBase
from pysense.pydantic.SearchResult import CertSearchResult, CertBaseSearchResult


class TrustCrlClient(BaseClient):

    def trust_crl_search(self) -> CertSearchResult:
        data = self._get('trust/crl/search')
        data['rows'] = [x for x in data['rows'] if not (x.get("refid") == "" and x.get("descr") == "")]
        data['rowCount'] = len(data['rows'])
        return CertBaseSearchResult.from_ui_dict(data, CertBase)

    def trust_crl_get(self, uuid):
        data = self._get('trust/crl/get/' + str(uuid))
        return Cert.from_ui_dict(data)
