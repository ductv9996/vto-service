import logging
from celery import Task
from celery.exceptions import MaxRetriesExceededError
from celery.signals import task_success
from datetime import datetime
from worker.worker import app
import sys
import os
import time
import cv2
import requests
import json
import sys
from HairStepInfer.lib.utils import png_to_str, _grab_image
from HairStepInfer.lib.utils import gcloud_storage_download, gcloud_storage_upload
from HairStepInfer.lib.utils import remove_directory
from HairStepInfer.lib.utils import base64_to_image
from apps.logging_config import logging_config

# Set up the logger
logger = logging.getLogger(__name__)
from pipeline import AvatarPipeline

sys.path.insert(0, os.path.split(os.getcwd())[0])
ROOT_DATA = os.path.join(os.getcwd(), 'static')
print(f'>> running on cache storage {ROOT_DATA}')
TAGS = ['body', 'front', 'right', 'left']
credentials = os.path.join(os.getcwd(), 'HairStepInfer/lib/gcloud_token.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


class PredictTask(Task):
    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        if not self.model:
            logger.info('Loading Model...')
            self.model = AvatarPipeline()
            logger.info('Model loaded')
        return self.run(*args, **kwargs)


@app.task(ignore_result=False, bind=True, base=PredictTask)
def predict_image(self, data: dict):
    # try:
        user_id = data['user_id']
        gender = data['gender']
        height = float(data['user_height']) / 100.
        weight = float(data['user_weight'])
        images = {}
        GSTORAGE = data['front']['bucket']
        for t in TAGS:
            tag = t
            token = data[t]['token']
            bucket = data[t]['bucket']
            fname = data[t]['fname']
            image = gcloud_downloader(user_id, tag, token, bucket, fname)
            images[t] = image
        # mock_image = base64_to_image(data['mock_image'])
        
        data_pred, measurement = self.model.run_avatar(user_id, gender, height, weight, images)
        measurement['height'] = height
        measurement['weight'] = weight

        logger.info('put the task into job queue')
        return {'status': 'SUCCESS', 
                'result': {'data_pred': data_pred, 
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

@task_success.connect(sender=predict_image)
def task_success_handler(sender=None, result=None, **kwargs):
    end_time = time.time()
    etimestamp = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    # print(os.path.split(os.getcwd())[0])
    print(result['result']['data_pred'])
    avatar_output_path = os.path.join(os.path.split(os.getcwd())[0], 'vto-service', result['result']['data_pred'][2:])
    objfilename = f"output-avatar/{result['result']['user_id']}_{etimestamp}.glb"
    gcloud_storage_upload(result['result']['GSTORAGE'], avatar_output_path, objfilename)
    
    # response = {
    #             "userId": result['result']['user_id'],
    #             "avatarId": 'null',
    #             "avatarStatus": "COMPLETED",
    #             "fileName": objfilename,
    #             "bucket": result['result']['GSTORAGE'],
    #             "generation": "1719675003924679",
    #             "contentType": "sample/obj",
    #             "uploadedCreatedAt": result['result']['start_time'],
    #             "uploadedUpdateAt": etimestamp,
    #             "size": "1790440",
    #             "downloadTokens": "ed4b1723-eb43-4c66-9e96-ad30abfdb314",
    #             "bodyMeasurement": 'null'
    #             }
    """
    measurement['arm_length']
    measurement['bicep_circumference']
    measurement['forearm_circumference']
    measurement['wrist_circumference']
    measurement['neck_circumference']
    measurement['head_circumference']
    measurement['chest_circumference']
    measurement['waist_circumference']
    measurement['pelvis_circumference']
    measurement['thigh_circumference']
    measurement['calf_circumference']
    measurement['ankle_circumference']
    """
    measurement = result['result']['measurement']
    response = {
                "userId": result['result']['user_id'],
                "avatarId": None,
                "avatarStatus": "COMPLETED",
                "fileName": objfilename,
                "bucket": result['result']['GSTORAGE'],
                "generation": "1719675003924679",
                "contentType": "sample/obj",
                "uploadedCreatedAt": result['result']['start_time'],
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
                    "shoulderBreadth": measurement['shoulder_breadth'],
                    }
                    }

    url = "https://vft-core-v1-0-b7eqrlfuiq-as.a.run.app:443/ai-ml/avatar/statusUpdate"
    payload = json.dumps(response)
    headers = {
                'Content-Type': 'application/json'
                }
    response = requests.request("POST", url, headers=headers, data=payload)
    # Print the response status code
    logger.info(f"user id {result['result']['user_id']} updated with {response.status_code}")
    print("Status Code:", response.status_code)
    # Print the response headers
    print("Headers:", response.headers)
    # Print the response text (content)
    print("Response Text:", response.text)
    # Print the response JSON (if any)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response content is not in JSON format")
    #todo: remove cache when file upload completed
    #remove_directory(os.path.join(ROOT, f'{user_id}'))

def gcloud_downloader(user_id, tag, token, bucket, fname):
    ipath = os.path.join(ROOT_DATA, f'{user_id}', 'images')
    os.makedirs(ipath, exist_ok=True)
    dest = os.path.join(ipath, f'{tag}.jpg')
    fname = fname[1:] if fname[0] == '/' else fname
    gcloud_storage_download(
                            bucket_name=bucket,
                            source_blob_name=fname,
                            destination_file_name=dest)
    # gcloud_storage_download_v1(token=token,
    #                            bucket_name=bucket,
    #                            file_name=fname,
    #                            output_file_name=dest)
    arr = cv2.imread(dest)
    return arr