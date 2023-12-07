import multiprocessing, pickle
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


import pprint
import traceback

class face_tracking(object):
	cam_shm = None
	terminate_cond = None
	process_refference = None
	tracking = None
	model_path = 'MediaPipeUtil/face_landmarker.task'

	def __init__(self, terminate, cam):
		self.cam_shm = cam
		self.terminate_cond = terminate

		manager = multiprocessing.Manager()
		self.tracking = manager.dict()
		self.tracking['Frame_Num'] = int(0)
		self.tracking['Landmarks'] = [[float(0), float(0), float(0)] for i in range(478)]
		self.tracking['BlendShape'] = [float(0) for i in range(52)]

	def get_face_tracking(self):
		return self.tracking

	def update_detection(self, result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
		if len(result.face_landmarks) > 0:
			for i in range(len(result.face_landmarks[0])):
				landmark = result.face_landmarks[0][i]
				self.tracking['Landmarks'][i] = [landmark.x, landmark.y, landmark.z]

			for i in result.face_blendshapes[0]:
				self.tracking['BlendShape'][i.index] = i.score

			self.tracking['Frame_Num'] = timestamp_ms


	def face_tracking_subprocess(self):
		options = FaceLandmarkerOptions(
			base_options=BaseOptions(model_asset_path=self.model_path),
			running_mode=VisionRunningMode.LIVE_STREAM,
			output_face_blendshapes=True,
			result_callback=self.update_detection)

		detector = FaceLandmarker.create_from_options(options)
		
		t = 0
		while self.terminate_cond.value:
			image = pickle.loads(bytearray(self.cam_shm[:]))
			mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
			detector.detect_async(mp_image, t)
			t += 1

	def run(self):
		self.process_refference = multiprocessing.Process(target=self.face_tracking_subprocess)
		self.process_refference.start()

	def end(self):
		if self.process_refference is not None:
			self.process_refference.terminate()
			self.process_refference.join(5)
			self.process_refference.close()
			self.process_refference = None