import cv2
import pickle
import multiprocessing

def update_image_process(camera_index, terminate_condition, shared_img, 
	):
	cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    success, image = False,None

    # Run while terminate condition is not set
    while terminate_condition.value and internal_run.value:
        # Update shared memory with new image
        success, image = cap.read()
        if success:
            shared_img[:] = pickle.dumps(image)

class cam_controller(object):
	shared_img = None
	terminate_condition = None
	internal_run = None
	camera_index = -1
	process_refference = None

	def __init__(self, terminate_process, cam_index=0):
		self.camera_index = cam_index
		
		# Get image for shared memory measurements
        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        success, image = False,None
        while not success:
            success, image = cap.read()
        cap.release()

        # Initialize shared memory storages
        self.shared_img = multiprocessing.Array('B', pickle.dumps(image))
        self.shared_img[:] = pickle.dumps(image)
        self.terminate_condition = terminate_process
        self.internal_run = multiprocessing.Value('i')
        self.internal_run.value = 0

    def get_image_shm(self)
    	return self.shared_img

	def run(self):
		# Return early if process already running
		if self.process_refference is None:
			return

		# Run new process
		self.internal_run.value = 1
        self.process_refference = multiprocessing.Process(target=p, 
            args=(self.camera_index, self.terminate_condition, self.shared_img, self.internal_run))
        self.process_refference.start()

    def end(self):
    	if self.process_refference is None:
    		return

    	self.internal_run.value = 0
    	self.process_refference.join(5)
		if self.process_refference.is_alive():
			self.process_refference.kill()
		self.process_refference.close()
		self.process_refference = None


