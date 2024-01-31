import pickle, json
from multiprocessing import shared_memory, Process

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

    def __init__(self, terminate, cam, shm_mem_name):
        self.cam_shm = cam
        self.terminate_cond = terminate
        self.tracking = shared_memory.SharedMemory(name=shm_mem_name)

    def update_detection(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        if len(result.handedness) == 0:
            return

        ret = {'Landmarks_Left':[], 'Landmarks_Right':[]}
        
        for i in range(len(result.handedness)):
            category = result.handedness[i][0]
            key = f'Landmarks_{category.category_name}'

            detection = []
            for landmark in result.hand_landmarks[i]:
            #for landmark in result.hand_world_landmarks[i]:
                detection.append([landmark.x, landmark.y, landmark.z])
            ret[key] = detection

        jsonify_ret = json.dumps(ret, separators=(',', ':'))
        byte_arr_ret = bytearray(self.tracking.size)
        byte_arr_ret[:len(jsonify_ret)] = bytearray(jsonify_ret, 'utf8')
        self.tracking.buf[:] = byte_arr_ret
        

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
        self.process_refference = Process(target=self.hand_tracking_subprocess)
        self.process_refference.start()

    def end(self):
        if self.process_refference is not None:
            self.process_refference.terminate()
            self.process_refference.join(5)
            self.process_refference.close()
            self.process_refference = None
            
            self.tracking.close()