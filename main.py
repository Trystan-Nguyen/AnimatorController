from main_controller import blendshape_controller
import cv2, numpy, pickle, time, pprint

if __name__ == '__main__':
	ctr = blendshape_controller(0)

	#ctr.run_body_tracking()
	ctr.run_face_tracking()
	#ctr.run_hand_tracking()
	input("Enter to print data")
	#pprint.pprint(ctr.get_body_detections())
	#print('\n\n\n---------------------------------------------------------------------\n\n\n')
	#pprint.pprint(ctr.get_hand_detections())
	#print('\n\n\n---------------------------------------------------------------------\n\n\n')
	print(ctr.get_face_detections())
	#print('\n\n\n---------------------------------------------------------------------\n\n\n')
	
	input("Enter to quit:")
	print(ctr.get_face_detections())
	ctr.terminate()
