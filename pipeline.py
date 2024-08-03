import numpy as np
import os

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
        # path_to_ply = result_dict['ply_path']# = ply_path
        path_to_ply = f"body_head_recovery/data/body_temp/hair/{gender}/hair.obj"
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
                                                        image_r=images['right'], 
                                                        image_l=images['left'])
        # hair_input_path="body_head_recovery/data/inputs/hair/225fccd3.ply"
        
        assert os.path.isfile(path_to_ply)
        save = os.path.join(self.DATA_ROOT, user_id, 'avatar')
        os.makedirs(save, exist_ok=True)
        avatar_output_path = os.path.join(save, 'avatar.glb')#"temp/avatar.glb"
        merger_body_hair(body_head_verts=body_head_verts, 
                        texture=final_texture,
                        hair_result=result_dict,
                        avatar_output_path=avatar_output_path)
        
        os.system(f"docker run --name convert_usdz -v {save}:/tmp vto/convert")
        os.system(f"docker cp convert_usdz:/tmp/avatar.usdz {save}/avatar.usdz")
        os.system("docker rm convert_usdz")

        avatar_usdz_path = os.path.join(save, 'avatar.usdz')#"temp/avatar.glb"

        return avatar_usdz_path, measurement

# processor = AvatarPipeline()
