from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Category(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Category for OPNsense
    """
    name: str = Field(...)
    auto: Optional[bool] = None
    color: Optional[str] = None

