from position.position_extrapolator import PositionExtrapolator
from serialize.serializable_tag_position import SerializableTagPositions
import argparse
import json
from typing import List, Tuple
from pydantic import BaseModel
import numpy as np

from util.position import Position2D, Position3D


class Tag3DPosition(BaseModel):
    x: float
    y: float
    z: float
    direction_vector: List[float]


class SerializableTag3DPositions(BaseModel):
    tag_positions: dict[str, Tag3DPosition]


def sin_cos_to_direction_vector(sin: float, cos: float) -> Tuple[float, float, float]:
    magnitude = np.sqrt(sin * sin + cos * cos)
    if magnitude > 0:
        sin = sin / magnitude
        cos = cos / magnitude

    return (cos, 0, -sin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tag_positions_file", type=str, default="out/tag_positions.json"
    )
    parser.add_argument("--map_size_meters", type=float, default=30)
    parser.add_argument("--map_size_pixels", type=int, default=800)
    parser.add_argument("--output_file", type=str, default="out/tag_positions_3d.json")
    args = parser.parse_args()

    tag_positions = SerializableTagPositions.from_json(args.tag_positions_file)

    new_tag_positions = {}
    tag_positions_dict = tag_positions[0]
    center_position = tag_positions[1]

    center_transform = center_position.transformation_matrix
    center_transform_inv = np.linalg.inv(center_transform)

    for tag_id, tag_pos in tag_positions_dict.items():
        tag_transform = tag_pos.transformation_matrix
        transformed_pos = center_transform_inv @ tag_transform

        direction = sin_cos_to_direction_vector(
            transformed_pos[1, 0], transformed_pos[1, 1]
        )
        new_tag_positions[str(tag_id)] = Tag3DPosition(
            x=transformed_pos[0, 2],
            y=0,
            z=transformed_pos[1, 2],
            direction_vector=list(direction),
        )

    output = SerializableTag3DPositions(tag_positions=new_tag_positions)

    with open(args.output_file, "w") as f:
        f.write(output.model_dump_json(indent=4))
