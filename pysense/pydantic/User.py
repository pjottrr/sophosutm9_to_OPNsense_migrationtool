from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class User(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for User for OPNsense
    """
    
    uid: Optional[str] = None
    name: str = Field(...)
    disabled: bool = Field(default=False)
    scope: str = Field(default="user")
    expires: Optional[str] = None
    authorizedkeys: Optional[str] = None
    otp_seed: Optional[str] = None
    shell: Optional[str] = None
    password: Optional[str] = None
    scrambled_password: Optional[bool] = None
    pwd_changed_at: Optional[str] = None
    landing_page: Optional[str] = None
    comment: Optional[str] = None
    email: Optional[str] = None
    apikeys: Optional[str] = None
    priv: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    group_memberships: List[str] = Field(default_factory=list)
    descr: Optional[str] = None
    dashboard: Optional[str] = None

