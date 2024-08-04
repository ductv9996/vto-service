from worker_multiple.worker import app
import logging
from celery import Task
# from celery.exceptions import MaxRetriesExceededError
from celery.signals import task_success
from datetime import datetime
import sys
import os
import time
import cv2
import requests
import json
import sys
from HairStepInfer.lib.utils import gcloud_storage_download, gcloud_storage_upload
from HairStepInfer.lib.utils import remove_directory
from apps.logging_config import logging_config
from db_table import AvatarStatusHandler

# Set up the logger
logger = logging.getLogger(__name__)
from pipeline import HeadPipeline, BodyPipeline, AvatarMerging

sys.path.insert(0, os.path.split(os.getcwd())[0])
ROOT_DATA = os.path.join(os.getcwd(), 'static')
print(f'>> running on cache storage {ROOT_DATA}')
TAGS_BODY = ['body']
TAGS_HEAD = ['front', 'left', 'right']
credentials = os.path.join(os.getcwd(), 'HairStepInfer/lib/gcloud_token.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
GSTORAGE = 'vtry-on-phase-1.appspot.com'
GCP_UPDATE_URL = "https://vft-core-v1-0-b7eqrlfuiq-as.a.run.app:443/ai-ml/avatar/statusUpdate"
status_handler = AvatarStatusHandler()

def gcloud_downloader(user_id, tag, token, bucket, fname):
    ipath = os.path.join(ROOT_DATA, f'{user_id}', 'images')
    os.makedirs(ipath, exist_ok=True)
    dest = os.path.join(ipath, f'{tag}.jpg')
    fname = fname[1:] if fname[0] == '/' else fname
    gcloud_storage_download(
                            bucket_name=bucket,
                            source_blob_name=fname,
                            destination_file_name=dest)
    arr = cv2.imread(dest)
    return arr

def data_prepare(data, tags):
    user_id = data['user_id']
    gender = data['gender']
    height = float(data['user_height']) / 100.
    weight = float(data['user_weight'])
    images = {}
    GSTORAGE = data['front']['bucket']
    for t in tags:
        tag = t
        token = data[t]['token']
        bucket = data[t]['bucket']
        fname = data[t]['fname']
        image = gcloud_downloader(user_id, tag, token, bucket, fname)
        images[t] = image
    
    return user_id, gender, height, weight, images, GSTORAGE

def body_params_reader(path_to_params):
    #todo: data getter write here
    with open(path_to_params) as f:
        measure_json = json.load(f)
    return measure_json

class HeadTask(Task):
    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        if not self.model:
            logger.info('Loading Model...')
            self.model = HeadPipeline()
            logger.info('Model loaded')
        return self.run(*args, **kwargs)

class BodyTask(Task):
    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        if not self.model:
            logger.info('Loading Model...')
            self.model = BodyPipeline()
            logger.info('Model loaded')
        return self.run(*args, **kwargs)

class AvatarTask(Task):
    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        if not self.model:
            logger.info('Loading Model...')
            self.model = AvatarMerging()
            logger.info('Model loaded')
        return self.run(*args, **kwargs)

@app.task(ignore_result=False, bind=True, base=HeadTask)
def head_generation(self, data: dict):
    # try:
    print(f"Task with param: {data}")
    user_id, gender, height, weight, images, GSTORAGE = data_prepare(tags=TAGS_HEAD)
    # gender, userId, image_f, image_r, image_l
    image_f, image_r, image_l = images['front'], images['left'], images['right']
    head_result_path = self.model.run(gender, user_id, image_f, image_r, image_l)

    logger.info('put the task into job queue')
    return {'status': 'SUCCESS', 
            'result': { 'head_model': head_result_path,
                        'user_id': user_id,
                        'start_time': data['start_time'],
                        'GSTORAGE': GSTORAGE}}
    # except Exception as ex:
    #     try:
    #         self.retry(countdown=2)
    #         logger.info('retrying ... ')
    #     except MaxRetriesExceededError as ex:
    #         logger.info('process failed')
    #         return {'status': 'FAIL', 'result': 'max retried achieved'}

@task_success.connect(sender=head_generation)
def task_success_handler_head(sender=None, result=None, **kwargs):
    end_time = time.time()
    etimestamp = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    root_path = os.path.split(os.getcwd())[0]
    root_path = os.getcwd()
    head_result_path = result['result']['head_model']
    head_model = os.path.join(root_path, 'vto-service', head_result_path[2:])
    id_keys = status_handler.show_table('testtable')
    # userId, faceStatus, faceModelPath, bodyStatus, 
    # bodyModelPath, avatarStatus, avatarPath
    uid = result['result']['user_id']
    if uid not in id_keys:
        data = dict(userId=result['result']['user_id'], faceStatus='yes', faceModelPath=head_model,
                    bodyStatus='null', bodyModelPath='null', avatarStatus='null', avatarPath='null')
        status_handler.insert_data(data)
    else:
        status_handler.update_component(dict(userId = uid, key = 'faceStatus', value = 'yes'))
        status_handler.update_component(dict(userId = uid, key = 'faceModelPath', value = head_model))


@app.task(ignore_result=False, bind=True, base=BodyTask)
def body_generation(self, data: dict):
    # try:
    print(f"Task 2 with param: {data}")
    logger.info('>> Running body generation')
    user_id, gender, height, weight, images, GSTORAGE = data_prepare(tags=TAGS_BODY)
    body_image_f = images['body']
    body_model = self.model.run(gender, user_id, body_image_f, height, weight)
    # read from data_measure: path to save measurement static/%userId/measurement/*.
    return {'status': 'SUCCESS', 
            'result': {'body_model': body_model, 
                        'user_id': user_id,
                        'start_time': data['start_time'],
                        'GSTORAGE': GSTORAGE}}
    # except Exception as ex:
    #     try:
    #         self.retry(countdown=2)
    #         logger.info('retrying ... ')
    #     except MaxRetriesExceededError as ex:
    #         logger.info('process failed')
    #         return {'status': 'FAIL', 'result': 'max retried achieved'}

@task_success.connect(sender=body_generation)
def task_success_handler_body(sender=None, result=None, **kwargs):
    end_time = time.time()
    etimestamp = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    root_path = os.path.split(os.getcwd())[0]
    root_path = os.getcwd()
    body_model = os.path.join(root_path, 'vto-service', result['result']['data_pred'][2:])
    id_keys = status_handler.show_table('testtable')
    # userId, faceStatus, faceModelPath, bodyStatus, 
    # bodyModelPath, avatarStatus, avatarPath
    uid = result['result']['user_id']
    if uid not in id_keys:
        data = dict(userId=result['result']['user_id'], 
                    faceStatus='null', faceModelPath='null',
                    bodyStatus='yes', bodyModelPath=body_model,
                    avatarStatus='null', avatarPath='null')
        status_handler.insert_data(data)
    else:
        status_handler.update_component(dict(userId = uid, key = 'bodyStatus', value = 'yes'))
        status_handler.update_component(dict(userId = uid, key = 'bodyModelPath', value = body_model))

@app.task(ignore_result=False, bind=True, base=AvatarTask)
def avatar_merge_task(self, data: dict):
    # try:
    print(f">> Avatar merging with param: {data}")
    user_id = data['userId']
    face_model_path = data['faceModelPath']
    body_model_path = data['bodyModelPath']

    head_verts_path = os.path.join(face_model_path, 'head_verts.txt')
    complete_texture_path = os.path.join(face_model_path, 'complete_texture.png')
    hair_result_path = os.path.join(face_model_path, 'hair_result.json')
    measurement_path = os.path.join(body_model_path, 'measurement.json')
    body_verts_path = os.path.join(body_model_path, 'body_verts.txt')

    avatar_path = self.model.run(body_verts_path, head_verts_path, complete_texture_path, hair_result_path)
    #todo: get the measurement params
    measurement: dict = body_params_reader(measurement_path)
    return {'status': 'SUCCESS', 
            'result': {'avatar_model': avatar_path, 
                        'user_id': user_id,
                        'start_time': data['start_time'],
                        'GSTORAGE': GSTORAGE,
                        'measurement': measurement}}
    # except Exception as ex:
    #     try:
    #         self.retry(countdown=2)
    #         logger.info('retrying ... ')
    #     except MaxRetriesExceededError as ex:
    #         logger.info('process failed')
    #         return {'status': 'FAIL', 'result': 'max retried achieved'}

@task_success.connect(sender=avatar_merge_task)
def task_success_handler(sender=None, result=None, **kwargs):
    user_id = result['result']['user_id']
    measurement = result['result']['measurement']
    start_time = result['result']['start_time']
    avatar_path = result['result']['avatar_model'][2:]
    gstorage = result['result']['GSTORAGE']
    end_time = time.time()
    etimestamp = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    root_path = os.path.split(os.getcwd())[0]
    root_path = os.getcwd()
    avatar_output_path = os.path.join(root_path, 'vto-service', avatar_path)
    objfilename = f"output-avatar/{user_id}_{etimestamp}.glb"
    gcloud_storage_upload(gstorage, avatar_output_path, objfilename)
    update_gcp_status(user_id, measurement, objfilename, gstorage, 
                      start_time, etimestamp)
    status_handler.update_component(dict(userId = user_id, key = 'avatarStatus', value = 'yes'))
    status_handler.update_component(dict(userId = user_id, key = 'avatarPath', value = avatar_output_path))

def update_gcp_status(user_id, measurement, objfilename, GSTORAGE, 
                      start_time, etimestamp, url=GCP_UPDATE_URL):
    response = {
                "userId": user_id,
                "avatarId": None,
                "avatarStatus": "COMPLETED",
                "fileName": objfilename,
                "bucket": GSTORAGE,
                "generation": "1719675003924679",
                "contentType": "sample/obj",
                "uploadedCreatedAt": start_time,
                "uploadedUpdateAt": etimestamp,
                "size": "1790440",
                "downloadTokens": "ed4b1723-eb43-4c66-9e96-ad30abfdb314",
                "bodyMeasurement": {
                    "weight": measurement['weight'],
                    "height": measurement['height'] * 100,
                    "armLength": measurement['arm_length'],
                    "bicepCircumference": measurement['bicep_circumference'],
                    "forearmCircumference": measurement['forearm_circumference'],
                    "wristCircumference": measurement['wrist_circumference'],
                    "neckCircumference": measurement['neck_circumference'],
                    "headCircumference": measurement['head_circumference'],
                    "chestCircumference": measurement['chest_circumference'],
                    "waistCircumference": measurement['waist_circumference'],
                    "pelvisCircumference": measurement['pelvis_circumference'],
                    "thighCircumference": measurement['thigh_circumference'],
                    "calfCircumference": measurement['calf_circumference'],
                    "ankleCircumference": measurement['ankle_circumference'],
                    "shoulderBreadth": 42
                    }
                    }
    payload = json.dumps(response)
    headers = {
                'Content-Type': 'application/json'
                }
    response = requests.request("POST", url, headers=headers, data=payload)
    logger.info(f"user id {user_id} updated with {response.status_code}")
    print(">> Status Code:", response.status_code)
    #todo: remove cache when file upload completed
    # if response.status_code == 200:
    #     remove_directory(os.path.join(ROOT_DATA, f'{user_id}'))
