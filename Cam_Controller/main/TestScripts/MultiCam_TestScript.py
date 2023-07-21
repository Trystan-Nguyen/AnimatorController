import multiprocessing
import cv2
import pickle
import numpy

from LibUtils import img_controller

def sharedmem_tupple_to_img(tupple):
	with tupple[0]:
		tupple[0].notify()
	return pickle.loads(bytearray(tupple[1][:]))

def new_window(window_name, tupple, end_condition):
	index = 0
	while end_condition.value:
		image = sharedmem_tupple_to_img(tupple)
		cv2.imshow(window_name, cv2.flip(image, 1))
		if cv2.waitKey(1) & 0xFF == 27:
			break
		
	cv2.destroyAllWindows()
	return None


def main():
	shared_mem_term = multiprocessing.Value('i')
	shared_mem_term.value = 1

	try:
		cam_obj = img_controller.img_controller(terminate_process=shared_mem_term, cam_index=1, capture_type=1)
	except Exception as e:
		print(e)

	cam_obj.run()

	window1 = multiprocessing.Process(target=new_window, args=("Window1", cam_obj.get_img_updater_tupple(), shared_mem_term))
	window1.start()

	window2 = multiprocessing.Process(target=new_window, args=("Window2", cam_obj.get_img_updater_tupple(), shared_mem_term))
	window2.start()

	input('Press Enter to end:\n')
	shared_mem_term.value = 0