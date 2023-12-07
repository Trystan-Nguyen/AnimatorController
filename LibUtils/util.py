import cv2, pickle

def readImg(img_shm):
	return pickle.loads(bytearray(img_shm[:]))
