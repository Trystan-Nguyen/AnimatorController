import cv2, numpy
import pickle
import multiprocessing

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    print('pose landmarker result: {}'.format(result))

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)


class body_tracking(object):
	cam_shm = None
	terminate_cond = None

	def __init__(self, cam, terminate):
		cam_shm = cam
		terminate_cond = terminate

		model_path = 'MediaPipeUtil/pose_landmarker_heavy.task'

	def run(self):
		while self.terminate_cond.value:
			with PoseLandmarker.create_from_options(options) as landmarker:
				mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, 
					data=pickle.loads(bytearray(cam_shm[:]))

				landmarker.detect_async(mp_image, frame_timestamp_ms)

