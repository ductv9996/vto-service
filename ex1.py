from pipeline import HairReconsPipeline
import cv2

path = '/media/duc/New Volume/Ductv14/VTO_Out/Project/try-on-ai-ml-avatar/HairStepInfer/examples/results/real_imgs/img/0d285f5be7fa09c3dbbf1c9334047888.png'
image = cv2.imread(path)#[:, :, ::-1]
processor = HairReconsPipeline()
reconstructed = processor.run_pipeline(image, user_id='444449mockupxsasds323233')