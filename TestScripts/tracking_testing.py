from LibUtils import face_tracking
from LibUtils import cam_controller

import multiprocessing
import time

def main():
	term_cond = multiprocessing.Value('i')
	term_cond.value = 1
	cam_obj = cam_controller.cam_controller(term_cond, 0)

	cam_obj.run()

	tracker = face_tracking.face_tracking(term_cond, cam_obj.get_image_shm())
	tracker.run()

	time.sleep(5)

	input("Enter to end\n")
	term_cond.value = 0
	cam_obj.end()
	tracker.end()