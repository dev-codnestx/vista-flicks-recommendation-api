from pydantic import BaseModel
from typing import List, Optional

class ReelModel(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    tags: List[str]
