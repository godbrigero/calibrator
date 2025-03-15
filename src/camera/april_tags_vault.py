from pydantic import BaseModel
from position.position_extrapolator import fancy_average_slow, optimize_array
from util.position import Position2D
import pyapriltags

'''
class SerializableAprilTagsVault(BaseModel):
    tags: dict[int, list[Position2D]]
'''
class AprilTagsVault:
    def __init__(self, optimize_every_n_tags: int = 10, weight_threshold: float = 0.01, similarity_threshold: float = 0.1):
        self.tags: dict[int, list[Position2D]] = {}
        self.optimize_every_n_tags = optimize_every_n_tags
        self.total_tags = 0
        self.weight_threshold = weight_threshold
        self.similarity_threshold = similarity_threshold
    
    def add_tag_on_field(self, tag: Position2D, id: int):
        if id not in self.tags:
            self.tags[id] = []
        
        self.tags[id].append(tag)
        
        self.total_tags += 1
        if self.total_tags >= self.optimize_every_n_tags:
            self.optimize_tags()
    
    def get_estimated_tag_position(self, id: int) -> Position2D | None:
        if id not in self.tags:
            return None
        
        return fancy_average_slow(self.tags[id])
    
    def optimize_tags(self):
        for id in self.tags:
            self.tags[id] = optimize_array(self.tags[id], self.weight_threshold, self.similarity_threshold)
    
    def get_all_estimated_tags(self) -> dict[int, Position2D]:
        output = {}
        for key in self.tags.keys():
            output[key] = self.get_estimated_tag_position(key)
        
        return output

    

def from_tags_detection_to_pos2d(tags_detection: pyapriltags.Detection) -> Position2D:
    assert tags_detection.pose_t is not None
    assert tags_detection.pose_R is not None
    
    return Position2D(tags_detection.pose_t[2][0], tags_detection.pose_t[0][0], tags_detection.pose_R[2, 0], -tags_detection.pose_R[2, 2])
