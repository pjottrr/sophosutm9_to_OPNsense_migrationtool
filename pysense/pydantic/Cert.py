from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.CertBase import CertBase



class Cert(CertBase):
    """
    Generated model for Cert for OPNsense
    """

    class CertCertActionEnum(str, Enum):
        INTERNAL = "internal"
        EXTERNAL = "external"
        IMPORT = "import"
        SIGN_CSR = "sign_csr"
        IMPORT_CSR = "import_csr"
        REISSUE = "reissue"
        MANUAL = "manual"

    class CertCertKeyTypeEnum(str, Enum):
        RSA_512 = "512"
        RSA_1024 = "1024"
        RSA_2048 = "2048"
        RSA_3072 = "3072"
        RSA_4096 = "4096"
        RSA_8192 = "8192"
        PRIME256V1 = "prime256v1"
        SECP384R1 = "secp384r1"
        SECP521R1 = "secp521r1"

    class CertCertDigestEnum(str, Enum):
        SHA1 = "sha1"
        SHA224 = "sha224"
        SHA256 = "sha256"
        SHA384 = "sha384"
        SHA512 = "sha512"

    class CertCertCertTypeEnum(str, Enum):
        USR_CERT = "usr_cert"
        SERVER_CERT = "server_cert"
        COMBINED_SERVER_CLIENT = "combined_server_client"
        V3_CA = "v3_ca"

    class CertCertPrivateKeyLocationEnum(str, Enum):
        FIREWALL = "firewall"
        LOCAL = "local"

    caref: Optional[str] = None
    crt: Optional[str] = None
    csr: Optional[str] = None
    prv: Optional[str] = None
    action: CertCertActionEnum = Field(...)
    key_type: CertCertKeyTypeEnum = Field(...)
    digest: CertCertDigestEnum = Field(...)
    cert_type: CertCertCertTypeEnum = Field(...)
    lifetime: int = Field(...)
    private_key_location: CertCertPrivateKeyLocationEnum = Field(...)
    city: Optional[str] = None
    state: Optional[str] = None
    organization: Optional[str] = None
    organizationalunit: Optional[str] = None
    country: str = Field(...)
    email: Optional[str] = None
    commonname: Optional[str] = None
    ocsp_uri: Optional[str] = None
    altnames_dns: Optional[str] = None
    altnames_ip: Optional[str] = None
    altnames_uri: Optional[str] = None
    altnames_email: Optional[str] = None
    crt_payload: Optional[str] = None
    csr_payload: Optional[str] = None
    prv_payload: Optional[str] = None
    rfc3280_purpose: Optional[str] = None
    in_use: Optional[bool] = None
    is_user: Optional[bool] = None
    name: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

