import pickle, multiprocessing, json
from multiprocessing import shared_memory, Process

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

    def __init__(self, terminate, cam, shm_mem_name):
        self.cam_shm = cam
        self.terminate_cond = terminate
        self.tracking = shared_memory.SharedMemory(name=shm_mem_name)
        
    def update_detection(self, result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        if len(result.pose_world_landmarks) == 0:
            return

        landmark_detections = []
        #for i in range(len(result.pose_landmarks[0])):
        for i in range(len(result.pose_world_landmarks[0])):
            l = result.pose_world_landmarks[0][i]
            landmark_detections.append([l.x, l.y, l.z, l.visibility, l.presence])
        
        jsonify_ret = json.dumps(landmark_detections)
        byte_arr_ret = bytearray(self.tracking.size)
        byte_arr_ret[:len(jsonify_ret)] = bytearray(jsonify_ret, 'utf8')
        self.tracking.buf[:] = byte_arr_ret

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
        self.process_refference = Process(target=self.body_tracking_subprocess)
        self.process_refference.start()

    def end(self):
        if self.process_refference is not None:
            self.process_refference.terminate()
            self.process_refference.join(5)
            self.process_refference.close()
            self.process_refference = None
            
            self.tracking.close()
                

