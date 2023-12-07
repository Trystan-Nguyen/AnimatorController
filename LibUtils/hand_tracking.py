import multiprocessing, pickle
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

import pprint

class hand_tracking(object):
	cam_shm = None
	terminate_cond = None
	process_refference = None
	tracking = None
	model_path = 'MediaPipeUtil/hand_landmarker.task'

	def __init__(self, terminate, cam):
		self.cam_shm = cam
		self.terminate_cond = terminate

		manager = multiprocessing.Manager()
		self.tracking = manager.dict()
		self.tracking['Frame_Num'] = int(0)
		self.tracking['Landmarks_Left'] = [[float(0), float(0), float(0)] for i in range(21)]
		self.tracking['Landmarks_Right'] = [[float(0), float(0), float(0)] for i in range(21)]

	def get_hand_tracking(self):
		return self.tracking

	def update_detection(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
		if len(result.handedness) == 0:
			return

		for category in result.handedness:
			index = category.index
			key = f'Landmarks_{category.category_name}'

			detection = []
			for landmark in hand_landmarks[index]:
			#for landmark in hand_world_landmarks[index]:
				detection.append([landmark.x, landmark.y, landmark.z])

			self.tracking[key] = detection
		self.tracking['Frame_Num'] = timestamp_ms

	def hand_tracking_subprocess(self):
		options = HandLandmarkerOptions(
			base_options=BaseOptions(model_asset_path=self.model_path),
			running_mode=VisionRunningMode.LIVE_STREAM,
			num_hands=2,
			result_callback=self.update_detection)
		detector = HandLandmarker.create_from_options(options)
		
		t = 0
		while self.terminate_cond.value:
			image = pickle.loads(bytearray(self.cam_shm[:]))
			mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
			detector.detect_async(mp_image, t)
			t += 1

	def run(self):
		self.process_refference = multiprocessing.Process(target=self.hand_tracking_subprocess)
		self.process_refference.start()

	def end(self):
		if self.process_refference is not None:
			self.process_refference.terminate()
			self.process_refference.join(5)
			self.process_refference.close()
			self.process_refference = None