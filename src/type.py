from dataclasses import dataclass
from typing import Tuple, TypedDict

@dataclass
class Args:
    circles: int
    circles_display: int

PositionType = Tuple[int, int]
ColorType = Tuple[int, int , int]

class DissolveSegmentType(TypedDict):
    start: float
    end: float
    active: bool
    dissolve_time: int
    alpha_factor: float