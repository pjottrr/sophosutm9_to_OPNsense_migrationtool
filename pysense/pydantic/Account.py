from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Account(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Account for OPNsense
    """

    class AccountsAccountCaEnum(str, Enum):
        BUYPASS = "buypass"
        BUYPASS_TEST = "buypass_test"
        GOOGLE = "google"
        GOOGLE_TEST = "google_test"
        LETSENCRYPT = "letsencrypt"
        LETSENCRYPT_TEST = "letsencrypt_test"
        SSLCOM = "sslcom"
        ZEROSSL = "zerossl"
        CUSTOM = "custom"

    id: Optional[str] = None
    enabled: bool = Field(default=True)
    name: str = Field(..., pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = Field(default=None, pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    email: Optional[str] = None
    ca: AccountsAccountCaEnum = Field(default=AccountsAccountCaEnum.LETSENCRYPT)
    custom_ca: Optional[str] = Field(default=None, pattern=r"^https?:\/\/.*[^\/]$", description="The URL must be a valid ACME endpoint without a trailing slash.")
    eab_kid: Optional[str] = Field(default=None, pattern=r"^.{1,8192}$", description="Should be a string between 1 and 8192 characters.")
    eab_hmac: Optional[str] = Field(default=None, pattern=r"^.{1,8192}$", description="Should be a string between 1 and 8192 characters.")
    key: Optional[str] = None
    statusCode: int = Field(default=100, ge=100, le=1000)
    statusLastUpdate: Optional[int] = None
