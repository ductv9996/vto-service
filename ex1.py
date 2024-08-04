from pipeline import AvatarPipeline
# import cv2

# path = '/media/duc/New Volume/Ductv14/VTO_Out/Project/try-on-ai-ml-avatar/HairStepInfer/examples/results/real_imgs/img/0d285f5be7fa09c3dbbf1c9334047888.png'
# image = cv2.imread(path)#[:, :, ::-1]
# processor = HairReconsPipeline()
# reconstructed = processor.run_pipeline(image, user_id='444449mockupxsasds323233')
import cv2

dir_path = "body_head_recovery/data/inputs_3view"
name = "Vit"
gender = "male"
height_m = 1.67
weight_kg = 67.0

body_image_f = cv2.imread(f"body_head_recovery/data/inputs/body/Vit.jpeg")
front_image = cv2.imread(f"{dir_path}/{name}/front.jpg")
right_image = cv2.imread(f"{dir_path}/{name}/right.jpg")
left_image = cv2.imread(f"{dir_path}/{name}/left.jpg")
images = {}
images["body"] = body_image_f
images["front"] = front_image
images["left"] = left_image
images["right"] = right_image
aa = AvatarPipeline()
aa.run_avatar(user_id="Vit", gender="male", height=1.7, weight=67., images=images)
