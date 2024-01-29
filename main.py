from main_controller import blendshape_controller
import cv2, numpy, pickle, time, pprint, json, multiprocessing
from multiprocessing import shared_memory

if __name__ == '__main__':
    config = None
    with open('./config.json', 'r') as f:
        config = json.loads(f.read())
    shm = shared_memory.SharedMemory(
    name=config['hand']['address'], size=config['hand']['size'], create=True)    
    
    ctr = blendshape_controller(cam_index=1)
    ctr.run_hand_tracking()
    
    input('Enter to continue\n')
    #print(shm.buf.tobytes())
    
    data = json.loads(bytearray(shm.buf[:]).decode().rstrip('\0x00'))
    
    input('Enter to continue\n')
    data2 = json.loads(bytearray(shm.buf[:]).decode().rstrip('\0x00'))
    
    pprint.pprint(data)
    print('---------------------------------------------------------')
    pprint.pprint(data2)
    
    ctr.terminate()
