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

    def __str__(self):
        return f"Tag3DPosition(x={round(self.x, 2)}, y={round(self.y, 2)}, z={round(self.z, 2)}, direction_vector={round(self.direction_vector[0], 2)}, {round(self.direction_vector[1], 2)})"


class SerializableTag3DPositions(BaseModel):
    tag_positions: dict[str, Tag3DPosition]


def sin_cos_to_direction_vector(sin: float, cos: float) -> Tuple[float, float]:
    magnitude = np.sqrt(sin * sin + cos * cos)
    if magnitude > 0:
        sin = sin / magnitude
        cos = cos / magnitude

    return (cos, sin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tag_positions_file", type=str, default="out/tag_positions.json"
    )
    parser.add_argument("--map_size_meters", type=float, default=30)
    parser.add_argument("--map_size_pixels", type=int, default=800)
    parser.add_argument("--output_file", type=str, default="out/tag_positions_3d.json")
    parser.add_argument("--use_center_position", type=bool, default=True)
    args = parser.parse_args()

    tag_positions = SerializableTagPositions.from_json(args.tag_positions_file)

    new_tag_positions = {}
    tag_positions_dict = tag_positions[0]
    center = tag_positions[1]
    for tag_id, tag_pos in tag_positions_dict.items():
        tag_transform = tag_pos.transformation_matrix

        direction = sin_cos_to_direction_vector(
            tag_transform[1, 0], tag_transform[1, 1]
        )
        new_tag_positions[str(tag_id)] = Tag3DPosition(
            x=center.x - tag_transform[0, 2],
            y=tag_transform[1, 2] - center.y,
            z=0,
            direction_vector=[-direction[0], direction[1], 0.0],
        )

        print(tag_id, new_tag_positions[str(tag_id)])

    output = SerializableTag3DPositions(tag_positions=new_tag_positions)

    with open(args.output_file, "w") as f:
        f.write(output.model_dump_json(indent=4))
