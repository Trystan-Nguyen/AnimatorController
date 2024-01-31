from LibUtils.cam_controller import cam_controller
from LibUtils.body_tracking import body_tracking
from LibUtils.hand_tracking import hand_tracking
from LibUtils.face_tracking import face_tracking

import multiprocessing

class animator_lib(object):
    terminate_process_shm = None
    controller_dict = {
        'cam_controller_obj': None
    }
    shm_cam = None
    shm_config = None

    def __init__(self, config, cam_index=0):
        self.terminate_process_shm = multiprocessing.Value('i')
        self.terminate_process_shm.value = 1

        # Get shm config
        self.shm_config = config
        
        # Start Camera
        self.controller_dict['cam_controller_obj'] = cam_controller(self.terminate_process_shm, cam_index)
        self.controller_dict['cam_controller_obj'].run()
        self.shm_cam = self.controller_dict['cam_controller_obj'].get_image_shm()
        

    def run_body_tracking(self):
        self.controller_dict['body_tracking_obj'] = body_tracking(self.terminate_process_shm, self.shm_cam, self.shm_config['body']['address'])
        self.controller_dict['body_tracking_obj'].run()
        
    def run_hand_tracking(self):
        self.controller_dict['hand_tracking_obj'] = hand_tracking(self.terminate_process_shm, self.shm_cam, self.shm_config['hand']['address'])
        self.controller_dict['hand_tracking_obj'].run()

    def run_face_tracking(self):
        self.controller_dict['face_tracking_obj'] = face_tracking(self.terminate_process_shm, self.shm_cam, self.shm_config['face']['address'])
        self.controller_dict['face_tracking_obj'].run()

    def terminate(self):
        self.terminate_process_shm.value = 0
        for key in self.controller_dict.keys():
            self.controller_dict[key].end()

'''
    # [[x,y,z,visibility,presence] x 33]
    def get_body_detections(self):
        return self.controller_dict['body_tracking_obj'].get_body_tracking()

    # [L[[x,y,z] x 21], R[[x,y,z] x 21]]
    def get_hand_detections(self):
        return self.controller_dict['hand_tracking_obj'].get_hand_tracking()

    # [[[x,y,z]] x 478, [score x 52]]
    def get_face_detections(self):
        return self.controller_dict['face_tracking_obj'].get_face_tracking()
'''