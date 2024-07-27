import trimesh
import numpy as np

from body_head_recovery.full_body_reconstruction import *


dir_path = "./inputs_3view"
name = "Vit"
gender = "male"
height_m = 1.67
weight_kg = 67.0

body_image_f = cv2.imread(f"body_head_recovery/data/inputs/body/Vit.jpeg")
front_image = cv2.imread(f"{dir_path}/{name}/front.jpg")
right_image = cv2.imread(f"{dir_path}/{name}/right.jpg")
left_image = cv2.imread(f"{dir_path}/{name}/left.jpg")


body_verts, measurement = body_from_image_params(gender=gender, body_image_f=body_image_f, height_m=height_m, weight_kg=weight_kg)
print(measurement)
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

body_head_verts, final_texture = merger_body_head(gender=gender, body_verts=body_verts,
                                                  image_f=front_image, image_r=right_image, image_l=left_image)
"""merger_body_head
Input:
    gender :string
    body_verts: tensor Nx3. 
    image_f,image_r,image_l : numpy array uint8(opencv image)
Output:
    body_head_verts: tensor Nx3. 
    final_texture: numpy array uint8(opencv image)
"""

hair_input_path= f"body_head_recovery/data/body_temp/hair/{gender}/hair.obj"
avatar_output_path="temp/avatar.glb"

merger_body_hair(body_head_verts=body_head_verts, 
                texture=final_texture,
                hair_input_path=hair_input_path,
                avatar_output_path=avatar_output_path)

os.system(f"docker run --name convert_usdz -v ./temp:/tmp vto/convert")
os.system(f"docker cp convert_usdz:/tmp/avatar.usdz ./temp/avatar.usdz")
os.system("docker rm convert_usdz")

print("Run reconstruction body head Done")