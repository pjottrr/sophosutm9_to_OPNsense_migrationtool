from pysense.pydantic.pydantic_base import UIAwareMixin


class Response(UIAwareMixin):
    response: str
