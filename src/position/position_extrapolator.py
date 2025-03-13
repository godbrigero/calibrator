from enum import Enum
from filterpy.kalman.kalman_filter import KalmanFilter
import numpy as np

from util.position import Position2D

class SensorType(Enum):
    LIDAR = "lidar"
    IMU = "imu"
    APRILTAG = "apriltag"

class Sensor:
    def __init__(self, position: Position2D, type: SensorType, noise_matrix: np.ndarray, vx: float = 0, vy: float = 0):
        self.position = position
        self.type = type
        self.vx = vx
        self.vy = vy
        self.noise_matrix = noise_matrix
    
    def get_state(self):
        return self.position.to_array_with_velocity()

class PositionExtrapolator:
    def __init__(self, map_size_pixels: int, map_size_meters: float, initial_dt: float = 0.1):
        self.map_size_pixels = map_size_pixels
        self.map_size_meters = map_size_meters
        
        self.kf = KalmanFilter(dim_x=6, dim_z=6)
        self.kf.x = np.array([map_size_meters / 2, map_size_meters / 2, 0, 0, 1, 0])
        self.kf.F = np.array([
            [1, 0, initial_dt, 0, 0, 0],
            [0, 1, 0, initial_dt, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])
    
    def update_time_step(self, dt: float):
        self.kf.F[0, 2] = dt
        self.kf.F[1, 3] = dt
    
    def predict(self):
        self.kf.predict()
    
    def update(self, sensor: Sensor):
        self.kf.update(sensor.get_state(), sensor.noise_matrix)
    
    def get_position(self):
        return Position2D(
            self.kf.x[0],
            self.kf.x[1],
            self.kf.x[5],
            self.kf.x[4],
            vx=self.kf.x[2],
            vy=self.kf.x[3]
        )

def fancy_average_slow(positions: list[Position2D]) -> Position2D:
    all_data = np.array([p.to_array_with_velocity() for p in positions])
    medians = np.median(all_data, axis=0)
    distances = np.linalg.norm(all_data - medians, axis=1)
    sigma = 1.0
    weights = np.exp(-0.5 * (distances**2) / sigma**2)
    weights = weights / np.sum(weights)
    
    weighted_avg = np.sum(all_data * weights[:, np.newaxis], axis=0)
    
    x, y, vx, vy, sin, cos = weighted_avg
    
    return Position2D(x, y, sin, cos, vx, vy)

def optimize_array(positions: list[Position2D], weight_threshold: float = 0.01, similarity_threshold: float = 0.1) -> list[Position2D]:
    if len(positions) < 2:
        return positions
    all_data = np.array([p.to_array_with_velocity() for p in positions])
    
    medians = np.median(all_data, axis=0)
    distances = np.linalg.norm(all_data - medians, axis=1)
    
    sigma = 1.0
    weights = np.exp(-0.5 * (distances**2) / sigma**2)
    
    good_weight_mask = weights > weight_threshold
    
    kept_indices = []
    remaining_indices = np.where(good_weight_mask)[0]
    
    while len(remaining_indices) > 0:
        current_idx = remaining_indices[np.argmax(weights[remaining_indices])]
        kept_indices.append(current_idx)
        
        point_distances = np.linalg.norm(
            all_data[remaining_indices] - all_data[current_idx], 
            axis=1
        )
        
        remaining_indices = remaining_indices[point_distances > similarity_threshold]
    
    return [positions[i] for i in kept_indices]