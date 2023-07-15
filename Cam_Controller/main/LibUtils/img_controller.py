import cv2
import pickle
import multiprocessing

class img_controller(object):
    shared_img = None
    condition_update_img = None
    terminate_condition = None
    process_refference = None
    camera_index = -1
    internal_run = None

    def __init__(self, terminate_process=None, cam_index=1):
        self.camera_index = cam_index

        # Get image for shared memory measurements
        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        success, image = False,None
        while not success:
            success, image = cap.read()
        cap.release()

        # Initialize shared memory storages
        self.shared_img = multiprocessing.Array('B', pickle.dumps(image))
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

    def get_img_updater_funct(self):
        def f():
            with self.condition_update_img:
                self.condition_update_img.notify()
            with self.shared_img:
                return pickle.dumps(self.shared_img[:])

        return f

    def run(self):
        self.internal_run.value = 1

        # Define new process to run
        def f():
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            success, image = False,None

            # Run while terminate condition is not set
            while self.terminate_condition.value and self.internal_run:
                # Update shared memory with new image
                success, image = cap.read()
                if success:
                    self.shared_img[:] = pickle.dumps(image)
                # Wait for request to update
                with self.condition_update_img:
                    self.condition_update_img.wait()
        
        # Run new process
        self.process_refference = multiprocessing.Process(target=f)
        self.process_refference.start()

    # Stardard stop function
    def stop(self):
        self.internal_run.value = 0
        self.condition_update_img.notify_all()
        if self.process_refference.is_alive():
            self.process_refference.terminate()
        self.process_refference.close()

    # Forced stop function
    def force_stop(self):
        self.internal_run.value = 0
        self.terminate_condition.value = 0
        self.condition_update_img.notify_all()
        
        if self.process_refference.is_alive():
            self.process_refference.kill()
        self.process_refference.close()




