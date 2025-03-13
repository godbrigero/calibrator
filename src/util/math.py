import numpy as np
from util.position import Position2D


def get_transformation_matrix_2d(position: Position2D):
    return np.array([
        [position.cos, -position.sin, position.x],
        [position.sin, position.cos, position.y],
        [0, 0, 1]
    ])

def reverse_radians(radians):
    return radians - np.pi

def to_tag_global_position(tag_position: Position2D, camera_position_local: Position2D, camera_position_global: Position2D) -> Position2D:
    T_tag_camera = tag_position.transformation_matrix
    T_camera_global = camera_position_global.transformation_matrix
    T_camera_local = camera_position_local.transformation_matrix # TODO
    
    return Position2D.from_2d_transformation_matrix(T_camera_global @ T_tag_camera)

def get_position_pixels(position: Position2D, map_size_meters: float, map_size_pixels: int) -> Position2D:
    return Position2D(
        position.x * map_size_pixels / map_size_meters,
        position.y * map_size_pixels / map_size_meters,
        position.sin,
        position.cos
    )