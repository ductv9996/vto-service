from pydantic import BaseModel
from typing import Optional


class FileDetail(BaseModel):
    bucket: str
    fileName: str
    generation: str
    contentType: str
    timeCreated: str
    updated: str
    size: str
    downloadTokens: str
    cameraInfo: Optional[str]

class ScanFacePhotosRequest(BaseModel):
    mockedImage: Optional[str]
    height: str
    weight: str
    userId: str
    gender: str
    scanType: str
    cameraFacing: str
    fileType: str
    body: FileDetail
    front: FileDetail
    right: FileDetail
    left: FileDetail

class ImageDetails(BaseModel):
    bucket: str
    fileName: str
    generation: str
    contentType: str
    timeCreated: str
    updated: str
    size: float
    downloadTokens: str
    cameraInfo: str

class Body(BaseModel):
    scanType: str
    cameraFacing: str
    fileType: str
    front: ImageDetails

class Face(BaseModel):
    scanType: str
    cameraFacing: str
    fileType: str
    front: ImageDetails
    right: ImageDetails
    left: ImageDetails

class UserData(BaseModel):
    userId: str
    gender: str
    height: float
    weight: float
    body: Body
    face: Face

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

class UserModel(BaseModel):
    userId: str
    gender: str
    height: float
    weight: float
    body: BodyData
    face: FaceData