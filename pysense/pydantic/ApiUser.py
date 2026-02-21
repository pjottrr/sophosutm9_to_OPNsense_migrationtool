from pydantic import Field
from pysense.pydantic.pydantic_base import UIAwareMixin


class ApiUser(UIAwareMixin):
    username: str = Field(...)
    key: str = Field(...)
    id: str = Field(...)
