import cv2
import numpy as np
import os
import json
#Anaconda3-2024.06-1-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh
from body_head_recovery.full_body_reconstruction import *
from HairStepInfer.inference import HairReconsPipeline

class AvatarPipeline():
    def __init__(self) -> None:
        self.DATA_ROOT = './static'
        self.hair_reconstructor = HairReconsPipeline()

    def run_hair(self, images, user_id):
        image = images['front']
        result = self.hair_reconstructor.run_pipeline(image, user_id=user_id)
        return result

    def run_avatar(self, user_id: str, gender: str, 
                        height: float, weight: float, 
                        images: dict, path_to_ply: str=''):
        assert len(images) == 4
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
        result_dict = self.run_hair(images, user_id=user_id)
        #override path to ply
        path_to_ply = result_dict['ply_path']# = ply_path
        print(f'>> hair reconstructed with ply file saved in {path_to_ply}')
        body_verts, measurement = body_from_image_params(gender=gender, 
                                                         body_image_f=images['body'],
                                                         height_m=height, 
                                                         weight_kg=weight)
        
        """merger_body_head
        Input:
            gender :string
            body_verts: tensor Nx3. 
            image_f,image_r,image_l : numpy array uint8(opencv image)
        Output:
            body_head_verts: tensor Nx3. 
            final_texture: numpy array uint8(opencv image)

        """
        body_head_verts, final_texture = merger_body_head(gender=gender, 
                                                          body_verts=body_verts,
                                                        image_f=images['front'], 
                                                        image_r=images['left'], 
                                                        image_l=images['right'])
        # hair_input_path="body_head_recovery/data/inputs/hair/225fccd3.ply"
        assert os.path.isfile(path_to_ply)
        save = os.path.join(self.DATA_ROOT, user_id, 'avatar')
        os.makedirs(save, exist_ok=True)
        avatar_output_path = os.path.join(save, 'avatar.glb')#"temp/avatar.glb"
        merger_body_hair(body_head_verts=body_head_verts, 
                        texture=final_texture,
                        hair_input_path=path_to_ply,
                        avatar_output_path=avatar_output_path)
        return avatar_output_path, measurement


class HeadPipeline():
    def __init__(self) -> None:
        self.hair_reconstructor = HairReconsPipeline()
        self.DATA_ROOT = './static'

    def run(self, gender, userId, image_f, image_r, image_l, **kwargs):
        """
        return:
            path to the head 3D model
        default:
            static/%userId/head/*.
        """
        #todo: run hair reconstruction
        hair_result = self.hair_reconstructor.run_pipeline(image_f, user_id=userId)
        hair_result_refine = {}

        hair_result_refine['pc_all_valid'] = np.asarray(hair_result['pc_all_valid']).tolist()
        hair_result_refine['lines'] = np.asarray(hair_result['lines']).tolist()
        hair_result_refine['colors'] = np.asarray(hair_result['colors']).tolist()
        #todo: run head reconstruction
        head_verts, complete_texture = run_head(gender, image_f, image_r, image_l)
        
        save = os.path.join(self.DATA_ROOT, userId, 'head')
        os.makedirs(save, exist_ok=True)

        head_verts_path = f"{save}/head_verts.txt"
        complete_texture_path = f"{save}/complete_texture.png"
        hair_result_path = f"{save}/hair_result.json"

        np.savetxt(head_verts_path, head_verts.numpy())
        cv2.imwrite(complete_texture_path, complete_texture)

        json_object = json.dumps(hair_result_refine, indent=4)
        
        # Writing to sample.json
        with open(hair_result_path, "w") as outfile:
            outfile.write(json_object)

        # return head_verts_path, complete_texture_path, hair_result_path
        return save


