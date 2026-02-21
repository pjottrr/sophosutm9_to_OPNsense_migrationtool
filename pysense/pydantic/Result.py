from typing import Optional
from pysense.pydantic.pydantic_base import UIAwareMixin


class Result(UIAwareMixin):
    result: str
    uuid: Optional[str] = None
