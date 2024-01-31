from main_controller import animator_lib
from multiprocessing import shared_memory
import sys, time, json

HAND_CODE = 0b001
BODY_CODE = 0b010
FACE_CODE = 0b100

# Expected Arguements
# exe camera_index config_uri code
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Error: Expected camera_index, config_uri, code arguements')
        sys.exit()
    
    args_camera_index = int(sys.argv[1])
    args_config_uri = sys.argv[2]
    args_code = int(sys.argv[3])
    
    config = None
    with open(args_config_uri, 'r') as f:
        config = json.loads(f.read())
    
    controller_obj = animator_lib(config, cam_index=args_camera_index)
    if args_code & HAND_CODE != 0:
        controller_obj.run_hand_tracking()
    if args_code & BODY_CODE != 0:
        controller_obj.run_body_tracking()
    if args_code & FACE_CODE != 0:
        controller_obj.run_face_tracking()
    
    cond = shared_memory.SharedMemory(name=config['terminateCond']['address'])
    while True:
        time.sleep(5)
        if cond.buf[0] == 1:
            break
    cond.close()
    
    controller_obj.terminate()