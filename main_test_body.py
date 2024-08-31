# import trimesh
# import numpy as np

# from body_head_recovery.full_body_reconstruction import *


# dir_path = "./inputs_3view"
# name = "Vit"
# gender = "male"
# height_m = 1.67
# weight_kg = 67.0

# body_image_f = cv2.imread(f"body_head_recovery/data/inputs/body/Vit.jpeg")
# front_image = cv2.imread(f"{dir_path}/{name}/front.jpg")
# right_image = cv2.imread(f"{dir_path}/{name}/right.jpg")
# left_image = cv2.imread(f"{dir_path}/{name}/left.jpg")


# body_verts, measurement = body_from_image_params(gender=gender, body_image_f=body_image_f, height_m=height_m, weight_kg=weight_kg)
# print(measurement)
# """body_from_image_params
# Input: 
#     gender :string
#     body_image_f: numpy array uint8(opencv image)
#     height_m: float32 
#     weight_kg: float32
# Output:
#     body_verts: tensor Nx3. 
#     measurement: json object 
# """

# body_head_verts, final_texture = merger_body_head(gender=gender, body_verts=body_verts,
#                                                   image_f=front_image, image_r=right_image, image_l=left_image)
# """merger_body_head
# Input:
#     gender :string
#     body_verts: tensor Nx3. 
#     image_f,image_r,image_l : numpy array uint8(opencv image)
# Output:
#     body_head_verts: tensor Nx3. 
#     final_texture: numpy array uint8(opencv image)
# """

# hair_input_path= f"body_head_recovery/data/body_temp/hair/{gender}/hair.obj"
# avatar_output_path="temp/avatar.glb"

# merger_body_hair(body_head_verts=body_head_verts, 
#                 texture=final_texture,
#                 hair_input_path=hair_input_path,
#                 avatar_output_path=avatar_output_path)

# os.system(f"docker run --name convert_usdz -v ./temp:/tmp vto/convert")
# os.system(f"docker cp convert_usdz:/tmp/avatar.usdz ./temp/avatar.usdz")
# os.system("docker rm convert_usdz")

# print("Run reconstruction body head Done")


import numpy as np

from body_head_recovery.full_body_reconstruction import *


dir_path = "./inputs_3view"
name = "Vit"
gender = "male"
height_m = 1.75
weight_kg = 60.0

body_image_f = cv2.imread(f"body_head_recovery/data/inputs/body/Vit.jpeg")
front_image = cv2.imread(f"{dir_path}/{name}/front.jpg")
right_image = cv2.imread(f"{dir_path}/{name}/right.jpg")
left_image = cv2.imread(f"{dir_path}/{name}/left.jpg")


# body_verts, measurement = body_from_image_params(gender=gender, body_image_f=body_image_f, height_m=height_m, weight_kg=weight_kg)
# print(measurement)
# """body_from_image_params
# Input: 
#     gender :string
#     body_image_f: numpy array uint8(opencv image)
#     height_m: float32 
#     weight_kg: float32
# Output:
#     body_verts: tensor Nx3. 
#     measurement: json object 
# """

# head_verts, complete_texture = run_head(gender, front_image, right_image, left_image)

# cv2.imwrite("complete_texture.png", complete_texture)

# body_head_verts = merger_body_head(body_verts=body_verts, head_verts=head_verts)

# np.savetxt("body_head_verts.txt", body_head_verts.numpy())

from body_head_recovery import config
from mathutils import Vector, Quaternion

