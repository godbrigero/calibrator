import cv2
from matplotlib import pyplot as plt
import numpy as np
import pyapriltags
from BreezySLAM.python.breezyslam.algorithms import RMHC_SLAM
from camera.april_tags_vault import AprilTagsVault, from_tags_detection_to_pos2d
from camera.detector import AprilTagDetector
from lidar.rp_lidar import RPLidarA1
from lidar.slam import RPLidarSLAM
from util.math import get_position_pixels
from util.visual import render_position

camera_matrix = np.array([[615.164, 0, 320], [0, 615.164, 240], [0, 0, 1]])
distortion_coefficients = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
tag_size = 0.05
map_size_pixels = 800
map_size_meters = 30
port = "/dev/tty.usbserial-210"
baudrate = 256000

SLAM = RMHC_SLAM(
    RPLidarA1(),
    map_size_pixels,
    map_size_meters,
    map_quality=1,
    hole_width_mm=300,
    random_seed=42,
    max_search_iter=1000,
)

def main():
    is_stopped = False
    april_tag_vault = AprilTagsVault(optimize_every_n_tags=100)
    
    def on_tag_detected(detection: pyapriltags.Detection):
        april_tag_vault.add_tag_on_field(from_tags_detection_to_pos2d(detection), detection.tag_id)
    
    detector = AprilTagDetector(camera_matrix, distortion_coefficients, on_tag_detected, tag_size, nthreads=4, resolution=(1280, 720))
    detector.start()
    
    slam = RPLidarSLAM(SLAM, port, baudrate, map_size_pixels, map_size_meters)
    slam.start()
    
    while not is_stopped:
        plt.clf()
        plt.imshow(slam.get_map(), cmap="gray")
        render_position(slam.get_position_pixels(), "red")
        
        for tag_id, tag_pos in april_tag_vault.get_all_estimated_tags().items():
            tag_pos_pixels = get_position_pixels(tag_pos, map_size_meters, map_size_pixels)
            render_position(tag_pos_pixels, "blue")
            plt.text(tag_pos_pixels.x, tag_pos_pixels.y, str(tag_id), color="blue")
        
        plt.pause(0.01)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_stopped = True

if __name__ == "__main__":
    main()