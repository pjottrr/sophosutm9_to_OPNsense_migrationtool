from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Certificate(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Certificate for OPNsense (from the ACME plugin)
    """

    class CertificatesCertificateKeylengthEnum(str, Enum):
        KEY_2048 = "key_2048"
        KEY_3072 = "key_3072"
        KEY_4096 = "key_4096"
        KEY_EC256 = "key_ec256"
        KEY_EC384 = "key_ec384"

    class CertificatesCertificateAliasmodeEnum(str, Enum):
        NONE = "none"
        AUTOMATIC = "automatic"
        DOMAIN = "domain"
        CHALLENGE = "challenge"

    id: Optional[str] = None
    enabled: bool = Field(...)
    name: str = Field(..., pattern=r"[^\s^\t^,^;^\\^\/^(^)^\[^\]]{1,255}", description="Please provide a valid FQDN, i.e. www.example.com or mail.example.com (max 255 characters).")
    description: Optional[str] = None
    altNames: List[str] = Field(default_factory=list)
    account: str = Field(..., description="Related item not found.")
    validationMethod: str = Field(..., description="Related item not found.")
    keyLength: CertificatesCertificateKeylengthEnum = Field(...)
    ocsp: bool = False
    restartActions: List[str] = Field(default_factory=list)
    autoRenewal: bool = Field(...)
    renewInterval: int = Field(..., ge=1, le=5000)
    aliasmode: CertificatesCertificateAliasmodeEnum = Field(...)
    domainalias: Optional[str] = None
    challengealias: Optional[str] = None
    certRefId: Optional[str] = None
    lastUpdate: Optional[int] = None
    statusCode: int = 100
    statusLastUpdate: Optional[int] = None