def create_human_body(body_verts=None, body_joints=None, cv_body_tex=None):

    model_path = f"body_head_recovery/data/body_temp/{gender}.fbx"

    # flip image corresponds with texture in blender
    texture_cv = np.flipud(cv_body_tex)
    texture_cv = cv2.cvtColor(texture_cv, cv2.COLOR_BGR2RGBA)  # Convert from BGR to RGB

    bpy.ops.import_scene.fbx(filepath=model_path, ignore_leaf_bones=False, global_scale=1.0)
    bpy.ops.object.select_all(action="DESELECT")
    
    fbx = bpy.data.objects[f"SMPLX-{gender}"]
    fbx.select_set(True)
    bpy.context.view_layer.objects.active = fbx

    bpy.ops.object.mode_set(mode="EDIT")

    # update joint location
    
    for index in range(config.NUM_SMPLX_JOINTS):
        bone = fbx.data.edit_bones[config.SMPLX_JOINT_NAMES[index]]
        bone.head = (0.0, 0.0, 0.0)
        bone.tail = (0.0, 0.0, 0.1)

        # Convert SMPL-X joint locations to Blender joint locations
        joint_location_smplx = body_joints[index]
        bone_start = Vector( (joint_location_smplx[0], -joint_location_smplx[2], joint_location_smplx[1]) )
        bone.translate(bone_start)


    # for index in range(config.NUM_SMPLX_JOINTS):
    #     bone = fbx.data.edit_bones[config.SMPLX_JOINT_NAMES[index]]
    #     joint_location_smplx = body_joints[index]
    #     head = [joint_location_smplx[0], -joint_location_smplx[2], joint_location_smplx[1]]
    #     tail = head - np.array(bone.head[:]) + np.array(bone.tail[:])
    #     bone.head = head
    #     bone.tail = tail

    # update vertices location
    v = 0
    for vert in fbx.children[0].data.vertices:
        # vert.co = 100 * body_mesh[v]
        vert.co[0] = body_verts[v][0]
        vert.co[1] = -body_verts[v][2]
        vert.co[2] = body_verts[v][1]
        v = v + 1

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    human_obj = fbx.children[0]
    bpy.context.view_layer.objects.active = human_obj
    ob = bpy.context.view_layer.objects.active

    # Get the existing material (assuming there's only one material on the object)
    material = ob.data.materials[0]

    # Enable 'Use nodes' for the material if not already enabled
    if not material.use_nodes:
        material.use_nodes = True

    # Get the material's node tree
    nodes = material.node_tree.nodes

    # Find the Principled BSDF node
    principled_bsdf = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled_bsdf = node
            break

    if principled_bsdf is None:
        raise Exception("No Principled BSDF shader found in the material")

    # Create a new Image Texture node
    texture_node = nodes.new(type='ShaderNodeTexImage')

    # Create a Blender image and fill it with the OpenCV image data
    image_height, image_width, _ = texture_cv.shape
    texture_image = bpy.data.images.new(name="TextureImage", width=image_width, height=image_height)

    # Flatten the image array and assign it to Blender image pixels
    texture_image.pixels = (texture_cv / 255.0).flatten()
    # Save the Blender image to a file
    texture_image.filepath_raw = "//humanTexture.png"
    texture_image.file_format = 'PNG'
    texture_image.save()

    # Assign the Blender image to the texture node
    texture_node.image = texture_image

    # Link the texture node to the Base Color input of the Principled BSDF node
    links = material.node_tree.links
    links.new(texture_node.outputs['Color'], principled_bsdf.inputs['Base Color'])

    bpy.ops.file.pack_all()
    bpy.ops.object.select_all(action="SELECT")
    # bpy.ops.export_scene.fbx(filepath=f"test_male.fbx", path_mode="COPY", embed_textures=True, bake_anim=False, add_leaf_bones=False)
    
    bpy.ops.export_scene.gltf(filepath=f"test_{gender}.glb", export_format='GLB', use_selection=True)
    return fbx

body_verts, joints, measurement = body_from_image_params(gender=gender, body_image_f=body_image_f, height_m=height_m, weight_kg=weight_kg)

joints = joints[:, :55]
# print(joints.shape)
# print(config.NUM_SMPLX_JOINTS)

# np.savetxt("body.txt", body_verts.numpy())
# np.savetxt("joints.txt", joints.numpy())

texture = cv2.imread("body_head_recovery/data/texture/innerwear_male.png")
bpy_refresh()
create_human_body(body_verts=body_verts.numpy(), body_joints=joints.numpy(), cv_body_tex=texture)
np.savetxt("test_male.txt", body_verts.numpy())

