from pydantic import BaseModel


class Package(BaseModel):
    name: str
    version: str
    comment: str
    flatsize: str
    locked: str
    automatic: str
    license: str
    repository: str
    origin: str
    provided: str
    installed: str
    path: str
    configured: str