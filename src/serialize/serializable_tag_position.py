import numpy as np
from pydantic import BaseModel
from typing import Sequence

from util.position import Position2D

class SerializableTagPositions(BaseModel):
    tag_positions: dict[int, list[float]]
    
    @classmethod
    def from_tag_positions(cls, tag_positions: dict[int, Position2D]):
        return cls(tag_positions={tag_id: from_np_transformation_matrix_to_list(tag_position.transformation_matrix) for tag_id, tag_position in tag_positions.items()})

    @classmethod
    def from_json(cls, file_path: str) -> dict[int, Position2D]:
        serializable_tag_positions = SerializableTagPositions.model_validate_json(open(file_path).read())
        return {tag_id: Position2D.from_2d_transformation_matrix(from_list_to_np_transformation_matrix(tag_position)) for tag_id, tag_position in serializable_tag_positions.tag_positions.items()}

def from_np_transformation_matrix_to_list(transformation_matrix: np.ndarray) -> list[float]:
    return transformation_matrix.astype(np.float64).flatten().tolist()

def from_list_to_np_transformation_matrix(transformation_matrix: Sequence[float]) -> np.ndarray:
    return np.array(transformation_matrix).reshape(2, 2)
