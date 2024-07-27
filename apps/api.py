import sys
import os
sys.path.insert(0, os.path.realpath(os.path.pardir))
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
# from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from worker.tasks import predict_image
import time
# from celery.result import AsyncResult
# from models import Task, Prediction
# import uuid
import logging
# from logging import config
# from pydantic.typing import List
# import numpy as np
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'apps'))
from apps.models import UserData, UserModel
from datetime import datetime
from apps.logging_config import logging_config

# Set up the logger
logger = logging.getLogger(__name__)
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout=60):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Request timeout")

app.add_middleware(TimeoutMiddleware, timeout=1000)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/api/process')
async def process(request: UserModel):
    d = {}
    data = data_parser(request=request)
    try:
        task_id = predict_image.delay(data)
        d['task_id'] = data['user_id']#str(task_id)
        d['status'] = 'PROCESSING'
        logger.info(f"processing on user ID {data['user_id']}")
        logger.info(f'processing on task ID {task_id}')
        return JSONResponse(status_code=202, content=d)
    except Exception as ex:
        logger.info(f"failure on user ID {data['user_id']}")
        logger.info(ex)
        d['task_id'] = data['user_id']
        d['status'] = 'ERROR'
        return JSONResponse(status_code=400, content=d)
    

def data_parser(request: UserModel):
    start_time = time.time()
    stimestamp = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    # meta = [{}]*4
    body = {}
    body['token'] = request.body.front.downloadTokens
    body['bucket'] = request.body.front.bucket
    body['fname'] = request.body.front.fileName

    face_front = {}
    face_front['token'] = request.face.front.downloadTokens
    face_front['bucket'] = request.face.front.bucket
    face_front['fname'] = request.face.front.fileName
    face_left = {}
    face_left['token'] = request.face.left.downloadTokens
    face_left['bucket'] = request.face.left.bucket
    face_left['fname'] = request.face.left.fileName
    face_right = {}
    face_right['token'] = request.face.right.downloadTokens
    face_right['bucket'] = request.face.right.bucket
    face_right['fname'] = request.face.right.fileName

    # print(request.mockedImage)
    output = dict(
                start_time=stimestamp, 
                gender=request.gender,
                user_height = request.height,
                user_weight = request.weight,
                user_id = request.userId,
                body = body,
                front = face_front,
                right = face_left,
                left = face_right
                )
    return output