from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Validation(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Validation for OPNsense
    """

    class ValidationsValidationMethodEnum(str, Enum):
        HTTP01 = "http01"
        DNS01 = "dns01"
        TLSALPN01 = "tlsalpn01"

    class ValidationsValidationHttpServiceEnum(str, Enum):
        OPNSENSE = "opnsense"
        HAPROXY = "haproxy"

    class ValidationsValidationTlsalpnServiceEnum(str, Enum):
        ACME = "acme"

    class ValidationsValidationDnsServiceEnum(str, Enum):
        DNS_1984HOSTING = "dns_1984hosting"
        DNS_ACMEDNS = "dns_acmedns"
        DNS_ACMEPROXY = "dns_acmeproxy"
        DNS_ACTIVE24 = "dns_active24"
        DNS_AD = "dns_ad"
        DNS_ALI = "dns_ali"
        DNS_KAS = "dns_kas"
        DNS_ARVAN = "dns_arvan"
        DNS_ARTFILES = "dns_artfiles"
        DNS_AURORA = "dns_aurora"
        DNS_AUTODNS = "dns_autodns"
        DNS_AWS = "dns_aws"
        DNS_AZURE = "dns_azure"
        DNS_BUNNY = "dns_bunny"
        DNS_CLOUDNS = "dns_cloudns"
        DNS_CF = "dns_cf"
        DNS_CX = "dns_cx"
        DNS_CN = "dns_cn"
        DNS_CONOHA = "dns_conoha"
        DNS_CONSTELLIX = "dns_constellix"
        DNS_CPANEL = "dns_cpanel"
        DNS_CYON = "dns_cyon"
        DNS_DDNSS = "dns_ddnss"
        DNS_DESEC = "dns_desec"
        DNS_DGON = "dns_dgon"
        DNS_DA = "dns_da"
        DNS_DNSEXIT = "dns_dnsexit"
        DNS_DNSHOME = "dns_dnshome"
        DNS_DNSIMPLE = "dns_dnsimple"
        DNS_DNSSERVICES = "dns_dnsservices"
        DNS_DOMENESHOP = "dns_domeneshop"
        DNS_ME = "dns_me"
        DNS_DP = "dns_dp"
        DNS_DOAPI = "dns_doapi"
        DNS_DO = "dns_do"
        DNS_DREAMHOST = "dns_dreamhost"
        DNS_DUCKDNS = "dns_duckdns"
        DNS_DYN = "dns_dyn"
        DNS_DYNU = "dns_dynu"
        DNS_DYNV6 = "dns_dynv6"
        DNS_EASYDNS = "dns_easydns"
        DNS_EUSERV = "dns_euserv"
        DNS_EXOSCALE = "dns_exoscale"
        DNS_FORNEX = "dns_fornex"
        DNS_FREEDNS = "dns_freedns"
        DNS_GANDI_LIVEDNS = "dns_gandi_livedns"
        DNS_GD = "dns_gd"
        DNS_GCLOUD = "dns_gcloud"
        DNS_GOOGLEDOMAINS = "dns_googledomains"
        DNS_GDNSDK = "dns_gdnsdk"
        DNS_HETZNER = "dns_hetzner"
        DNS_HETZNERCLOUD = "dns_hetznercloud"
        DNS_HEXONET = "dns_hexonet"
        DNS_HOSTINGDE = "dns_hostingde"
        DNS_HE = "dns_he"
        DNS_INFOBLOX = "dns_infoblox"
        DNS_INFOMANIAK = "dns_infomaniak"
        DNS_INTERNETBS = "dns_internetbs"
        DNS_INWX = "dns_inwx"
        DNS_IONOS = "dns_ionos"
        DNS_IPV64 = "dns_ipv64"
        DNS_ISPCONFIG = "dns_ispconfig"
        DNS_JD = "dns_jd"
        DNS_JOKER = "dns_joker"
        DNS_KINGHOST = "dns_kinghost"
        DNS_KNOT = "dns_knot"
        DNS_LEASEWEB = "dns_leaseweb"
        DNS_LEXICON = "dns_lexicon"
        DNS_LIMACITY = "dns_limacity"
        DNS_LINODE = "dns_linode"
        DNS_LINODE_V4 = "dns_linode_v4"
        DNS_LOOPIA = "dns_loopia"
        DNS_LUA = "dns_lua"
        DNS_MIAB = "dns_miab"
        DNS_MIJNHOST = "dns_mijnhost"
        DNS_MYDNSJP = "dns_mydnsjp"
        DNS_MYTHIC_BEASTS = "dns_mythic_beasts"
        DNS_NAMECOM = "dns_namecom"
        DNS_NAMECHEAP = "dns_namecheap"
        DNS_NAMESILO = "dns_namesilo"
        DNS_NEDERHOST = "dns_nederhost"
        DNS_NETCUP = "dns_netcup"
        DNS_NIC = "dns_nic"
        DNS_NJALLA = "dns_njalla"
        DNS_NSONE = "dns_nsone"
        DNS_NSUPDATE = "dns_nsupdate"
        DNS_ONLINE = "dns_online"
        DNS_OPNSENSE = "dns_opnsense"
        DNS_OCI = "dns_oci"
        DNS_OVH = "dns_ovh"
        DNS_PDNS = "dns_pdns"
        DNS_PLESKXML = "dns_pleskxml"
        DNS_POINTHQ = "dns_pointhq"
        DNS_PORKBUN = "dns_porkbun"
        DNS_RACKSPACE = "dns_rackspace"
        DNS_RAGE4 = "dns_rage4"
        DNS_REGRU = "dns_regru"
        DNS_SCALEWAY = "dns_scaleway"
        DNS_SCHLUNDTECH = "dns_schlundtech"
        DNS_SELECTEL = "dns_selectel"
        DNS_SELFHOST = "dns_selfhost"
        DNS_SERVERCOW = "dns_servercow"
        DNS_SIMPLY = "dns_simply"
        DNS_TRANSIP = "dns_transip"
        DNS_UDR = "dns_udr"
        DNS_UNOEURO = "dns_unoeuro"
        DNS_VARIOMEDIA = "dns_variomedia"
        DNS_VSCALE = "dns_vscale"
        DNS_VULTR = "dns_vultr"
        DNS_WEBSUPPORT = "dns_websupport"
        DNS_WORLD4YOU = "dns_world4you"
        DNS_YANDEX = "dns_yandex"
        DNS_ZILORE = "dns_zilore"
        DNS_ZONE = "dns_zone"
        DNS_ZONEEDIT = "dns_zoneedit"
        DNS_ZONOMI = "dns_zonomi"

    class ValidationsValidationDnsLexiconProviderEnum(str, Enum):
        ALIYUN = "aliyun"
        AURORA = "aurora"
        AUTO = "auto"
        AZURE = "azure"
        CLOUDFLARE = "cloudflare"
        CLOUDNS = "cloudns"
        CLOUDXNS = "cloudxns"
        CONOHA = "conoha"
        CONSTELLIX = "constellix"
        DIGITALOCEAN = "digitalocean"
        DINAHOSTING = "dinahosting"
        DIRECTADMIN = "directadmin"
        DNSIMPLE = "dnsimple"
        DNSMADEEASY = "dnsmadeeasy"
        DNSPARK = "dnspark"
        DNSPOD = "dnspod"
        DREAMHOST = "dreamhost"
        EASYDNS = "easydns"
        EASYNAME = "easyname"
        EXOSCALE = "exoscale"
        GANDI = "gandi"
        GEHIRN = "gehirn"
        GLESYS = "glesys"
        GODADDY = "godaddy"
        GOOGLECLOUDDNS = "googleclouddns"
        GRATISDNS = "gratisdns"
        HENET = "henet"
        HETZNER = "hetzner"
        HOVER = "hover"
        INFOBLOX = "infoblox"
        INTERNETBS = "internetbs"
        INWX = "inwx"
        LINODE = "linode"
        LINODE4 = "linode4"
        LOCALZONE = "localzone"
        LUADNS = "luadns"
        MEMSET = "memset"
        NAMECHEAP = "namecheap"
        NAMESILO = "namesilo"
        NETCUP = "netcup"
        NFSN = "nfsn"
        NSONE = "nsone"
        ONAPP = "onapp"
        ONLINE = "online"
        OVH = "ovh"
        PLESK = "plesk"
        POINTHQ = "pointhq"
        POWERDNS = "powerdns"
        RACKSPACE = "rackspace"
        RAGE4 = "rage4"
        ROUTE53 = "route53"
        SAFEDNS = "safedns"
        SAKURACLOUD = "sakuracloud"
        SOFTLAYER = "softlayer"
        SUBREG = "subreg"
        TRANSIP = "transip"
        VULTR = "vultr"
        YANDEX = "yandex"
        ZEIT = "zeit"
        ZILORE = "zilore"
        ZONOMI = "zonomi"

    class ValidationsValidationDnsSlApiverEnum(str, Enum):
        V1 = "v1"
        V2 = "v2"

    class ValidationsValidationDnsKasAuthtypeEnum(str, Enum):
        PLAIN = "plain"
        SHA1 = "sha1"

    id: Optional[str] = None
    enabled: bool = Field(default=True)
    name: str = Field(..., pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    description: Optional[str] = Field(default=None, pattern=r"^.{1,255}$", description="Should be a string between 1 and 255 characters.")
    method: ValidationsValidationMethodEnum = Field(default=ValidationsValidationMethodEnum.DNS01)
    http_service: ValidationsValidationHttpServiceEnum = Field(default=ValidationsValidationHttpServiceEnum.OPNSENSE)
    http_opn_autodiscovery: bool = Field(default=True)
    http_opn_interface: Optional[str] = None
    http_opn_ipaddresses: List[str] = Field(default_factory=list)
    http_haproxyInject: bool = Field(default=True)
    http_haproxyFrontends: List[str] = Field(default_factory=list, description="Related HAProxy frontend not found.")
    tlsalpn_service: ValidationsValidationTlsalpnServiceEnum = Field(default=ValidationsValidationTlsalpnServiceEnum.ACME)
    tlsalpn_acme_autodiscovery: bool = Field(default=True)
    tlsalpn_acme_interface: Optional[str] = None
    tlsalpn_acme_ipaddresses: List[str] = Field(default_factory=list)
    dns_service: ValidationsValidationDnsServiceEnum = Field(default=ValidationsValidationDnsServiceEnum.DNS_FREEDNS)
    dns_sleep: int = Field(default=0, ge=0, le=84600, description="Please specify a value between 0 and 84600 seconds.")
    dns_active24_token: Optional[str] = None
    dns_ad_key: Optional[str] = None
    dns_ali_key: Optional[str] = None
    dns_ali_secret: Optional[str] = None
    dns_autodns_user: Optional[str] = None
    dns_autodns_password: Optional[str] = None
    dns_autodns_context: Optional[str] = None
    dns_aws_id: Optional[str] = None
    dns_aws_secret: Optional[str] = None
    dns_azuredns_subscriptionid: Optional[str] = None
    dns_azuredns_tenantid: Optional[str] = None
    dns_azuredns_appid: Optional[str] = None
    dns_azuredns_clientsecret: Optional[str] = None
    dns_azuredns_managedidentity: bool = Field(default=False)
    dns_bunny_api_key: Optional[str] = None
    dns_cf_email: Optional[str] = None
    dns_cf_key: Optional[str] = None
    dns_cf_token: Optional[str] = None
    dns_cf_account_id: Optional[str] = None
    dns_cf_zone_id: Optional[str] = None
    dns_cloudns_auth_id: Optional[str] = None
    dns_cloudns_sub_auth_id: Optional[str] = None
    dns_cloudns_auth_password: Optional[str] = None
    dns_cx_key: Optional[str] = None
    dns_cx_secret: Optional[str] = None
    dns_cyon_user: Optional[str] = None
    dns_cyon_password: Optional[str] = None
    dns_da_key: Optional[str] = None
    dns_da_insecure: bool = Field(default=True)
    dns_ddnss_token: Optional[str] = None
    dns_dgon_key: Optional[str] = None
    dns_dnsexit_auth_user: Optional[str] = None
    dns_dnsexit_auth_pass: Optional[str] = None
    dns_dnsexit_api: Optional[str] = None
    dns_dnshome_password: Optional[str] = None
    dns_dnshome_subdomain: Optional[str] = None
    dns_dnsimple_token: Optional[str] = None
    dns_dnsservices_user: Optional[str] = None
    dns_dnsservices_password: Optional[str] = None
    dns_doapi_token: Optional[str] = None
    dns_do_pid: Optional[str] = None
    dns_do_password: Optional[str] = None
    dns_domeneshop_token: Optional[str] = None
    dns_domeneshop_secret: Optional[str] = None
    dns_dp_id: Optional[str] = None
    dns_dp_key: Optional[str] = None
    dns_dh_key: Optional[str] = None
    dns_duckdns_token: Optional[str] = None
    dns_dyn_customer: Optional[str] = None
    dns_dyn_user: Optional[str] = None
    dns_dyn_password: Optional[str] = None
    dns_dynu_clientid: Optional[str] = None
    dns_dynu_secret: Optional[str] = None
    dns_freedns_user: Optional[str] = None
    dns_freedns_password: Optional[str] = None
    dns_fornex_api_key: Optional[str] = None
    dns_gandi_livedns_key: Optional[str] = None
    dns_gandi_livedns_token: Optional[str] = None
    dns_gcloud_key: Optional[str] = None
    dns_googledomains_access_token: Optional[str] = None
    dns_googledomains_zone: Optional[str] = None
    dns_gd_key: Optional[str] = None
    dns_gd_secret: Optional[str] = None
    dns_hostingde_server: Optional[str] = None
    dns_hostingde_apiKey: Optional[str] = None
    dns_he_user: Optional[str] = None
    dns_he_password: Optional[str] = None
    dns_infoblox_credentials: Optional[str] = None
    dns_infoblox_server: Optional[str] = None
    dns_inwx_user: Optional[str] = None
    dns_inws_password: Optional[str] = None
    dns_inwx_password: Optional[str] = None
    dns_inwx_shared_secret: Optional[str] = None
    dns_ionos_prefix: Optional[str] = None
    dns_ionos_secret: Optional[str] = None
    dns_ipv64_token: Optional[str] = None
    dns_ispconfig_user: Optional[str] = None
    dns_ispconfig_password: Optional[str] = None
    dns_ispconfig_api: Optional[str] = None
    dns_ispconfig_insecure: bool = Field(default=True)
    dns_jd_id: Optional[str] = None
    dns_jd_region: Optional[str] = None
    dns_jd_secret: Optional[str] = None
    dns_joker_username: Optional[str] = None
    dns_joker_password: Optional[str] = None
    dns_kinghost_username: Optional[str] = None
    dns_kinghost_password: Optional[str] = None
    dns_knot_server: Optional[str] = None
    dns_knot_key: Optional[str] = None
    dns_lexicon_provider: ValidationsValidationDnsLexiconProviderEnum = Field(default=ValidationsValidationDnsLexiconProviderEnum.CLOUDFLARE)
    dns_lexicon_user: Optional[str] = None
    dns_lexicon_token: Optional[str] = None
    dns_limacity_apikey: Optional[str] = None
    dns_linode_key: Optional[str] = None
    dns_linode_v4_key: Optional[str] = None
    dns_loopia_api: str = Field(default="https://api.loopia.se/RPCSERV")
    dns_loopia_user: Optional[str] = None
    dns_loopia_password: Optional[str] = None
    dns_lua_email: Optional[str] = None
    dns_lua_key: Optional[str] = None
    dns_miab_user: Optional[str] = None
    dns_miab_password: Optional[str] = None
    dns_miab_server: Optional[str] = None
    dns_me_key: Optional[str] = None
    dns_me_secret: Optional[str] = None
    dns_mydnsjp_masterid: Optional[str] = None
    dns_mydnsjp_password: Optional[str] = None
    dns_mythic_beasts_key: Optional[str] = None
    dns_mythic_beasts_secret: Optional[str] = None
    dns_namecheap_user: Optional[str] = None
    dns_namecheap_api: Optional[str] = None
    dns_namecheap_sourceip: Optional[str] = None
    dns_namecom_user: Optional[str] = None
    dns_namecom_token: Optional[str] = None
    dns_namesilo_key: Optional[str] = None
    dns_nederhost_key: Optional[str] = None
    dns_netcup_cid: Optional[str] = None
    dns_netcup_key: Optional[str] = None
    dns_netcup_pw: Optional[str] = None
    dns_njalla_token: Optional[str] = None
    dns_nsone_key: Optional[str] = None
    dns_nsupdate_server: Optional[str] = None
    dns_nsupdate_zone: Optional[str] = None
    dns_nsupdate_key: Optional[str] = None
    dns_oci_cli_user: Optional[str] = None
    dns_oci_cli_tenancy: Optional[str] = None
    dns_oci_cli_region: Optional[str] = None
    dns_oci_cli_key: Optional[str] = None
    dns_online_key: Optional[str] = None
    dns_opnsense_host: str = Field(default="localhost")
    dns_opnsense_port: str = Field(default="443")
    dns_opnsense_key: Optional[str] = None
    dns_opnsense_token: Optional[str] = None
    dns_opnsense_insecure: bool = Field(default=False)
    dns_ovh_app_key: Optional[str] = None
    dns_ovh_app_secret: Optional[str] = None
    dns_ovh_consumer_key: Optional[str] = None
    dns_ovh_endpoint: Optional[str] = None
    dns_pleskxml_user: Optional[str] = None
    dns_pleskxml_pass: Optional[str] = None
    dns_pleskxml_uri: Optional[str] = None
    dns_pdns_url: Optional[str] = None
    dns_pdns_serverid: Optional[str] = None
    dns_pdns_token: Optional[str] = None
    dns_porkbun_key: Optional[str] = None
    dns_porkbun_secret: Optional[str] = None
    dns_sl_key: Optional[str] = None
    dns_sl_apiver: Optional[ValidationsValidationDnsSlApiverEnum] = None
    dns_sl_token_lifetime: Optional[str] = None
    dns_sl_account_id: Optional[str] = None
    dns_sl_project_name: Optional[str] = None
    dns_sl_login_name: Optional[str] = None
    dns_sl_password: Optional[str] = None
    dns_selfhost_user: Optional[str] = None
    dns_selfhost_password: Optional[str] = None
    dns_selfhost_map: Optional[str] = None
    dns_servercow_username: Optional[str] = None
    dns_servercow_password: Optional[str] = None
    dns_simply_api_key: Optional[str] = None
    dns_simply_account_name: Optional[str] = None
    dns_transip_username: Optional[str] = None
    dns_transip_key: Optional[str] = None
    dns_udr_user: Optional[str] = None
    dns_udr_password: Optional[str] = None
    dns_uno_key: Optional[str] = None
    dns_uno_user: Optional[str] = None
    dns_vscale_key: Optional[str] = None
    dns_vultr_key: Optional[str] = None
    dns_yandex_token: Optional[str] = None
    dns_zilore_key: Optional[str] = None
    dns_zm_key: Optional[str] = None
    dns_gdnsdk_user: Optional[str] = None
    dns_gdnsdk_password: Optional[str] = None
    dns_acmedns_user: Optional[str] = None
    dns_acmedns_password: Optional[str] = None
    dns_acmedns_subdomain: Optional[str] = None
    dns_acmedns_updateurl: Optional[str] = None
    dns_acmedns_baseurl: Optional[str] = None
    dns_acmeproxy_endpoint: Optional[str] = None
    dns_acmeproxy_username: Optional[str] = None
    dns_acmeproxy_password: Optional[str] = None
    dns_variomedia_key: Optional[str] = None
    dns_schlundtech_user: Optional[str] = None
    dns_schlundtech_password: Optional[str] = None
    dns_easydns_apitoken: Optional[str] = None
    dns_easydns_apikey: Optional[str] = None
    dns_euserv_user: Optional[str] = None
    dns_euserv_password: Optional[str] = None
    dns_leaseweb_key: Optional[str] = None
    dns_cn_user: Optional[str] = None
    dns_cn_password: Optional[str] = None
    dns_arvan_token: Optional[str] = None
    dns_artfiles_username: Optional[str] = None
    dns_artfiles_password: Optional[str] = None
    dns_hetzner_token: Optional[str] = None
    dns_hetznercloud_token: Optional[str] = None
    dns_hexonet_login: Optional[str] = None
    dns_hexonet_password: Optional[str] = None
    dns_1984hosting_user: Optional[str] = None
    dns_1984hosting_password: Optional[str] = None
    dns_kas_login: Optional[str] = None
    dns_kas_authdata: Optional[str] = None
    dns_kas_authtype: ValidationsValidationDnsKasAuthtypeEnum = Field(default=ValidationsValidationDnsKasAuthtypeEnum.PLAIN)
    dns_desec_token: Optional[str] = None
    dns_desec_name: Optional[str] = None
    dns_infomaniak_token: Optional[str] = None
    dns_zone_username: Optional[str] = None
    dns_zone_key: Optional[str] = None
    dns_dynv6_token: Optional[str] = None
    dns_cpanel_user: Optional[str] = None
    dns_cpanel_token: Optional[str] = None
    dns_cpanel_hostname: Optional[str] = None
    dns_regru_username: Optional[str] = None
    dns_regru_password: Optional[str] = None
    dns_nic_username: Optional[str] = None
    dns_nic_password: Optional[str] = None
    dns_nic_client: Optional[str] = None
    dns_nic_secret: Optional[str] = None
    dns_websupport_api_key: Optional[str] = None
    dns_websupport_api_secret: Optional[str] = None
    dns_world4you_username: Optional[str] = None
    dns_world4you_password: Optional[str] = None
    dns_aurora_key: Optional[str] = None
    dns_aurora_secret: Optional[str] = None
    dns_conoha_user: Optional[str] = None
    dns_conoha_password: Optional[str] = None
    dns_conoha_tenantid: Optional[str] = None
    dns_conoha_idapi: str = Field(default="https://identity.xxxx.conoha.io/v2.0")
    dns_constellix_key: Optional[str] = None
    dns_constellix_secret: Optional[str] = None
    dns_exoscale_key: Optional[str] = None
    dns_exoscale_secret: Optional[str] = None
    dns_internetbs_key: Optional[str] = None
    dns_internetbs_password: Optional[str] = None
    dns_pointhq_key: Optional[str] = None
    dns_pointhq_email: Optional[str] = None
    dns_rackspace_user: Optional[str] = None
    dns_rackspace_key: Optional[str] = None
    dns_rage4_token: Optional[str] = None
    dns_rage4_user: Optional[str] = None
    dns_mijnhost_api_key: Optional[str] = None
    dns_scaleway_token: Optional[str] = None
    dns_zoneedit_id: Optional[str] = None
    dns_zoneedit_token: Optional[str] = None

