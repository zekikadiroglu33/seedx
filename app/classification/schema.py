from typing import Literal
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    seed_id: str
    classification: Literal["accept" ,"reject", "pending"] 
    is_sampled: bool
    image_path: str = None