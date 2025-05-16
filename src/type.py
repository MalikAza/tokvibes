from dataclasses import dataclass
from typing import Tuple

@dataclass
class Args:
    circles: int
    circles_display: int

PositionType = Tuple[int, int]
ColorType = Tuple[int, int , int]