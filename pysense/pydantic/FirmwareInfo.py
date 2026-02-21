from typing import List
from pydantic import BaseModel
from pysense.pydantic.ChangelogItem import ChangelogItem
from pysense.pydantic.Package import Package
from pysense.pydantic.Product import Product


class FirmwareInfo(BaseModel):
    product_id: str
    product_version: str
    package: List[Package]
    changelog: List[ChangelogItem]
    product: Product

    def is_installed(self, package_name: str) -> bool:
        for package in self.package:
            if package.installed == '1':
                return True
        return False
