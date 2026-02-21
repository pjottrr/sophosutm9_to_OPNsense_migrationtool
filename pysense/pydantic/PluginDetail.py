from pydantic import BaseModel


class PluginDetail(BaseModel):
    details: str