class BodyPipeline():
    def __init__(self) -> None:
        self.DATA_ROOT = './static'

    def run(self, gender, userId, body_image_f, height_m, weight_kg, **kwargs):
        """
        return: 
            path to the body 3D model
            path to measurement
            path to the others infor
        default:
            static/%userId/body/*.
        """
        body_verts, measurement = body_from_image_params(gender=gender, 
                                                         body_image_f=body_image_f,
                                                         height_m=height_m, 
                                                         weight_kg=weight_kg)
        
        save = os.path.join(self.DATA_ROOT, userId, 'body')
        os.makedirs(save, exist_ok=True)

        body_verts_path = f"{save}/body_verts.txt"
        measurement_path = f"{save}/measurement.json"

        np.savetxt(body_verts_path, body_verts.numpy())
        # Serializing json
        json_object = json.dumps(measurement, indent=4)
        
        # Writing to sample.json
        with open(measurement_path, "w") as outfile:
            outfile.write(json_object)

        # return body_verts_path, measurement_path
        return save


class AvatarMerging():
    def __init__(self) -> None:
        self.DATA_ROOT = './static'

    def run(self, body_verts_path, head_verts_path, complete_texture_path, hair_result_path, **kwargs):
        """
        return:
            path to the avatar 3D model
        default:
            static/%userId/avatar/*.
        """
        body_verts = np.loadtxt(body_verts_path)
        head_verts = np.loadtxt(head_verts_path)
        complete_texture = cv2.imread(complete_texture_path)
        # Opening JSON file
        with open(hair_result_path, 'r') as openfile:
            # Reading from json file
            hair_result = json.load(openfile)

        #todo: merge body -> head
        body_head_verts = merger_body_head(body_verts=body_verts, head_verts=head_verts)

        #todo: merge hair -> avatar
        save = os.path.join(self.DATA_ROOT, userId, 'avatar')
        os.makedirs(save, exist_ok=True)
        avatar_output_path = os.path.join(save, 'avatar.glb')#"temp/avatar.glb"
        merger_body_hair(body_head_verts, complete_texture, hair_result, avatar_output_path)

        save = os.path.join(self.DATA_ROOT, userId, 'avatar')
        os.makedirs(save, exist_ok=True)
        avatar_output_path = os.path.join(save, 'avatar.glb')#"temp/avatar.glb"

        os.system(f"docker run --name convert_usdz -v {save}:/tmp vto/convert")
        os.system(f"docker cp convert_usdz:/tmp/avatar.usdz {save}/avatar.usdz")
        os.system("docker rm convert_usdz")

        avatar_usdz_path = os.path.join(save, 'avatar.usdz')#"temp/avatar.glb"

        return avatar_usdz_path

# processor = AvatarPipeline()

head = HeadPipeline()
body = BodyPipeline()
merger = AvatarMerging()

dir_path = "body_head_recovery/data/inputs_3view"
name = "Vit"
gender = "male"
height_m = 1.67
weight_kg = 67.0
userId = "Vit"

body_image_f = cv2.imread(f"body_head_recovery/data/inputs/body/Vit.jpeg")
front_image = cv2.imread(f"{dir_path}/{name}/front.jpg")
right_image = cv2.imread(f"{dir_path}/{name}/right.jpg")
left_image = cv2.imread(f"{dir_path}/{name}/left.jpg")
images = {}
images["body"] = body_image_f
images["front"] = front_image
images["left"] = left_image
images["right"] = right_image

body_model_path = body.run(gender=gender, userId=userId, body_image_f=body_image_f, height_m=height_m, weight_kg=weight_kg)
face_model_path = head.run(gender=gender, userId=userId, image_f=front_image, image_r=right_image, image_l=left_image)

head_verts_path = os.path.join(face_model_path, 'head_verts.txt')
complete_texture_path = os.path.join(face_model_path, 'complete_texture.png')
hair_result_path = os.path.join(face_model_path, 'hair_result.json')
measurement_path = os.path.join(body_model_path, 'measurement.json')
body_verts_path = os.path.join(body_model_path, 'body_verts.txt')
avatar_output_path = merger.run(body_verts_path, head_verts_path, complete_texture_path, hair_result_path)
