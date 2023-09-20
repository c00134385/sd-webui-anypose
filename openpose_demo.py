import cv2
import einops
import gradio as gr
import numpy as np
import torch
import random
from PIL import Image
import sys
import functools
import os
import time

from annotator.util import HWC3

from scripts.processor import (
    resize_image_with_pad
)

from annotator.openpose import OpenposeDetector, encode_poses_as_json, draw_poses

model_openpose = OpenposeDetector()

base = 'D:\\AI\\images'
output_base = 'D:\\AI\\output'
include_body = True
include_hand = True
include_face = True

def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            yield os.path.join(root, f)


def checkFile(file_path):
    # 判断文件是否存在
    if os.path.exists(file_path):
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1]
        # 判断文件扩展名是否为图片格式
        image_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        if file_ext.lower() in image_ext:
            # 输出文件是图像的提示信息
            print(f"{file_path} 该文件是图像文件。")
            return True
        else:
            # 输出文件不是图像的提示信息
            print(f"{file_path} 该文件不是图像文件。")
            return False
    else:
        # 输出文件不存在的提示信息
        print(f"{file_path} 文件不存在。")
        return False


def detectPose(file_path):
    start_time = time.time()
    (filepath, tempfilename) = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(tempfilename)
    print(f'{filepath}  {file_name}  {file_ext}')

    # img = Image.open("D:\\AI\\images\\00013-1474532850.png")

    print(f'start detecting {file_path}')
    output_file_path = filepath.replace(base, output_base)

    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    img = Image.open(file_path)
    img = np.array(img)
    # print(img)
    # print(type(img))

    img = HWC3(img)
    # print('image: ', img)
    # print('image', type(img))

    # print('image.shape: ', img.shape)
    img, remove_pad = resize_image_with_pad(img, 512)
    # print('*image.shape: ', img.shape)
    # print('hello world', model_openpose)
    H, W, _ = img.shape
    poses = model_openpose.detect_poses(img, include_hand, include_face)
    # print("\r\n")
    # print("openpose detect output: ")
    # print(poses)

    poseImg = draw_poses(poses, H, W, draw_body=include_body, draw_hand=include_hand, draw_face=include_face)
    # print(type(poseImg))
    poseImg = Image.fromarray(poseImg)
    poseImg.save(os.path.join(output_file_path, file_name + ".png"))
    # print("\r\n")
    # print("conver to json: ")
    poses = encode_poses_as_json(poses, H, W)
    # print(poses)
    # print(type(poses))
    f = open(os.path.join(output_file_path, file_name + ".json"), "w")
    f.write(poses)
    f.close()
    print(f'stop detecting {file_path}')
    end_time = time.time()
    print("耗时: {:.2f}秒".format(end_time - start_time))




def main():
    for i in findAllFile(base):
        print(f'------------ {i}')
        (filepath, tempfilename) = os.path.split(i)
        print(f'{filepath}  {tempfilename}')
        if checkFile(i):
            detectPose(i)


if __name__ == '__main__':
    main()

# # img = Image.open("D:\\AI\\images\\00013-1474532850.png")
# img = Image.open("D:\\AI\\images\\20230916213447.jpg")
# img = np.array(img)
# # print(img)
# # print(type(img))

# img = HWC3(img)
# # print('image: ', img)
# # print('image', type(img))



# print('image.shape: ', img.shape)
# img, remove_pad = resize_image_with_pad(img, 512)
# print('*image.shape: ', img.shape)
# model_openpose = OpenposeDetector()
# print('hello world', model_openpose)
# H, W, _ = img.shape
# poses = model_openpose.detect_poses(img, include_hand, include_face)
# print("\r\n")
# print("openpose detect output: ")
# print(poses)

# poseImg = draw_poses(poses, H, W, draw_body=include_body, draw_hand=include_hand, draw_face=include_face)
# print(type(poseImg))
# poseImg = Image.fromarray(poseImg)
# poseImg.save("full_pose.png")

# print("\r\n")
# print("conver to json: ")
# poses = encode_poses_as_json(poses, H, W)
# print(poses)
# print(type(poses))

# f = open("full_pose.json", "w")
# f.write(poses)
# f.close()


# print(torch.cuda.is_available())



# def upload_file(files):
#     file_paths = [file.name for file in files]
#     return file_paths

# with gr.Blocks() as demo:
#     file_output = gr.File()
#     upload_button = gr.UploadButton("Click to Upload a File", file_types=["image", "video"], file_count="multiple")
#     upload_button.upload(upload_file, upload_button, file_output)

# demo.launch()



# print(get_cuda_device_string())

# if torch.cuda.is_available():
#     return get_cuda_device_string()





# result = g_openpose_model.run_model(img, False, False, True, None)
# print(result)
# img = HWC3(img)
# print(img)
# print(type(img))

# module = global_state.get_module_basename("openpose_full")
# print(f'module: {module}')
# img = gr.Image(value="D:\\AI\\images\\00013-1474532850.png", type="numpy")
# print(img)
# print(type(img))

# def process(input_image):
#     print('image: ', input_image)
#     print('image', type(input_image))
#     return input_image


# block = gr.Blocks().queue()
# with block:
#     with gr.Row():
#         gr.Markdown("## Control Stable Diffusion with Human Pose")
#     with gr.Row():
#         with gr.Column():
#             input_image = gr.Image(source='upload', type="numpy")
#             # prompt = gr.Textbox(label="Prompt")
#             run_button = gr.Button(label="Run")
#             # with gr.Accordion("Advanced options", open=False):
#             #     num_samples = gr.Slider(label="Images", minimum=1, maximum=12, value=1, step=1)
#             #     image_resolution = gr.Slider(label="Image Resolution", minimum=256, maximum=768, value=512, step=64)
#             #     strength = gr.Slider(label="Control Strength", minimum=0.0, maximum=2.0, value=1.0, step=0.01)
#             #     guess_mode = gr.Checkbox(label='Guess Mode', value=False)
#             #     detect_resolution = gr.Slider(label="OpenPose Resolution", minimum=128, maximum=1024, value=512, step=1)
#             #     ddim_steps = gr.Slider(label="Steps", minimum=1, maximum=100, value=20, step=1)
#             #     scale = gr.Slider(label="Guidance Scale", minimum=0.1, maximum=30.0, value=9.0, step=0.1)
#             #     seed = gr.Slider(label="Seed", minimum=-1, maximum=2147483647, step=1, randomize=True)
#             #     eta = gr.Number(label="eta (DDIM)", value=0.0)
#             #     a_prompt = gr.Textbox(label="Added Prompt", value='best quality, extremely detailed')
#             #     n_prompt = gr.Textbox(label="Negative Prompt",
#             #                           value='longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality')
#         with gr.Column():
#             result_gallery = gr.Image(type="numpy").style(height='auto')
#             # result_gallery = gr.Gallery(label='Output', show_label=False, elem_id="gallery").style(grid=2, height='auto')
#     ips = [input_image]
#     run_button.click(fn=process, inputs=ips, outputs=[result_gallery])


# block.launch()