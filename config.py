# config.py

# --- Canvas and Border ---
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
BORDER_THICKNESS = 15 # Thickness of the border around the edge
BORDER_COLOR = "black" # Color of the border

# --- Shape and Element Counts ---
NUM_RANDOM_DOTS = 30
NUM_RANDOM_LINES = 10
NUM_RANDOM_RECTANGLES = 5
NUM_RANDOM_CIRCLES = 5
NUM_RANDOM_POLYGONS = 4
NUM_RANDOM_CUBES = 3
NUM_RANDOM_PYRAMIDS = 3
NUM_RANDOM_PRISMS = 3
NUM_CONNECTIONS = 5        # How many connecting lines to draw between static shapes

# --- Size and Style Constants ---
MIN_DOT_SIZE = 1
MAX_DOT_SIZE = 6
MIN_LINE_THICKNESS = 1
MAX_LINE_THICKNESS = 4
MIN_RECT_OUTLINE = 1
MAX_RECT_OUTLINE = 5
MIN_CIRCLE_OUTLINE = 1
MAX_CIRCLE_OUTLINE = 5
MIN_POLYGON_OUTLINE = 1
MAX_POLYGON_OUTLINE = 5
MIN_SHAPE_SIZE = 20
MAX_SHAPE_SIZE_LIMIT = 70 # Max preferred size, will be constrained by canvas inner dimensions
MIN_POLYGON_VERTICES = 3
MAX_POLYGON_VERTICES = 7
MIN_CUBE_SIZE = 15
MAX_CUBE_SIZE = 40
MIN_PYRAMID_BASE = 15
MAX_PYRAMID_BASE = 45
MIN_PYRAMID_HEIGHT_FACTOR = 0.8 # Relative to base size
MAX_PYRAMID_HEIGHT_FACTOR = 1.5
MIN_PRISM_DIM = 10 # Min dimension for width/depth/height
MAX_PRISM_DIM = 40 # Max dimension for width/depth/height
SHAPE_PLACEMENT_ATTEMPTS = 100
CONNECTION_LINE_COLOR = "grey50" # Color for connecting lines
CONNECTION_LINE_WIDTH = 1        # Width for connecting lines

# --- Background Style ---
NUM_FAINT_SHAPES_MIN = 4
NUM_FAINT_SHAPES_MAX = 8
FAINT_SHAPE_MIN_SCALE = 0.4 # Min size relative to canvas dimension
FAINT_SHAPE_MAX_SCALE = 1.2 # Max size relative to canvas dimension
FAINT_COLOR_MIN_BRIGHTNESS = 190
FAINT_COLOR_MAX_BRIGHTNESS = 245

# --- Animation Constants ---
NUM_ANIMATED_SHAPES = 2  # How many shapes to animate
UPDATE_INTERVAL_MS = 50  # Milliseconds between animation frames (e.g., 50ms = 20 FPS)
MOVEMENT_SPEED = 0.8     # Pixels to move per frame
COLOR_FADE_STEPS = 150   # How many steps (frames) a color fade should take

# --- Calculated Inner Bounds (dependent on other constants) ---
# These are calculated here for convenience but used in main.py
INNER_X_MIN = BORDER_THICKNESS
INNER_Y_MIN = BORDER_THICKNESS
INNER_X_MAX = CANVAS_WIDTH - BORDER_THICKNESS
INNER_Y_MAX = CANVAS_HEIGHT - BORDER_THICKNESS
INNER_WIDTH = CANVAS_WIDTH - 2 * BORDER_THICKNESS
INNER_HEIGHT = CANVAS_HEIGHT - 2 * BORDER_THICKNESS

# Adjust MAX_SHAPE_SIZE based on inner dimensions
MAX_SHAPE_SIZE = min(MAX_SHAPE_SIZE_LIMIT, INNER_WIDTH, INNER_HEIGHT)

