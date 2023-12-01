from .cam_controller import cam_controller

import multiprocessing

class blendshape_controller(object):
	terminate_process_shm = None
	controller_dict = {
		'cam_controller_obj': None
	}
	

	def __init__(self, cam_index=0):
		self.terminate_process_shm = multiprocessing.Value('i')
		self.terminate_process_shm.value = 1

		# Start Camera
		controller_dict['cam_controller_obj'] = cam_controller(self.terminate_process_shm, cam_index)
		controller_dict['cam_controller_obj'].run()

	def terminate(self):
		self.terminate_process_shm.value = 0

		for key in controller_dict.keys():
			if controller_dict[key] is not None:
				controller_dict[key].end()