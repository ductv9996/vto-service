from pipeline import HairReconsPipeline
import cv2

path = '/home/thinkpro/try-on-ai-ml-avatar/static/test.jpg'
image = cv2.imread(path)#[:, :, ::-1]
processor = HairReconsPipeline()
reconstructed = processor.run_pipeline(image, user_id='444449mockupxsasds323233')