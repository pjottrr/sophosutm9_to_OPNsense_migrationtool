from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.CertBase import CertBase


class Ca(CertBase):
    """
    Generated model for Ca for OPNsense
    """

    class CaCaActionEnum(str, Enum):
        EXISTING = "existing"
        INTERNAL = "internal"
        OCSP = "ocsp"

    class CaCaKeyTypeEnum(str, Enum):
        RSA_512 = "512"
        RSA_1024 = "1024"
        RSA_2048 = "2048"
        RSA_3072 = "3072"
        RSA_4096 = "4096"
        RSA_8192 = "8192"
        PRIME256V1 = "prime256v1"
        SECP384R1 = "secp384r1"
        SECP521R1 = "secp521r1"

    class CaCaDigestEnum(str, Enum):
        SHA1 = "sha1"
        SHA224 = "sha224"
        SHA256 = "sha256"
        SHA384 = "sha384"
        SHA512 = "sha512"

    crt: Optional[str] = None
    prv: Optional[str] = None
    serial: Optional[int] = None
    caref: Optional[str] = None
    action: CaCaActionEnum = Field(default=CaCaActionEnum.INTERNAL)
    key_type: CaCaKeyTypeEnum = Field(default=CaCaKeyTypeEnum.RSA_2048)
    digest: CaCaDigestEnum = Field(default=CaCaDigestEnum.SHA256)
    lifetime: int = Field(default=825)
    city: Optional[str] = Field(default=None, pattern=r"^[^\x00-\x08\x0b\x0c\x0e-\x1f\n]*$")
    state: Optional[str] = Field(default=None, pattern=r"^[^\x00-\x08\x0b\x0c\x0e-\x1f\n]*$")
    organization: Optional[str] = Field(default=None, pattern=r"^[^\x00-\x08\x0b\x0c\x0e-\x1f\n]*$")
    organizationalunit: Optional[str] = Field(default=None, pattern=r"^[^\x00-\x08\x0b\x0c\x0e-\x1f\n]*$")
    country: str = Field(default="NL")
    email: Optional[str] = Field(default=None, pattern=r"^[^\x00-\x08\x0b\x0c\x0e-\x1f\n]*$")
    commonname: Optional[str] = Field(default=None, pattern=r"^[^\x00-\x08\x0b\x0c\x0e-\x1f\n]*$")
    ocsp_uri: Optional[str] = None
    crt_payload: Optional[str] = None
    prv_payload: Optional[str] = None
    refcount: Optional[int] = None
    name: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

