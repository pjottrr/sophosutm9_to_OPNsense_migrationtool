import time
from pysense.pydantic.Cert import Cert
from pysense.pydantic.Result import Result


class Helper:

    @staticmethod
    def config_has_errors(result: Result):
        return result.result.find('Error') == 0

    @staticmethod
    def cert_expired(cert: Cert, compare_time: int=None) -> bool:
        if compare_time is None:
            compare_time = time.time()
        if int(cert.valid_to) > compare_time > int(cert.valid_from):
            return False
        return True
