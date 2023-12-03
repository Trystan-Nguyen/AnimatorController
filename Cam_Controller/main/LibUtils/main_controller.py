from .cam_controller import cam_controller
from .body_tracking import body_tracking

import multiprocessing, json

class blendshape_controller(object):
	terminate_process_shm = None
	controller_dict = {
		'cam_controller_obj': None,
		'body_tracking_obj': None
	}
	shm_dict = {
		'cam': None,
		'body': None
	}
	framenum_dict = {
		'body': -1
	}
	

	def __init__(self, cam_index=0):
		self.terminate_process_shm = multiprocessing.Value('i')
		self.terminate_process_shm.value = 1

		# Start Camera
		self.controller_dict['cam_controller_obj'] = cam_controller(self.terminate_process_shm, cam_index)
		self.controller_dict['cam_controller_obj'].run()
		self.shm_dict['cam'] = self.controller_dict['cam_controller_obj'].get_image_shm()

	def run_body_tracking(self):
		self.controller_dict['body_tracking_obj'] = body_tracking(self.terminate_process_shm, self.shm_dict['cam'])
		self.controller_dict['body_tracking_obj'].run()
		self.shm_dict['body'] = self.controller_dict['body_tracking_obj'].get_body_tracking()

	'''
		{
			'Frame_Num':int,
			'Landmarks':[[x, y, z, visibility, presence] x 33]
		}
	'''
	def get_body_detections(self):
		if framenum_dict['body'] != self.shm_dict['body']['Frame_Num']:
			framenum_dict['body'] = self.shm_dict['body']['Frame_Num']
			return json.dumps(self.shm_dict['body']['Landmarks'])
		return '[]'

	def terminate(self):
		self.terminate_process_shm.value = 0

		for key in controller_dict.keys():
			if controller_dict[key] is not None:
				controller_dict[key].end()