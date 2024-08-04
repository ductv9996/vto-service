from pydantic import BaseModel
from typing import Optional

class ImageData(BaseModel):
    cameraFacing: str
    fileType: str
    scanType: str
    bucket: str
    fileName: str
    generation: str
    timeCreated: str
    updated: str
    size: int
    downloadTokens: str
    contentType: str
    cameraInfo: Optional[str] = None

class BodyData(BaseModel):
    front: ImageData

class FaceData(BaseModel):
    front: ImageData
    right: ImageData
    left: ImageData

class UserBody(BaseModel):
    userId: str
    gender: str
    height: float
    weight: float
    body: BodyData

class UserFace(BaseModel):
    userId: str
    gender: str
    height: float
    weight: float
    face: FaceData

class MockBody(BaseModel):
    param: str