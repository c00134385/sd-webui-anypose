import modules.scripts as scripts
import gradio as gr
import os
import json
import json
import random
from typing import NamedTuple, Tuple, List, Callable, Union, Optional
import numpy as np
import math
import matplotlib
import cv2
from PIL import Image

current_script = os.path.realpath(__file__)
current_folder = os.path.dirname(current_script)
work_basedir = os.path.dirname(current_folder)  # 本插件目录
path1 = work_basedir + r"/json"
path2 = work_basedir + r"/yours"
pathrandom = work_basedir + r"/random"
assetsPath = work_basedir + r"/assets"

eps = 0.01


class Keypoint(NamedTuple):
    x: float
    y: float
    score: float = 1.0
    id: int = -1


class BodyResult(NamedTuple):
    # Note: Using `Union` instead of `|` operator as the ladder is a Python
    # 3.10 feature.
    # Annotator code should be Python 3.8 Compatible, as controlnet repo uses
    # Python 3.8 environment.
    # https://github.com/lllyasviel/ControlNet/blob/d3284fcd0972c510635a4f5abe2eeb71dc0de524/environment.yaml#L6
    keypoints: List[Union[Keypoint, None]]
    total_score: float = 0.0
    total_parts: int = 0


HandResult = List[Keypoint]
FaceResult = List[Keypoint]


class PoseResult(NamedTuple):
    body: BodyResult
    left_hand: Union[HandResult, None]
    right_hand: Union[HandResult, None]
    face: Union[FaceResult, None]


def decode_json_as_poses(json_string: str, normalize_coords: bool = False) -> Tuple[List[PoseResult], int, int]:
    """ Decode the json_string complying with the openpose JSON output format
    to poses that controlnet recognizes.
    https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/02_output.md

    Args:
        json_string: The json string to decode.
        normalize_coords: Whether to normalize coordinates of each keypoint by canvas height/width.
                          `draw_pose` only accepts normalized keypoints. Set this param to True if
                          the input coords are not normalized.

    Returns:
        poses
        canvas_height
        canvas_width                      
    """
    pose_json = json.loads(json_string)
    height = pose_json['canvas_height']
    width = pose_json['canvas_width']

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def normalize_keypoint(keypoint: Keypoint) -> Keypoint:
        return Keypoint(
            keypoint.x / width,
            keypoint.y / height
        )

    def decompress_keypoints(numbers: Optional[List[float]]) -> Optional[List[Optional[Keypoint]]]:
        if not numbers:
            return None

        assert len(numbers) % 3 == 0

        def create_keypoint(x, y, c):
            if c < 1.0:
                return None
            keypoint = Keypoint(x, y)
            if normalize_coords:
                keypoint = normalize_keypoint(keypoint)
            return keypoint

        return [
            create_keypoint(x, y, c)
            for x, y, c in chunks(numbers, n=3)
        ]

    return (
        [
            PoseResult(
                body=BodyResult(keypoints=decompress_keypoints(
                    pose.get('pose_keypoints_2d'))),
                left_hand=decompress_keypoints(
                    pose.get('hand_left_keypoints_2d')),
                right_hand=decompress_keypoints(
                    pose.get('hand_right_keypoints_2d')),
                face=decompress_keypoints(pose.get('face_keypoints_2d'))
            )
            for pose in pose_json['people']
        ],
        height,
        width,
    )


def draw_poses(poses: List[PoseResult], H, W, draw_body=True, draw_hand=True, draw_face=True):
    """
    Draw the detected poses on an empty canvas.

    Args:
        poses (List[PoseResult]): A list of PoseResult objects containing the detected poses.
        H (int): The height of the canvas.
        W (int): The width of the canvas.
        draw_body (bool, optional): Whether to draw body keypoints. Defaults to True.
        draw_hand (bool, optional): Whether to draw hand keypoints. Defaults to True.
        draw_face (bool, optional): Whether to draw face keypoints. Defaults to True.

    Returns:
        numpy.ndarray: A 3D numpy array representing the canvas with the drawn poses.
    """
    canvas = np.zeros(shape=(H, W, 3), dtype=np.uint8)

    for pose in poses:
        if draw_body:
            canvas = draw_bodypose(canvas, pose.body.keypoints)

        if draw_hand:
            canvas = draw_handpose(canvas, pose.left_hand)
            canvas = draw_handpose(canvas, pose.right_hand)

        if draw_face:
            canvas = draw_facepose(canvas, pose.face)

    return canvas


