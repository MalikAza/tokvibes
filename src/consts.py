WIDTH = 600
HEIGHT = 800
FPS = 60
GRAVITY = 0.1
ZOOM_SPEED = 0.25

BALL_RADIUS = 17  # Default radius of the ball
BOUNCE_DAMPENING = 0.98
MIN_VELOCITY = 4
BALL_TRAIL_LENGTH = 15  # Length of the ball trail
SCORE_POSITION_1 = (WIDTH//2 - 80, 30)
SCORE_POSITION_2 = (WIDTH//2 + 20, 30)

FIRST_INNER_CIRCLE_RADIUS = 120  # Radius of the first circle
CIRCLE_ROTATION_SPEED = 0.010  
CIRCLE_SPACING = 12  # Space between each concentric circle
CIRCLE_WIDTH = 5  # Width of the circle lines
HOLE_SIZE_DEGREES = 30  # Size of hole in degrees
HOLE_SHIFT = -15  # Shift of the hole in degrees
DEFAULT_CIRCLE_NUMBERS = 30 # total number of circles
CIRCLE_NUMBERS_DISPLAY = 10
CIRCLE_FADE_OUT_FRAME = 30  
CIRCLE_FADE_IN_FRAME = 40

# Dissolve effect settings
DISSOLVE_SEGMENTS = 40
MIN_CIRCLE_WIDTH = 1 # in pixel so cant be a float

# Fire effect settings
FIRE_PARTICLES = 60          # Maximum number of fire particles per pill
FIRE_LIFETIME = 60           # Lifetime of fire particles in frames
FIRE_SPEED = 0.5             # Base speed of fire particles
SCORE_EFFECT_DURATION = 2    # Duration of score effect in seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)