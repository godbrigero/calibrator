import numpy as np
from util.position import Position2D

def reverse_radians(radians):
    return radians - np.pi

def to_tag_global_position(tag_position: Position2D, camera_position_local: Position2D, camera_position_global: Position2D, map_size_meters: float) -> Position2D:
    T_tag_camera = tag_position.transformation_matrix
    T_camera_global = camera_position_global.transformation_matrix
    T_camera_local = camera_position_local.transformation_matrix # TODO
    
    pos_global = Position2D.from_2d_transformation_matrix(T_camera_global @ T_tag_camera)
    # pos_global = Position2D(pos_global.x + map_size_meters / 2, pos_global.y + map_size_meters / 2, pos_global.sin, pos_global.cos)

    return pos_global

def get_position_pixels(position: Position2D, map_size_meters: float, map_size_pixels: int) -> Position2D:
    return Position2D(
        position.x * map_size_pixels / map_size_meters,
        position.y * map_size_pixels / map_size_meters,
        position.sin,
        position.cos
    )

def get_position_on_map(position_tag_local: Position2D, position_tag_global: Position2D) -> Position2D:
    T_tag_camera = position_tag_local.transformation_matrix
    T_tag_world = position_tag_global.transformation_matrix
    T_world_camera = T_tag_world @ np.linalg.inv(T_tag_camera)
    
    return Position2D.from_2d_transformation_matrix(T_world_camera)
