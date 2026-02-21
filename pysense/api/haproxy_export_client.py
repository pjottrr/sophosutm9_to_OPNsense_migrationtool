from pysense.base_client import BaseClient
from pysense.pydantic.Response import Response


class HaproxyExportClient(BaseClient):

    def haproxy_export_config(self):
        data = self._get('haproxy/export/config')
        return Response(**data)
