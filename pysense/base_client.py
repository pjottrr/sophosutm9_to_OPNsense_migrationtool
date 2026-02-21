import json
import re
import requests
from pydantic import BaseModel

from pysense.pydantic.SearchRequest import SearchRequest
from pysense.pydantic.pydantic_base import UIAwareMixin

DEFAULT_TIMEOUT = 5

# All the successful HTTP status codes from RFC 7231 & 4918
HTTP_SUCCESS = (200, 201, 202, 203, 204, 205, 206, 207)


class APIException(Exception):
    """Representation of the API exception."""

    def __init__(self, status_code=None, resp_body=None, *args, **kwargs):
        """Initialize the API exception."""
        self.resp_body = resp_body
        self.status_code = status_code
        self.json = None
        self.uuid = None
        try:
            self.json = json.loads(resp_body)
            self.uuid = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', self.json['errorMessage']).group(1)
            # print(self.uuid)
        except Exception as e:
            print(e)


        message = kwargs.get("message", resp_body)
        super(APIException, self).__init__(message, *args, **kwargs)


class BaseClient(object):
    """Representation of the OPNsense API client."""

    def __init__(
        self, api_key, api_secret, base_url, verify_cert=False, timeout=DEFAULT_TIMEOUT
    ):
        """Initialize the OPNsense API client."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.verify_cert = verify_cert
        self.timeout = timeout
        self.debug = False
        # settings
        self.acl_sso_protected_frontends = 'acl_sso_protected_frontends'

    def _process_response(self, response, raw=False):
        """Handle the response."""
        if response.status_code in HTTP_SUCCESS:
            return response.text if raw else json.loads(response.text)
        else:
            raise APIException(
                status_code=response.status_code, resp_body=response.text
            )

    def _get(self, endpoint, raw=False):
        req_url = "{}/{}".format(self.base_url, endpoint)
        if self.debug:
            print('GET', req_url)
        response = requests.get(
            req_url,
            verify=self.verify_cert,
            auth=(self.api_key, self.api_secret),
            timeout=self.timeout,
        )
        if self.debug:
            print('GET', req_url)
            print(response.text)
        return self._process_response(response, raw)

    def _post(self, endpoint, body, raw=False):
        req_url = "{}/{}".format(self.base_url, endpoint)
        # print(req_url, body)
        if isinstance(body, UIAwareMixin):
            body = body.to_simple_dict()
        elif isinstance(body, BaseModel):
            body = body.model_dump()
        if not isinstance(body, dict) and body != '' and body is not None:
            print('Warn', body, 'is not a dict')
        response = requests.post(
            req_url,
            json=body,
            verify=self.verify_cert,
            auth=(self.api_key, self.api_secret),
            timeout=self.timeout,
        )
        if self.debug:
            print('POST', req_url)
            print('body:', body)
            print(response.text)
        return self._process_response(response, raw)

    def _search(self, url, search: SearchRequest = None):
        if search is None:
            return self._get(url)
        else:
            return self._post(url, search)

    @staticmethod
    def _get_arg_formatter(url_argument=None):
        if url_argument is not None:
            url_argument = "/" + str(url_argument)
        else:
            url_argument = ""
        return url_argument

    @staticmethod
    def domain_name_safe(name:str):
        """
        Make a domain name (example.com) safe to be used as entity name (example_dot_com)

        :param name:
        :return:
        """
        return name.replace('.', '_dot_')