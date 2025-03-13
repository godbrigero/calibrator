from threading import Thread
from typing import Callable
import cv2
import numpy as np
import pyapriltags


class AprilTagDetector(Thread):
    def __init__(
        self,
        camera_matrix: np.ndarray,
        distortion_coefficients: np.ndarray,
        on_tag_detected: Callable[[pyapriltags.Detection], None],
        tag_size: float,
        resolution: tuple[int, int] = (640, 480),
        family: str = "tag36h11",
        nthreads: int = 1,
        quad_decimate: float = 2.0,
        quad_sigma: float = 0.0,
        refine_edges: int = 1,
        decode_sharpening: float = 0.25,
    ):
        super().__init__()
        self.detector = pyapriltags.Detector(
            families=family,
            nthreads=nthreads,
            quad_decimate=quad_decimate,
            quad_sigma=quad_sigma,
            refine_edges=refine_edges,
            decode_sharpening=decode_sharpening
        )
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.is_running = False
        
        self.camera_matrix = camera_matrix
        self.distortion_coefficients = distortion_coefficients
        self.tag_size = tag_size
        self.on_tag_detected = on_tag_detected
        
    def run(self):
        self.is_running = True
        while self.is_running:
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                break
            
            undistorted_frame = cv2.undistort(self.frame, self.camera_matrix, self.distortion_coefficients)
            gray_frame = cv2.cvtColor(undistorted_frame, cv2.COLOR_BGR2GRAY)
            fx, fy, cx, cy = (
                self.camera_matrix[0, 0],
                self.camera_matrix[1, 1],
                self.camera_matrix[0, 2],
                self.camera_matrix[1, 2],
            )
            
            detections = self.detector.detect(
                gray_frame,
                estimate_tag_pose=True,
                camera_params=(fx, fy, cx, cy),
                tag_size=self.tag_size,
            )
            
            if detections:
                for detection in detections:
                    if self.on_tag_detected is not None:
                        self.on_tag_detected(detection)                    
    
    def get_frame(self):
        if self.frame is None:
            return np.zeros(
                (480, 640, 3), dtype=np.uint8
            )
        
        return self.frame
    
    def stop(self):
        self.is_running = False
        self.cap.release()
