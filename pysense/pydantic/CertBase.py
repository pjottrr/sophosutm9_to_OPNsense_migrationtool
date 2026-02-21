from typing import Optional
from pydantic import Field
from pysense.pydantic.pydantic_base import UIAwareMixin


class CertBase(UIAwareMixin):
    refid: Optional[str] = None
    descr: str = Field(...)
