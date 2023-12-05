import pickle, multiprocessing

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class body_tracking(object):
	cam_shm = None
	terminate_cond = None
	process_refference = None
	tracking = None
	model_path = 'MediaPipeUtil/pose_landmarker_heavy.task'

	def __init__(self, terminate, cam):
		self.cam_shm = cam
		self.terminate_cond = terminate

		manager = multiprocessing.Manager()
		self.tracking = manager.dict()
		self.tracking['Frame_Num'] = int(0)
		self.tracking['Landmarks'] = [[float(0), float(0), float(0), float(0), float(0)] for i in range(33)]

	def get_body_tracking(self):
		return self.tracking

	def update_detection(self, result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
		if len(result.pose_world_landmarks) == 0:
			return

		landmark_detections = []
		#for i in range(len(result.pose_landmarks[0])):
		for i in range(len(result.pose_world_landmarks[0])):
			l = result.pose_world_landmarks[0][i]
			landmark_detections.append([l.x, l.y, l.z, l.visibility, l.presence])

		self.tracking['Landmarks'] = landmark_detections
		self.tracking['Frame_Num'] = timestamp_ms

	def body_tracking_subprocess(self):
		options = PoseLandmarkerOptions(
			base_options=BaseOptions(model_asset_path= self.model_path),
			running_mode=VisionRunningMode.LIVE_STREAM,
			result_callback=self.update_detection)
		detector = vision.PoseLandmarker.create_from_options(options)

		t = 0
		while self.terminate_cond.value:
			image = pickle.loads(bytearray(self.cam_shm[:]))
			mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
			detector.detect_async(mp_image, t)
			t += 1

	def run(self):
		self.process_refference = multiprocessing.Process(target=self.body_tracking_subprocess)
		self.process_refference.start()
	
	def end(self):
		if self.process_refference is not None:
			self.process_refference.terminate()
			self.process_refference.join(5)
			self.process_refference.close()
			self.process_refference = None
				

