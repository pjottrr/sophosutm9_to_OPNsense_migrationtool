from typing import List
from pydantic import BaseModel


class ProductCheck(BaseModel):
    api_version: str
    connection: str
    downgrade_packages: List[str]
    download_size: str
    last_check: str
    needs_reboot: str
    new_packages: List[str]
    os_version: str
    product_id: str
    product_target: str
    product_version: str
    product_abi: str
    reinstall_packages: List[str]
    remove_packages: List[str]
    repository: str
    upgrade_major_message: str
    upgrade_major_version: str
    upgrade_needs_reboot: str
    upgrade_packages: List[str]
    upgrade_sets: List[str]
