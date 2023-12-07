import cv2
import pickle
import multiprocessing

# Helper Functions
#---------------------------------------------------------------------------------------------------
def run_cam_opt0(camera_index, terminate_condition, internal_run, shared_img, condition_update_img):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    success, image = False,None

    # Run while terminate condition is not set
    while terminate_condition.value and internal_run.value:
        # Update shared memory with new image
        success, image = cap.read()
        if success:
            shared_img[:] = pickle.dumps(image)
        # Wait for request to update
        with condition_update_img:
            condition_update_img.wait()

    # On manual Termination
    internal_run.value = 0

def run_cam_opt1(camera_index, terminate_condition, internal_run, shared_img, condition_update_img):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    success, image = False,None

    # Run while terminate condition is not set
    while terminate_condition.value and internal_run.value:
        # Update shared memory with new image
        success, image = cap.read()
        if success:
            shared_img[:] = pickle.dumps(image)

    # On manual Termination
    internal_run.value = 0
#---------------------------------------------------------------------------------------------------

class img_controller(object):
    shared_img = None
    condition_update_img = None
    terminate_condition = None
    process_refference = None
    camera_index = -1
    internal_run = None
    capture_type = 0

    def __init__(self, terminate_process=None, cam_index=0, capture_type=0):
        self.camera_index = cam_index
        self.capture_type = capture_type

        # Get image for shared memory measurements
        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        success, image = False,None
        while not success:
            success, image = cap.read()
        cap.release()

        # Initialize shared memory storages
        self.shared_img = multiprocessing.Array('B', pickle.dumps(image))
        self.shared_img[:] = pickle.dumps(image)
        self.condition_update_img = multiprocessing.Condition()
        #self.terminate_condition = terminate_process
        self.internal_run = multiprocessing.Value('i')
        self.internal_run.value = 1

        # TEMP
        if terminate_process == None:
            self.terminate_condition = multiprocessing.Value('i')
            self.terminate_condition.value = 1
        else:
            self.terminate_condition = terminate_process

    # Return function to retrieve camera capture
    def get_img_updater_tupple(self):
        return (self.condition_update_img, self.shared_img)
        '''
        def f():
            with self.condition_update_img:
                self.condition_update_img.notify()
            return pickle.loads(bytearray(self.shared_img[:]))
        return f
        '''

    # Define and run camera capture process
    def run(self):
        self.internal_run.value = 1

        # Define new process to run
        p = None
        # Capture Type 0: Single frame delay
        if self.capture_type == 0:
            p = run_cam_opt0

        # Capture Type 1: Always Updating
        elif self.capture_type == 1:
            p = run_cam_opt1

        else:
            print('Caputer Type is undefined')
            return

        # Run new process
        self.process_refference = multiprocessing.Process(target=p, 
            args=(self.camera_index, self.terminate_condition, self.internal_run, self.shared_img, self.condition_update_img))
        self.process_refference.start()

    # Stardard stop function
    def stop(self):
        self.internal_run.value = 0
        self.condition_update_img.notify_all()
        if self.process_refference.is_alive():
            self.process_refference.terminate()
        self.process_refference.close()
        self.process_refference = None

    # Forced stop function
    def force_stop(self):
        self.internal_run.value = 0
        self.terminate_condition.value = 0
        self.condition_update_img.notify_all()
        
        if self.process_refference.is_alive():
            self.process_refference.kill()
        self.process_refference.close()
        self.process_refference = None

    # Get Camera Capture status
    def process_status(self):
        return self.internal_run.value
