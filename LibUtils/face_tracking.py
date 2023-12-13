import multiprocessing, pickle, numpy, json
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

import pprint, traceback

class face_tracking(object):
	cam_shm = None
	terminate_cond = None
	process_refference = None
	tracking = None
	model_path = 'MediaPipeUtil/face_landmarker.task'

	def __init__(self, terminate, cam, manager):
		self.cam_shm = cam
		self.terminate_cond = terminate

		self.landmarks = manager.list([manager.list([float(0), float(0), float(0)]) for i in range(478)])
		self.trackers = manager.list([float(0) for i in range(52)])

	def get_face_tracking(self):
		landmarks = [i[:] for i in self.landmarks]
		blend = self.trackers[:]
		return json.dumps([landmarks, blend])

	def update_detection(self, result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
		try:
			if len(result.face_landmarks) > 0:
				l = []
				for i in range(len(result.face_landmarks[0])):
					landmark = result.face_landmarks[0][i]
					l.append([landmark.x, landmark.y, landmark.z])
				self.landmarks[:] = l[:]

				scores = []
				for i in result.face_blendshapes[0]:
					scores.append(i.score)
				self.trackers[:] = scores
		except:
			print(traceback.format_exc())



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