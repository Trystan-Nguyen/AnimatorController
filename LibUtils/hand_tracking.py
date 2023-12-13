import multiprocessing, pickle, json
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class hand_tracking(object):
	cam_shm = None
	terminate_cond = None
	process_refference = None
	tracking = None
	model_path = 'MediaPipeUtil/hand_landmarker.task'

	def __init__(self, terminate, cam, manager):
		self.cam_shm = cam
		self.terminate_cond = terminate

		self.tracking = manager.dict()
		self.tracking['SkipHands'] = manager.list([False, False])
		self.tracking['Landmarks_Left'] = manager.list([manager.list([float(0), float(0), float(0)]) for i in range(21)])
		self.tracking['Landmarks_Right'] = manager.list([manager.list([float(0), float(0), float(0)]) for i in range(21)])


	def get_hand_tracking(self):
		ret = [[],[]]

		if self.tracking['SkipHands'][0]:
			ret[0] = [i[:] for i in self.tracking['Landmarks_Left']]
		if self.tracking['SkipHands'][1]:
			ret[1] = [i[:] for i in self.tracking['Landmarks_Right']]
		return json.dumps(ret)

	def update_detection(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
		if len(result.handedness) == 0:
			return

		invalidHands = ['Landmarks_Left', 'Landmarks_Right']
		for i in range(len(result.handedness)):
			category = result.handedness[i][0]
			key = f'Landmarks_{category.category_name}'
			invalidHands.remove(key)

			detection = []
			for landmark in result.hand_landmarks[i]:
			#for landmark in result.hand_world_landmarks[i]:
				detection.append([landmark.x, landmark.y, landmark.z])
			self.tracking[key] = detection
		
		self.tracking['SkipHands'][0] = 'Landmarks_Left' not in invalidHands
		self.tracking['SkipHands'][1] = 'Landmarks_Right' not in invalidHands


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