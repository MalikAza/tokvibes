from abc import ABC
from dataclasses import dataclass
from typing import List

from .ball import Ball
from .circle import Circle

@dataclass
class Args:
    circles: int
    circles_display: int

class GameType(ABC):
    circles: List[Circle]
    balls: List[Ball]