import sys
import os
sys.path.insert(0, os.path.realpath(os.path.pardir))
sys.path.insert(0, os.path.join(os.getcwd(), 'apps_multiple'))
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from worker_multiple.tasks import head_generation, body_generation
from apps_multiple.api_utils import face_data_parser, body_data_parser
import logging

from datetime import datetime
from apps_multiple.logging_config import logging_config
from apps_multiple.models import UserBody, UserFace

# Set up the logger
logger = logging.getLogger(__name__)
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

# http://34.142.153.115:8888/api/processFaceScan
# http://34.142.153.115:8888/api/processBodyScan

@app.post('/api/processFaceScan')
async def process_face(request: UserFace):
    d = {}
    data = face_data_parser(request=request)
    try:
        task_id = head_generation.delay(data)
        d['task_id'] = data['user_id']#str(task_id)
        d['status'] = 'PROCESSING'
        logger.info(f"head processing on user ID {data['user_id']}")
        logger.info(f'head processing on task ID {task_id}')
        return JSONResponse(status_code=202, content=d)
    
    except Exception as ex:
        logger.info(f"head failure on user ID {data['user_id']}")
        logger.info(ex)
        d['task_id'] = data['user_id']
        d['status'] = 'ERROR'
        return JSONResponse(status_code=400, content=d)
    
@app.post('/api/processBodyScan')
async def process_body(request: UserBody):
    d = {}
    data = body_data_parser(request=request)
    try:
        task_id = body_generation.delay(data)
        d['task_id'] = data['user_id']#str(task_id)
        d['status'] = 'PROCESSING'
        logger.info(f"body processing on user ID {data['user_id']}")
        logger.info(f'body processing on task ID {task_id}')
        return JSONResponse(status_code=202, content=d)
    
    except Exception as ex:
        logger.info(f"body failure on user ID {data['user_id']}")
        logger.info(ex)
        d['task_id'] = data['user_id']
        d['status'] = 'ERROR'
        return JSONResponse(status_code=400, content=d)