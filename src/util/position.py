import numpy as np
from pydantic import BaseModel


class Position2D:
    def __init__(
        self, x: float, y: float, sin: float, cos: float, vx: float = 0, vy: float = 0
    ):
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
        return cls(
            transformation_matrix[0, 2],
            transformation_matrix[1, 2],
            transformation_matrix[1, 0],
            transformation_matrix[1, 1],
        )

    def __str__(self):
        return f"Position2D(x={round(self.x, 2)}, y={round(self.y, 2)}, sin={round(self.sin, 2)}, cos={round(self.cos, 2)})"


class Position3D:
    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        sin: float,
        cos: float,
        vx: float = 0,
        vy: float = 0,
        vz: float = 0,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.sin = sin
        self.cos = cos
        self.vx = vx
        self.vy = vy
        self.vz = vz

        self.transformation_matrix = make_transformation_matrix_3d(
            np.array([self.x, self.y, self.z]), np.array([self.cos, 0, self.sin])
        )


def get_transformation_matrix_2d(position: Position2D):
    return np.array(
        [
            [position.cos, -position.sin, position.x],
            [position.sin, position.cos, position.y],
            [0, 0, 1],
        ]
    )


def make_transformation_matrix_3d(
    position: np.ndarray,
    direction_vector: np.ndarray,
) -> np.ndarray:
    z_axis = np.array(direction_vector)
    z_axis = z_axis / np.linalg.norm(z_axis)

    x_axis = np.cross(np.array([0, 1, 0]), z_axis)
    x_axis = x_axis / np.linalg.norm(x_axis)

    y_axis = np.cross(z_axis, x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)

    return create_transformation_matrix_3d(
        np.column_stack((x_axis, y_axis, z_axis)),
        np.array([position[0], position[1], position[2]]),
    )


def create_transformation_matrix_3d(
    rotation_matrix: np.ndarray, translation_vector: np.ndarray
) -> np.ndarray:
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation_matrix
    transformation_matrix[:3, 3] = translation_vector

    return transformation_matrix
