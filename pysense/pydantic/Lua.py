from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Lua(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Lua for OPNsense
    """

    class LuasLuaFilenameSchemeEnum(str, Enum):
        ID = "id"
        NAME = "name"

    id: str = Field(default='')
    enabled: bool = Field(default=True)
    name: str = Field(..., pattern=r"^[^\t^,^;^\.^\[^\]^\{^\}]{1,255}$", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = Field(default=None, pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    preload: bool = Field(default=True)
    filename_scheme: LuasLuaFilenameSchemeEnum = Field(default=LuasLuaFilenameSchemeEnum.ID)
    content: str = Field(...)

