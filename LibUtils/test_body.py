import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

import traceback
import sys

import time

def draw_landmarks_on_image(rgb_image, detection_result):
	pose_landmarks_list = detection_result.pose_landmarks
	annotated_image = np.copy(rgb_image)

	# Loop through the detected poses to visualize.
	for idx in range(len(pose_landmarks_list)):
		pose_landmarks = pose_landmarks_list[idx]

	# Draw the pose landmarks.
	pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
	pose_landmarks_proto.landmark.extend([
		landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
	])
	solutions.drawing_utils.draw_landmarks(
		annotated_image,
		pose_landmarks_proto,
		solutions.pose.POSE_CONNECTIONS,
		solutions.drawing_styles.get_default_pose_landmarks_style())
	return annotated_image

model_path = '../MediaPipeUtil/pose_landmarker_heavy.task'


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the live stream mode:
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
	try:
		print("\n\n\n---------------------------------------------\n\n\n")
		GLOBAL_RESULT = result
		print('pose landmarker result: {}'.format(result.pose_landmarks))
		
		annotated_image = draw_landmarks_on_image(output_image.numpy_view(), result)
		cv2.imshow("window", annotated_image)
		cv2.waitKey(0) 
		input("Enter to Exit:\n")
	except Exception:
		print(traceback.format_exc())

if __name__=='__main__':
	options = PoseLandmarkerOptions(
		base_options=BaseOptions(model_asset_path=model_path),
		running_mode=VisionRunningMode.LIVE_STREAM,
    	result_callback=print_result)
	detector = vision.PoseLandmarker.create_from_options(options)

	cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
	success, image = False,None
	while not success:
		success, image = cap.read()

	#cv2.imshow("Start", image)

	mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
	detector.detect_async(mp_image, 0)

	time.sleep(5)
	input("Enter to Exit2:\n")
	'''
	detection_result = PoseLandmarkerOptions.result_callback
	annotated_image = draw_landmarks_on_image(image, detection_result)
	cv2.imshow("window", annotated_image)
	cv2.waitKey(0) 
	'''
	