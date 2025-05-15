import argparse
from dataclasses import dataclass
import pygame

from .game import Game
from .consts import DEFAULT_CIRCLE_NUMBERS, HEIGHT, WIDTH


@dataclass
class Args:
    circles: int

def __parse_cli() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--circles',
        type=int,
        default=DEFAULT_CIRCLE_NUMBERS,
        help="Number of circles"
    )
    parsed = parser.parse_args()

    return Args(
        circles=parsed.circles
    )

def __init_game() -> Game:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TikTok Circles")

    args = __parse_cli()

    return Game(screen, args.circles)

def run() -> None:
    game = __init_game()
    game.run()