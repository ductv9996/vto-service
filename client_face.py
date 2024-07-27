import requests
import json
import cv2
from HairStepInfer.lib.utils import image_to_str

url = "http://34.142.153.115:8888/api/process"
# path = '/home/thinkpro/try-on-ai-ml-avatar/HairStepInfer/examples/results/real_imgs/img/29dc6387017754215b532130750e2370.png'
# image = cv2.imread(path)#[:, :, ::-1]
# idata = image_to_str(image)
payload = json.dumps({
                        "userId": "000010-fb0c-4cdb-9986-595d3014eb92",
                        "gender": "female",
                        "height": 170,
                        "weight": 65.5,
                        "body": {
                                "front": {
                                "cameraFacing": "front",
                                "fileType": "photo",
                                "scanType": "body",
                                "bucket": "vtry-on-phase-1.appspot.com",
                                "fileName": "/input-body/Vit-body-front.jpg",
                                "generation": "1719675003924679",
                                "timeCreated": "2024-06-29T15:30:03.927Z",
                                "updated": "2024-06-29T15:30:03.927Z",
                                "size": 1790440,
                                "downloadTokens": "ed4b1723-eb43-4c66-9e96-ad30abfdb314",
                                "contentType": "image/jpeg",
                                "cameraInfo": "none"
                                }
                        },
                        "face": {
                        "front": {
                        "cameraFacing": "front",
                        "fileType": "photo",
                        "scanType": "body",
                        "bucket": "vtry-on-phase-1.appspot.com",
                                        "fileName": "/input-face/Vit-face-front.jpg",
                        "generation": "1719675003924679",
                        "timeCreated": "2024-06-29T15:30:03.927Z",
                        "updated": "2024-06-29T15:30:03.927Z",
                        "size": 1790440,
                        "downloadTokens": "ed4b1723-eb43-4c66-9e96-ad30abfdb314",
                        "contentType": "image/jpeg",
                        "cameraInfo": "none"
                        },
                        "right": {
                        "cameraFacing": "front",
                        "fileType": "photo",
                        "scanType": "body",
                        "bucket": "vtry-on-phase-1.appspot.com",
                                        "fileName": "/input-face/Vit-face-right.jpg",

                        "generation": "1719675003924679",
                        "timeCreated": "2024-06-29T15:30:03.927Z",
                        "updated": "2024-06-29T15:30:03.927Z",
                        "size": 1790440,
                        "downloadTokens": "ed4b1723-eb43-4c66-9e96-ad30abfdb314",
                        "contentType": "image/jpeg",
                        "cameraInfo": "none"
                        },
                        "left": {
                        "cameraFacing": "front",
                        "fileType": "photo",
                        "scanType": "body",
                        "bucket": "vtry-on-phase-1.appspot.com",
                                        "fileName": "/input-face/Vit-face-left.jpg",
                        "generation": "1719675003924679",
                        "timeCreated": "2024-06-29T15:30:03.927Z",
                        "updated": "2024-06-29T15:30:03.927Z",
                        "size": 1790440,
                        "downloadTokens": "ed4b1723-eb43-4c66-9e96-ad30abfdb314",
                        "contentType": "image/jpeg",
                        "cameraInfo": "none"
                        }
                        }
                        }
                        )
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
