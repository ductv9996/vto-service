import time
from datetime import datetime
from apps_multiple.models import UserFace, UserBody

def face_data_parser(request: UserFace):
    start_time = time.time()
    stimestamp = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
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
                front = face_front,
                right = face_left,
                left = face_right
                )
    return output

def body_data_parser(request: UserBody):
    start_time = time.time()
    stimestamp = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    body = {}
    body['token'] = request.body.front.downloadTokens
    body['bucket'] = request.body.front.bucket
    body['fname'] = request.body.front.fileName

    output = dict(
                start_time=stimestamp, 
                gender=request.gender,
                user_height = request.height,
                user_weight = request.weight,
                user_id = request.userId,
                body = body,
                )
    return output