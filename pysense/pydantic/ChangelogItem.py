from pydantic import BaseModel


class ChangelogItem(BaseModel):
    series: str
    version: str
    date: str
