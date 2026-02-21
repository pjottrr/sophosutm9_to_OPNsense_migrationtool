from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import UIAwareMixin



class Group(UIAwareMixin):
    """
    Generated model for Group for OPNsense
    """
    
    gid: Optional[str] = None
    name: str = Field(..., pattern=r"^[a-zA-Z0-9\.\-_]{1,32}$", description="A groupname must contain a maximum of 32 alphanumeric characters.")
    scope: str = Field(default="user")
    description: Optional[str] = None
    priv: List[str] = Field(default_factory=list)
    member: List[str] = Field(default_factory=list)
    source_networks: Optional[str] = None

