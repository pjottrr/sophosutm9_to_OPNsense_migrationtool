from typing import List
from pydantic import BaseModel
from pysense.pydantic.ProductCheck import ProductCheck


class Product(BaseModel):
    product_abi: str
    product_arch: str
    product_check: ProductCheck
    product_conflicts: str
    product_copyright_owner: str
    product_copyright_url: str
    product_copyright_years: str
    product_email: str
    product_hash: str
    product_id: str
    product_latest: str
    product_license: List[str]
    product_log: int
    product_mirror: str
    product_name: str
    product_nickname: str
    product_repos: str
    product_series: str
    product_tier: str
    product_time: str
    product_version: str
    product_website: str
