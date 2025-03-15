from threading import Thread
import time

import numpy as np

from breezyslam.algorithms import RMHC_SLAM
from rplidar import RPLidar
from scipy.interpolate import interp1d

from util.math import reverse_radians
from util.position import Position2D


class RPLidarSLAM(Thread):
    def __init__(
        self,
        slam: RMHC_SLAM,
        port="/dev/tty.usbserial-210",
        baudrate=256000,
        map_size_pixels=800,
        map_size_meters=30,
    ):
        super().__init__()
        
        self.slam = slam
        self.port = port
        self.baudrate = baudrate
        self.map_size_pixels = map_size_pixels
        self.map_size_meters = map_size_meters
        
        self.mapbytes = bytearray(map_size_pixels * map_size_pixels)
        self.lidar = RPLidar(self.port, baudrate=self.baudrate)
        
        self.is_running = False
        self.is_connected = False
    
    def run(self):
        self.is_running = True
        self.warmup_lidar()
        
        next_generator = self.lidar.iter_scans()
        while self.is_running and self.is_connected:
            scan = next(next_generator)
            
            distances = [item[2] for item in scan]
            angles = [item[1] for item in scan]
            f = interp1d(
                angles, distances, bounds_error=False, fill_value=0
            )
            interpolated_distances = list(f(np.arange(360)))
            
            self.slam.update(interpolated_distances)
    
    def warmup_lidar(self):
        while self.is_running and not self.is_connected:
            try:
                print("Attempting to connect to LiDAR...")
                # Initialize RPLidar inside the thread
                self.lidar = RPLidar(self.port, baudrate=self.baudrate)

                # Reset sequence
                self.lidar.stop()
                self.lidar.stop_motor()
                time.sleep(1)  # Give it time to stop
                self.lidar.disconnect()
                
                time.sleep(1)
                self.lidar = RPLidar(self.port, baudrate=self.baudrate)
                self.lidar.start_motor()
                time.sleep(1)  # Wait for motor to reach speed

                # Test connection by getting first scan
                print("Testing LiDAR connection...")
                next(self.lidar.iter_scans())
                print("Successfully connected to LiDAR!")
                self.is_connected = True
                break
            except Exception as e:
                self.lidar = RPLidar(self.port, baudrate=self.baudrate)
                print(f"Failed to connect to LiDAR: {e}")
                print("Retrying in 0.5 seconds...")
                time.sleep(0.5)
    
    def stop(self):
        self.is_running = False
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()
    
    def get_position_meters(self) -> Position2D:
        x, y, theta = self.slam.getpos()
        theta = reverse_radians(np.radians(theta))
        
        return Position2D(x / 1000, y / 1000, np.sin(theta), np.cos(theta))

    def get_position_pixels(self) -> Position2D:
        position = self.get_position_meters()
        return Position2D(
            position.x * self.map_size_pixels / self.map_size_meters,
            position.y * self.map_size_pixels / self.map_size_meters,
            position.sin,
            position.cos
        )
    
    def get_map(self):
        self.slam.getmap(self.mapbytes)
        
        return np.frombuffer(self.mapbytes, dtype=np.uint8).reshape(
            self.map_size_pixels, self.map_size_pixels
        )