def draw_bodypose(canvas: np.ndarray, keypoints: List[Keypoint]) -> np.ndarray:
    """
    Draw keypoints and limbs representing body pose on a given canvas.

    Args:
        canvas (np.ndarray): A 3D numpy array representing the canvas (image) on which to draw the body pose.
        keypoints (List[Keypoint]): A list of Keypoint objects representing the body keypoints to be drawn.

    Returns:
        np.ndarray: A 3D numpy array representing the modified canvas with the drawn body pose.

    Note:
        The function expects the x and y coordinates of the keypoints to be normalized between 0 and 1.
    """
    H, W, C = canvas.shape
    stickwidth = 4

    limbSeq = [
        [2, 3], [2, 6], [3, 4], [4, 5],
        [6, 7], [7, 8], [2, 9], [9, 10],
        [10, 11], [2, 12], [12, 13], [13, 14],
        [2, 1], [1, 15], [15, 17], [1, 16],
        [16, 18],
    ]

    colors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0],
              [0, 255, 85], [0, 255, 170], [0, 255, 255], [
                  0, 170, 255], [0, 85, 255], [0, 0, 255], [85, 0, 255],
              [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]]

    for (k1_index, k2_index), color in zip(limbSeq, colors):
        keypoint1 = keypoints[k1_index - 1]
        keypoint2 = keypoints[k2_index - 1]

        if keypoint1 is None or keypoint2 is None:
            continue

        Y = np.array([keypoint1.x, keypoint2.x]) * float(W)
        X = np.array([keypoint1.y, keypoint2.y]) * float(H)
        mX = np.mean(X)
        mY = np.mean(Y)
        length = ((X[0] - X[1]) ** 2 + (Y[0] - Y[1]) ** 2) ** 0.5
        angle = math.degrees(math.atan2(X[0] - X[1], Y[0] - Y[1]))
        polygon = cv2.ellipse2Poly((int(mY), int(mX)), (int(
            length / 2), stickwidth), int(angle), 0, 360, 1)
        cv2.fillConvexPoly(canvas, polygon, [
                           int(float(c) * 0.6) for c in color])

    for keypoint, color in zip(keypoints, colors):
        if keypoint is None:
            continue

        x, y = keypoint.x, keypoint.y
        x = int(x * W)
        y = int(y * H)
        cv2.circle(canvas, (int(x), int(y)), 4, color, thickness=-1)

    return canvas


def draw_handpose(canvas: np.ndarray, keypoints: Union[List[Keypoint], None]) -> np.ndarray:
    """
    Draw keypoints and connections representing hand pose on a given canvas.

    Args:
        canvas (np.ndarray): A 3D numpy array representing the canvas (image) on which to draw the hand pose.
        keypoints (List[Keypoint]| None): A list of Keypoint objects representing the hand keypoints to be drawn
                                          or None if no keypoints are present.

    Returns:
        np.ndarray: A 3D numpy array representing the modified canvas with the drawn hand pose.

    Note:
        The function expects the x and y coordinates of the keypoints to be normalized between 0 and 1.
    """
    if not keypoints:
        return canvas

    H, W, C = canvas.shape

    edges = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8], [0, 9], [9, 10],
             [10, 11], [11, 12], [0, 13], [13, 14], [14, 15], [15, 16], [0, 17], [17, 18], [18, 19], [19, 20]]

    for ie, (e1, e2) in enumerate(edges):
        k1 = keypoints[e1]
        k2 = keypoints[e2]
        if k1 is None or k2 is None:
            continue

        x1 = int(k1.x * W)
        y1 = int(k1.y * H)
        x2 = int(k2.x * W)
        y2 = int(k2.y * H)
        if x1 > eps and y1 > eps and x2 > eps and y2 > eps:
            cv2.line(canvas, (x1, y1), (x2, y2), matplotlib.colors.hsv_to_rgb(
                [ie / float(len(edges)), 1.0, 1.0]) * 255, thickness=2)

    for keypoint in keypoints:
        if keypoint is None:
            continue

        x, y = keypoint.x, keypoint.y
        x = int(x * W)
        y = int(y * H)
        if x > eps and y > eps:
            cv2.circle(canvas, (x, y), 4, (0, 0, 255), thickness=-1)
    return canvas


