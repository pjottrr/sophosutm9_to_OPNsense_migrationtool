from typing import Literal, Optional
from pydantic import BaseModel, UUID4


class BaseObject(BaseModel):
    uuid: UUID4
    # enabled: Optional[Literal['0', '1']] # Validator does not work
    name: str
    description: Optional[str] = ""
