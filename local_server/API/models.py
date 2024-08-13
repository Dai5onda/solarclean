from pydantic import BaseModel

class ImageModel(BaseModel):
    id: int
    original_path: str
    processed_path: str
    status: str