def draw_facepose(canvas: np.ndarray, keypoints: Union[List[Keypoint], None]) -> np.ndarray:
    """
    Draw keypoints representing face pose on a given canvas.

    Args:
        canvas (np.ndarray): A 3D numpy array representing the canvas (image) on which to draw the face pose.
        keypoints (List[Keypoint]| None): A list of Keypoint objects representing the face keypoints to be drawn
                                          or None if no keypoints are present.

    Returns:
        np.ndarray: A 3D numpy array representing the modified canvas with the drawn face pose.

    Note:
        The function expects the x and y coordinates of the keypoints to be normalized between 0 and 1.
    """
    if not keypoints:
        return canvas

    H, W, C = canvas.shape
    for keypoint in keypoints:
        if keypoint is None:
            continue

        x, y = keypoint.x, keypoint.y
        x = int(x * W)
        y = int(y * H)
        if x > eps and y > eps:
            cv2.circle(canvas, (x, y), 3, (255, 255, 255), thickness=-1)
    return canvas


def loadAssetsFiles():
    dic = {}
    loadJsonFiles(path1, dic)
    loadJsonFiles(path2, dic)
    print(f'dic: {dic}')
    return json.dumps(dic, ensure_ascii=False)


def loadJsonFiles(path, dic):
    files = os.listdir(path)
    for item in files:
        if item.endswith(".json"):
            filepath = path+'/'+item
            filename = filepath[filepath.rindex('/') + 1:-5]
            with open(filepath, "r", encoding="utf-8-sig") as f:
                res = json.loads(f.read())
                dic[filename] = res


class Script(scripts.Script):
    json = loadAssetsFiles()
    poseImage = None

    def title(self):
        return "AnyPose"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    # def showPose(src):
    #     print(f'id: {src}')
    #     pass
    def processPoseJson(self, src):
        file_name, file_ext = os.path.splitext(src)

        dest = os.path.join(assetsPath, src)
        dest = os.path.normpath(dest)
        print(f'dest: {dest} {os.path.exists(dest)}')
        if os.path.exists(dest):
            f = open(dest, 'r')
            json_string = f.read()
            poses, height, width = decode_json_as_poses(json_string)
            # print(f'{poses} {height} {width}')
            poses = draw_poses(poses, height, width,
                               draw_body=True, draw_hand=True, draw_face=True)
            # print(f'postImg: {poses} {type(poses)}')
            # poses = Image.fromarray(poses)
            print(f'postImg: {poses} {type(poses)}')
            # poses.save(os.path.normpath(os.path.join(assetsPath, file_name + '.png')))
            return poses
            # img = Image.open("D:\\AI\\images\\202309162134.jpg")
            # img = np.array(img)
            # print(f'postImg: {img} {type(img)}')
            # return img

    def ui(self, is_img2img):
        """this function should create gradio UI elements. See https://gradio.app/docs/#components
        The return value should be an array of all components that are used in processing.
        Values of those returned components will be passed to run() and process() functions.
        """
        controls = ()
        prefix = "img2img" if is_img2img else "txt2img"
        elem_id_tabname = prefix + "_anypose"
        with gr.Group(elem_id=elem_id_tabname):
            with gr.Accordion(f"AnyPose v{1.0}", open=False, elem_id="anypose"):
                textarea = gr.TextArea(self.json, visible=False)
                btnreload = gr.Button(
                    '🔄', elem_classes="anypose-reload sm secondary gradio-button svelte-1ipelgc")
                with gr.Row():
                    self.poseImage = gr.Image().style(height=242)
                    with gr.Tabs(elem_id=f"{elem_id_tabname}_tabs", scale=2):
                        # 将 JSON 对象转换为 Python 字典
                        params_json = json.loads(self.json)
                        items = params_json.items()
                        i = 0
                        for key, value in items:
                            i += 1
                            print(str(key) + '=' + str(value))
                            print(f'----------------- {type(value)}')
                            with gr.Tab(f"{key}", elem_classes=['cnet-unit-tab']):
                                with gr.Row():
                                    if isinstance(value, dict):
                                        ii = 0
                                        for k, v in value.items():
                                            ii += 1
                                            def showPose(src):
                                                print(f'id: {src}')
                                                result = self.processPoseJson(
                                                    src)
                                                print(f'result --------- : {result} {type(result)}')
                                                return result
                                            text = gr.Text(
                                                value=v, visible=False)
                                            btn = gr.Button(
                                                value=f"{k}", elem_id=f"{elem_id_tabname}_button_{i}_{ii}")
                                            btn.click(fn=showPose, inputs=[
                                                      text], outputs=[self.poseImage])
                                            controls += (btn,)
                                    else:
                                        controls += (gr.TextArea(
                                            value=f"{prefix} {value}", elem_id=f"{elem_id_tabname}_textarea_{i}"),)

            def reloadData():
                self.json = loadAssetsFiles()
                return self.json

            btnreload.click(fn=reloadData, inputs=None, outputs=textarea)

        return controls
