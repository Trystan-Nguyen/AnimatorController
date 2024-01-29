from LibUtils.cam_controller import cam_controller
import cv2, numpy, pickle, time, pprint, json, multiprocessing
from multiprocessing import shared_memory

if __name__ == '__main__':
    terminate_process_shm = multiprocessing.Value('i')
    terminate_process_shm.value = 1

    controller = cam_controller(terminate_process_shm, 1)
    controller.run()
    shm = controller.get_image_shm()
    
    while True:
        cv2.imshow('Cam', pickle.loads(bytearray(shm[:])))
        keys = cv2.waitKey(1) & 0xFF
        if keys == ord('q'):
            break
    