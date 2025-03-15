import numpy as np
from pydantic import BaseModel


class Position2D:
    def __init__(self, x: float, y: float, sin: float, cos: float, vx: float = 0, vy: float = 0):
        self.x = x
        self.y = y
        self.sin = sin
        self.cos = cos
        self.vx = vx
        self.vy = vy
        
        self.transformation_matrix = get_transformation_matrix_2d(self)
    
    def to_array(self):
        return np.array([self.x, self.y, self.sin, self.cos])
    
    def to_array_with_velocity(self):
        return np.array([self.x, self.y, self.vx, self.vy, self.sin, self.cos])
    
    @classmethod
    def from_2d_transformation_matrix(cls, transformation_matrix: np.ndarray):
        return cls(transformation_matrix[0, 2], transformation_matrix[1, 2], transformation_matrix[1, 0], transformation_matrix[1, 1])

def get_transformation_matrix_2d(position: Position2D):
    return np.array([
        [position.cos, -position.sin, position.x],
        [position.sin, position.cos, position.y],
        [0, 0, 1]
    ])