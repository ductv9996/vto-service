# import numpy as np
# import torch
# import shutil
# import json
# import requests
import cv2
from lib.utils import png_to_str, _grab_image, gcloud_storage_download, gcloud_storage_upload
from fastapi import FastAPI, File, Form, UploadFile, status
from datetime import datetime
import time
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging.config
# import sys
from lib.utils import remove_directory
content_keys = [
    "userId",
    "avatarId",
    "fileName",
    "bucket",
    "generation",
    "contentType",
    "uploadedCreatedAt",
    "uploadedUpdateAt",
    "size",
    "downloadTokens",
    "bodyMeasurement"
]
ROOT = './static'
GSTORAGE = 'vtry-on-phase-1.appspot.com/output-avatar'
if not os.path.exists("logs"):
    os.mkdir("logs")

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()
app = FastAPI()
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:5173",
# ]


app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
# static_path = os.path.join(os.getcwd(), 'static')

from fastapi import FastAPI
from models import ScanFacePhotosRequest

def body_from_image_params(gender, 
                            body_image_f, 
                            height_m, 
                            weight_kg):
    """body_from_image_params
        Input: 
            gender :string
            body_image_f: numpy array uint8(opencv image)
            height_m: float32 
            weight_kg: float32
        Output:
            body_verts: tensor Nx3. 
            measurement: json object 
        """
    body_verts, measurement = None, None
    return body_verts, measurement

def merger_body_head(gender, 
                    body_verts,
                    image_f, 
                    image_r, 
                    image_l):
    """merger_body_head
        Input:
            gender :string
            body_verts: tensor Nx3. 
            image_f,image_r,image_l : numpy array uint8(opencv image)
        Output:
            body_head_verts: tensor Nx3. 
            final_texture: numpy array uint8(opencv image)
        """
    body_head_verts, final_texture = None, None
    return body_head_verts, final_texture

def merger_body_hair(body_verts, 
                    texture,
                    hair_input_path,
                    avatar_output_path):
    """
    hair_input_path: path to ply
    avatar_output_path: glb store destination
    """
    return # store the .glb file to cache and upload to gcloud

app = FastAPI()

#receive the mess from mobile side
#download the image
#generate the avatar as an .obj file
#upload to google cloud storage
@app.post("/service/aiml/avatar/scanFacePhotos")
async def scan_photos(request: ScanFacePhotosRequest):
    start_time = time.time()
    stimestamp = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    # Extract data from the request
    user_gender = request.gender
    user_height = request.height
    user_weight = request.weight
    user_id = request.userId

    # scan_type = request.scanType
    # camera_facing = request.cameraFacing
    # file_type = request.fileType

    body = request.body
    front = request.front
    right = request.right
    left = request.left

    tags = ['body', 'left', 'right', 'front']
    images = []
    for idx, data in enumerate([body, left, right, front]):
        token = data.downloadTokens
        bucket = data.bucket
        fname = data.fileName
        ipath = os.path.join(ROOT, f'{user_id}', 'images')
        os.makedirs(ipath, exist_ok=True)
        dest = os.path.join(ipath, f'{tags[idx]}.jpg')

        gcloud_storage_download(token=token, 
                                bucket_name=bucket, 
                                file_name=fname, 
                                output_file_name=dest)

        arr = cv2.imread(dest)
        images.append(arr)
    assert len(images) == 4
    
    avatar_output_path = run_avatar(images, user_gender, 
                                    user_height, user_weight, 
                                    user_id)
    end_time = time.time()
    etimestamp = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    objfilename = f'{user_id}_{etimestamp}_avatar.glb'
    gcloud_storage_upload(GSTORAGE, avatar_output_path, objfilename)
    #todo: remove cache when file upload completed
    #remove_directory(os.path.join(ROOT, f'{user_id}'))
    response = {
                "userId": user_id,
                "avatarId": 'null',
                "avatarStatus": "COMPLETED",
                "fileName": objfilename,
                "bucket": GSTORAGE,
                "generation": "1719675003924679",
                "contentType": "sample/obj",
                "uploadedCreatedAt": stimestamp,
                "uploadedUpdateAt": etimestamp,
                "size": "1790440",
                "downloadTokens": "null",
                "bodyMeasurement": 'null'
                }
    # Respond with a success message
    return response

def run_avatar(images, user_gender, user_height, user_weight, user_id):
    body_verts, measurement = body_from_image_params(gender=user_gender, 
                                                     body_image_f=images[0],
                                                     height_m=user_height,
                                                     weight_kg=user_weight)
    body_head_verts, final_texture = merger_body_head(gender=user_gender,
                                                      body_verts=body_verts,
                                                      image_f=images[-1],
                                                      image_l=images[1],
                                                      image_r=images[2])
    #todo: run hair reconstruction here
    hair_input_path = os.path.join(ROOT, f'{user_id}', 'ply', 'hair.ply')
    apath = os.path.join(ROOT, f'{user_id}', 'glb')
    os.makedirs(apath, exist_ok=True)
    avatar_output_path = os.path.join(apath, 'final.glb')
    merger_body_hair(body_verts=body_head_verts, 
                    texture=final_texture,
                    hair_input_path=hair_input_path,
                    avatar_output_path=avatar_output_path)
    return avatar_output_path

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

