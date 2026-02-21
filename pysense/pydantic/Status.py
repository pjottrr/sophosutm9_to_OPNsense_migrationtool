from typing import Optional, Literal
from pydantic import BaseModel


class Status(BaseModel):
    status: Literal['ok', 'failure']
    msg_uuid: Optional[str] = None