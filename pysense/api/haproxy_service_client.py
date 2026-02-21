from pysense.base_client import BaseClient
from pysense.pydantic.Result import Result
from pysense.pydantic.Status import Status


class HaproxyServiceClient(BaseClient):

    def haproxy_service_configtest(self):
        data = self._get('haproxy/service/configtest')
        # print(data)
        return Result(**data)

    def haproxy_service_reconfigure(self):
        data = self._post('haproxy/service/reconfigure', '')
        # print(data)
        return Status(**data)
