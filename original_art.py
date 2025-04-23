import tkinter as tk
import random
import math

# --- Constants for better readability ---
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
BORDER_THICKNESS = 15 # Thickness of the border around the edge
BORDER_COLOR = "black" # Color of the border

# Calculate inner bounds (area where shapes can be drawn and animated)
INNER_X_MIN = BORDER_THICKNESS
INNER_Y_MIN = BORDER_THICKNESS
INNER_X_MAX = CANVAS_WIDTH - BORDER_THICKNESS
INNER_Y_MAX = CANVAS_HEIGHT - BORDER_THICKNESS
INNER_WIDTH = CANVAS_WIDTH - 2 * BORDER_THICKNESS
INNER_HEIGHT = CANVAS_HEIGHT - 2 * BORDER_THICKNESS

# --- Shape and Element Counts ---
NUM_RANDOM_DOTS = 30
NUM_RANDOM_LINES = 10
NUM_RANDOM_RECTANGLES = 5 # Adjusted slightly
NUM_RANDOM_CIRCLES = 5    # Adjusted slightly
NUM_RANDOM_POLYGONS = 4    # Adjusted slightly
NUM_RANDOM_CUBES = 3       # Adjusted slightly
NUM_RANDOM_PYRAMIDS = 3    # <<< Added
NUM_RANDOM_PRISMS = 3      # <<< Added
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
# Ensure max shape size doesn't exceed inner dimensions
MAX_SHAPE_SIZE = min(70, INNER_WIDTH, INNER_HEIGHT)
MIN_POLYGON_VERTICES = 3
MAX_POLYGON_VERTICES = 7
MIN_CUBE_SIZE = 15
MAX_CUBE_SIZE = 40
MIN_PYRAMID_BASE = 15 # <<< Added
MAX_PYRAMID_BASE = 45 # <<< Added
MIN_PYRAMID_HEIGHT_FACTOR = 0.8 # <<< Added (Relative to base size)
MAX_PYRAMID_HEIGHT_FACTOR = 1.5 # <<< Added
MIN_PRISM_DIM = 10 # <<< Added (Min dimension for width/depth/height)
MAX_PRISM_DIM = 40 # <<< Added (Max dimension for width/depth/height)
SHAPE_PLACEMENT_ATTEMPTS = 100
CONNECTION_LINE_COLOR = "grey50" # Color for connecting lines
CONNECTION_LINE_WIDTH = 1        # Width for connecting lines

# --- Animation Constants ---
NUM_ANIMATED_SHAPES = 2  # How many shapes to animate (e.g., 1 or 2)
UPDATE_INTERVAL_MS = 50  # Milliseconds between animation frames (e.g., 50ms = 20 FPS)
MOVEMENT_SPEED = 0.8     # Pixels to move per frame (can be float for slower movement)
COLOR_FADE_STEPS = 150   # How many steps (frames) a color fade should take (higher is slower)

# --- Global list to hold shapes we want to animate ---
animated_shapes = []
canvas = None # Will be assigned later
placed_shapes_data = [] # Will store data about placed shapes

# --- Helper function for random colors ---
def get_random_color():
    """Generates a random hex color code."""
    return f'#{random.randint(0, 0xFFFFFF):06x}'

# --- Helper function for faint colors (for background) ---
def get_random_faint_color(min_brightness=190, max_brightness=245):
    """Generates a random hex color code that is relatively light/pale."""
    try:
        r = random.randint(min_brightness, max_brightness)
        g = random.randint(min_brightness, max_brightness)
        b = random.randint(min_brightness, max_brightness)
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        return f'#{r:02x}{g:02x}{b:02x}'
    except ValueError:
        print(f"Warning: Invalid brightness range ({min_brightness}-{max_brightness}). Using default grey.")
        return "#DDDDDD"

# --- Color Helpers for Animation and Shading ---
def hex_to_rgb(hex_color):
    """Converts a hex color string (e.g., '#ffffff') to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6: return (0, 0, 0)
    try: return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError: return (0, 0, 0)

def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple to a hex color string."""
    rgb = tuple(max(0, min(255, int(c))) for c in rgb)
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

def interpolate_color(color1_hex, color2_hex, factor):
    """Finds a color between color1 and color2. factor = 0.0 -> color1, factor = 1.0 -> color2."""
    rgb1 = hex_to_rgb(color1_hex)
    rgb2 = hex_to_rgb(color2_hex)
    new_rgb = [rgb1[i] + (rgb2[i] - rgb1[i]) * factor for i in range(3)]
    return rgb_to_hex(tuple(new_rgb))

def adjust_brightness(hex_color, factor):
    """Adjusts the brightness of a hex color by a factor."""
    rgb = hex_to_rgb(hex_color)
    if not rgb: return hex_color # Return original if conversion failed

    # Adjust each component, clamping between 0 and 255
    new_rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
    return rgb_to_hex(new_rgb)

# --- Helper function to generate polygon points (adjusted for border) ---
def generate_random_polygon_points(center_x, center_y, avg_radius, irregularity, spikeyness, num_vertices):
    """Generates points for a random polygon, respecting inner bounds."""
    points = []
    angle_step = 2 * math.pi / num_vertices
    for i in range(num_vertices):
        angle = i * angle_step
        radius = random.gauss(avg_radius, avg_radius * irregularity)
        radius = max(MIN_SHAPE_SIZE / 2, radius) # Ensure minimum radius
        angle += random.gauss(0, angle_step * spikeyness * 0.5)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        # Ensure points stay within the inner canvas bounds
        x = max(INNER_X_MIN, min(INNER_X_MAX, x))
        y = max(INNER_Y_MIN, min(INNER_Y_MAX, y))
        points.extend([x, y])
    return points

# --- Helper function to check bounding box overlap ---
def check_overlap(box1, box2):
    """Checks if two bounding boxes (x1, y1, x2, y2) overlap."""
    if not box1 or len(box1) != 4 or not box2 or len(box2) != 4:
        return False
    # Check for invalid bounds where min > max
    if box1[0] > box1[2] or box1[1] > box1[3] or box2[0] > box2[2] or box2[1] > box2[3]:
        return False # Invalid box definition
    # Standard overlap check
    if box1[2] < box2[0] or box1[0] > box2[2] or box1[3] < box2[1] or box1[1] > box2[3]:
        return False
    return True

# --- Helper function to get polygon bounding box ---
def get_polygon_bounds(points):
    """Calculates the bounding box (x1, y1, x2, y2) for a list of polygon points."""
    if not points or len(points) < 2: return (0, 0, 0, 0)
    x_coords = points[0::2]
    y_coords = points[1::2]
    if not x_coords or not y_coords: return (0,0,0,0)
    return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

# --- Helper function to draw Isometric Cube ---
def draw_isometric_cube(canvas_obj, center_x, center_y, size, color):
    """
    Draws an isometric cube on the canvas with simple shading.
    Returns the 2D bounding box of the drawn cube.
    """
    offset_x = size * 0.866 # approx sqrt(3)/2
    offset_y = size * 0.5   #

    # Define the 7 visible points in 2D screen coordinates relative to center
    points = [
        (center_x, center_y - size),                     # Top point (0)
        (center_x - offset_x, center_y - offset_y),      # Top-Left (1)
        (center_x, center_y),                            # Center (where faces meet) (2)
        (center_x + offset_x, center_y - offset_y),      # Top-Right (3)
        (center_x - offset_x, center_y + offset_y),      # Bottom-Left (4)
        (center_x, center_y + size),                     # Bottom-Middle (5)
        (center_x + offset_x, center_y + offset_y)       # Bottom-Right (6)
    ]

    # Define the three visible faces using point indices
    top_face = [points[0], points[1], points[2], points[3]]
    left_face = [points[1], points[4], points[5], points[2]]
    right_face = [points[3], points[6], points[5], points[2]]

    # Simple shading
    top_color = adjust_brightness(color, 1.2)  # Lighter top
    left_color = adjust_brightness(color, 0.8) # Darker left
    right_color = adjust_brightness(color, 0.6) # Darkest right (or adjust factors)

    # Outline color can be black or derived from the base color
    outline_col = "black" # adjust_brightness(color, 0.4)

    # Draw faces (draw darker faces first, potentially)
    canvas_obj.create_polygon(left_face, fill=left_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(right_face, fill=right_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(top_face, fill=top_color, outline=outline_col, width=1)

    # Calculate the 2D bounding box of the drawn cube
    all_x = [p[0] for p in points]
    all_y = [p[1] for p in points]
    bounds = (min(all_x), min(all_y), max(all_x), max(all_y))

    return bounds

# --- Helper function to draw Isometric Square Pyramid ---
def draw_isometric_pyramid(canvas_obj, center_x, center_y, base_size, height_factor, color):
    """
    Draws an isometric square pyramid on the canvas with simple shading.
    Returns the 2D bounding box of the drawn pyramid.
    Base center is offset slightly below the provided center_y for visual balance.
    """
    base_offset_x = base_size * 0.866 / 2 # Half base diagonal projection
    base_offset_y = base_size * 0.5 / 2   # Half base diagonal projection
    pyramid_height = base_size * height_factor

    # Adjust center slightly so the visual bulk is around center_x, center_y
    base_center_y = center_y + pyramid_height * 0.2 # Lower the base center slightly

    # Define the 5 points (4 base corners, 1 apex)
    apex = (center_x, base_center_y - pyramid_height) # Top point (0)
    base_front = (center_x, base_center_y + base_offset_y * 2) # Base point closest (1) - Approximation
    base_left = (center_x - base_offset_x * 2, base_center_y) # Base left corner (2)
    base_back = (center_x, base_center_y - base_offset_y * 2) # Base point furthest (3) - Approximation (hidden often)
    base_right = (center_x + base_offset_x * 2, base_center_y) # Base right corner (4)

    # Define the visible faces (usually 2 sides and maybe part of base)
    # We'll draw the two front-facing triangles
    left_face = [apex, base_left, base_front]
    right_face = [apex, base_right, base_front]

    # Simple shading
    left_color = adjust_brightness(color, 0.85) # Slightly darker left
    right_color = adjust_brightness(color, 0.65) # Darker right

    outline_col = "black" # adjust_brightness(color, 0.4)

    # Draw faces
    # Note: A full base isn't typically drawn in simple isometric views unless tilted.
    # We draw the two visible triangular faces.
    canvas_obj.create_polygon(left_face, fill=left_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(right_face, fill=right_color, outline=outline_col, width=1)

    # Calculate the 2D bounding box
    # Use only the drawn points for bounds: apex, base_front, base_left, base_right
    all_x = [p[0] for p in [apex, base_front, base_left, base_right]]
    all_y = [p[1] for p in [apex, base_front, base_left, base_right]]
    bounds = (min(all_x), min(all_y), max(all_x), max(all_y))

    return bounds

# --- Helper function to draw Isometric Rectangular Prism (Cuboid) ---
def draw_isometric_prism(canvas_obj, center_x, center_y, width, depth, height, color):
    """
    Draws an isometric rectangular prism (cuboid) on the canvas with simple shading.
    Width corresponds to the X-diagonal axis, Depth to the Y-diagonal axis, Height is vertical.
    Returns the 2D bounding box of the drawn prism.
    """
    # Calculate offsets based on dimensions
    offset_x_w = width * 0.866 / 2
    offset_y_w = width * 0.5 / 2
    offset_x_d = depth * 0.866 / 2
    offset_y_d = depth * 0.5 / 2
    offset_y_h = height / 2

    # Define the 8 corners relative to the center
    # Bottom face corners
    p0 = (center_x - offset_x_w + offset_x_d, center_y + offset_y_w + offset_y_d - offset_y_h) # Bottom front-left
    p1 = (center_x + offset_x_w + offset_x_d, center_y - offset_y_w + offset_y_d - offset_y_h) # Bottom back-left (often hidden)
    p2 = (center_x + offset_x_w - offset_x_d, center_y - offset_y_w - offset_y_d - offset_y_h) # Bottom back-right
    p3 = (center_x - offset_x_w - offset_x_d, center_y + offset_y_w - offset_y_d - offset_y_h) # Bottom front-right
    # Top face corners (directly above bottom corners)
    p4 = (p0[0], p0[1] + height) # Top front-left
    p5 = (p1[0], p1[1] + height) # Top back-left (often hidden)
    p6 = (p2[0], p2[1] + height) # Top back-right
    p7 = (p3[0], p3[1] + height) # Top front-right

    # Define the three visible faces (Top, Front-Left, Front-Right)
    # Note: Indices match the points p0-p7 defined above
    top_face = [p4, p5, p6, p7] # Top face
    left_face = [p0, p3, p7, p4] # Front-Left face (using p0, p3, p7, p4)
    right_face = [p3, p2, p6, p7] # Front-Right face (using p3, p2, p6, p7)

    # Simple shading
    top_color = adjust_brightness(color, 1.2)  # Lighter top
    left_color = adjust_brightness(color, 0.8) # Darker left
    right_color = adjust_brightness(color, 0.6) # Darkest right

    outline_col = "black" # adjust_brightness(color, 0.4)

    # Draw faces (draw darker faces first, potentially)
    canvas_obj.create_polygon(left_face, fill=left_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(right_face, fill=right_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(top_face, fill=top_color, outline=outline_col, width=1)

    # Calculate the 2D bounding box of the drawn prism (using all 8 points for safety)
    all_points = [p0, p1, p2, p3, p4, p5, p6, p7]
    all_x = [p[0] for p in all_points]
    all_y = [p[1] for p in all_points]
    bounds = (min(all_x), min(all_y), max(all_x), max(all_y))

    return bounds


# --- Animation Logic ---

def assign_new_target_position(shape_info):
    """Assigns a new random target position within INNER bounds for an animated shape."""
    global canvas
    if not canvas: return

    canvas_item_id = shape_info['id']
    try:
        current_coords = canvas.coords(canvas_item_id)
        if not current_coords or len(current_coords) < 4:
             shape_info['move_steps_remaining'] = 0
             return
    except tk.TclError:
        shape_info['move_steps_remaining'] = 0
        return

    # Determine current width/height based on shape type
    if shape_info['type'] in ['rectangle', 'oval']:
        curr_x1, curr_y1, curr_x2, curr_y2 = current_coords
        curr_w = curr_x2 - curr_x1
        curr_h = curr_y2 - curr_y1
    elif shape_info['type'] == 'polygon':
        bounds = get_polygon_bounds(current_coords)
        curr_x1, curr_y1, curr_x2, curr_y2 = bounds
        curr_w = curr_x2 - curr_x1
        curr_h = curr_y2 - curr_y1
    else: # Unknown type
        shape_info['move_steps_remaining'] = 0
        return

    # Define movement bounds (INNER area)
    min_x = INNER_X_MIN
    min_y = INNER_Y_MIN
    max_x = INNER_X_MAX - curr_w # Target top-left so right edge is at INNER_X_MAX
    max_y = INNER_Y_MAX - curr_h # Target top-left so bottom edge is at INNER_Y_MAX

    if max_x <= min_x: max_x = min_x + 1
    if max_y <= min_y: max_y = min_y + 1

    target_x1 = random.randint(min_x, int(max_x))
    target_y1 = random.randint(min_y, int(max_y))

    # Calculate movement steps and deltas
    current_pos_x = current_coords[0] if shape_info['type'] != 'polygon' else curr_x1
    current_pos_y = current_coords[1] if shape_info['type'] != 'polygon' else curr_y1

    delta_x = target_x1 - current_pos_x
    delta_y = target_y1 - current_pos_y
    distance = math.sqrt(delta_x**2 + delta_y**2)

    if distance < MOVEMENT_SPEED:
        shape_info['move_steps_remaining'] = 0
        shape_info['dx'] = 0
        shape_info['dy'] = 0
    else:
        steps_needed = max(1, int(distance / MOVEMENT_SPEED))
        shape_info['move_steps_remaining'] = steps_needed
        shape_info['dx'] = delta_x / steps_needed
        shape_info['dy'] = delta_y / steps_needed
        shape_info['target_coords'] = [target_x1, target_y1] # Store target top-left


def update_animation(canvas_obj, root):
    """The main animation loop function."""
    global animated_shapes

    shapes_to_remove_indices = []

    for i, shape in enumerate(animated_shapes):
        shape_id = shape['id']
        try:
            # --- Update Color ---
            if shape['color_step'] < COLOR_FADE_STEPS:
                shape['color_step'] += 1
                factor = shape['color_step'] / COLOR_FADE_STEPS
                new_fill = interpolate_color(shape['current_fill'], shape['target_fill'], factor)
                new_outline = shape['current_outline']
                if 'target_outline' in shape:
                     new_outline = interpolate_color(shape['current_outline'], shape['target_outline'], factor)

                config_opts = {'fill': new_fill}
                if 'target_outline' in shape:
                    config_opts['outline'] = new_outline
                canvas_obj.itemconfig(shape_id, **config_opts)

            else: # Reached target color, pick new targets and reset
                shape['current_fill'] = shape['target_fill']
                shape['target_fill'] = get_random_color()
                if 'target_outline' in shape:
                    shape['current_outline'] = shape['target_outline']
                    shape['target_outline'] = get_random_color()
                shape['color_step'] = 0

            # --- Update Position ---
            if shape['move_steps_remaining'] > 0:
                current_coords = canvas_obj.coords(shape_id)
                if shape['type'] == 'polygon':
                    bounds = get_polygon_bounds(current_coords)
                else:
                    bounds = current_coords

                if not bounds or len(bounds) < 4:
                    shape['move_steps_remaining'] = 0
                    continue

                next_x1 = bounds[0] + shape['dx']
                next_y1 = bounds[1] + shape['dy']
                next_x2 = bounds[2] + shape['dx']
                next_y2 = bounds[3] + shape['dy']

                if (next_x1 < INNER_X_MIN or next_x2 > INNER_X_MAX or
                    next_y1 < INNER_Y_MIN or next_y2 > INNER_Y_MAX):
                    shape['move_steps_remaining'] = 0
                    assign_new_target_position(shape)
                else:
                    canvas_obj.move(shape_id, shape['dx'], shape['dy'])
                    shape['move_steps_remaining'] -= 1
            else: # Reached target position or stopped, pick a new target
                assign_new_target_position(shape)

        except tk.TclError:
            if i not in shapes_to_remove_indices:
                 shapes_to_remove_indices.append(i)
        except Exception as e:
             print(f"Unexpected error updating item {shape_id}: {e}. Marking for removal.")
             if i not in shapes_to_remove_indices:
                 shapes_to_remove_indices.append(i)

    # Remove shapes that caused errors
    if shapes_to_remove_indices:
        for index in sorted(shapes_to_remove_indices, reverse=True):
            del animated_shapes[index]

    # Schedule the next update
    try:
        root.after(UPDATE_INTERVAL_MS, update_animation, canvas_obj, root)
    except tk.TclError:
        print("Window closed, stopping animation loop.")


# --- Main Application Setup ---
def main():
    global canvas, animated_shapes, placed_shapes_data

    root = tk.Tk()
    root.title("Random Art Within Borders (Simulated 3D)") # Updated title
    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    canvas.pack()

    placed_shapes_data = [] # Reset list for this run

    # --- Draw Large Faint Background Shapes (Bottom Layer) ---
    print("Drawing faint background shapes...")
    num_faint_shapes = random.randint(4, 8)
    for _ in range(num_faint_shapes):
        size_x = random.randint(int(CANVAS_WIDTH * 0.4), int(CANVAS_WIDTH * 1.2))
        size_y = random.randint(int(CANVAS_HEIGHT * 0.4), int(CANVAS_HEIGHT * 1.2))
        x1 = random.randint(-size_x // 3, CANVAS_WIDTH - (2 * size_x // 3))
        y1 = random.randint(-size_y // 3, CANVAS_HEIGHT - (2 * size_y // 3))
        x2 = x1 + size_x
        y2 = y1 + size_y
        faint_color = get_random_faint_color()
        if random.choice([True, False]):
             canvas.create_rectangle(x1, y1, x2, y2, fill=faint_color, outline="")
        else:
             canvas.create_oval(x1, y1, x2, y2, fill=faint_color, outline="")
    print(f"Faint background shapes drawn ({num_faint_shapes}).")

    # --- Draw Main Contrasting Background (Split) ---
    bg_color1 = get_random_color()
    bg_color2 = get_random_color()
    while bg_color1 == bg_color2: bg_color2 = get_random_color()
    split_direction = random.randint(0, 1)
    if split_direction == 0:
        canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT / 2, fill=bg_color1, outline="")
        canvas.create_rectangle(0, CANVAS_HEIGHT / 2, CANVAS_WIDTH, CANVAS_HEIGHT, fill=bg_color2, outline="")
    else:
        canvas.create_rectangle(0, 0, CANVAS_WIDTH / 2, CANVAS_HEIGHT, fill=bg_color1, outline="")
        canvas.create_rectangle(CANVAS_WIDTH / 2, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill=bg_color2, outline="")

    # --- Draw the Border ---
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, outline=BORDER_COLOR, width=BORDER_THICKNESS * 2)

    # --- Draw Randomized Rectangles (Non-Overlapping, Within Border) ---
    print(f"Attempting to place {NUM_RANDOM_RECTANGLES} rectangles...")
    rectangles_placed = 0
    for _ in range(NUM_RANDOM_RECTANGLES):
        placed = False
        for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
            max_possible_size_x = min(MAX_SHAPE_SIZE, INNER_WIDTH)
            max_possible_size_y = min(MAX_SHAPE_SIZE, INNER_HEIGHT)
            if max_possible_size_x < MIN_SHAPE_SIZE or max_possible_size_y < MIN_SHAPE_SIZE: break
            size_x = random.randint(MIN_SHAPE_SIZE, max_possible_size_x)
            size_y = random.randint(MIN_SHAPE_SIZE, max_possible_size_y)
            x1 = random.randint(INNER_X_MIN, INNER_X_MAX - size_x)
            y1 = random.randint(INNER_Y_MIN, INNER_Y_MAX - size_y)
            x2 = x1 + size_x
            y2 = y1 + size_y
            current_bounds = (x1, y1, x2, y2)
            overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)

            if not overlaps:
                rect_fill_color = get_random_color()
                rect_outline_color = get_random_color()
                rect_outline_width = random.randint(MIN_RECT_OUTLINE, MAX_RECT_OUTLINE)
                shape_id = canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=rect_fill_color,
                    outline=rect_outline_color,
                    width=rect_outline_width
                )
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                shape_data = {
                    'id': shape_id, 'type': 'rectangle',
                    'bounds': current_bounds, 'center': (center_x, center_y),
                    'fill': rect_fill_color, 'outline': rect_outline_color
                 }
                placed_shapes_data.append(shape_data)
                placed = True
                rectangles_placed += 1
                break
    print(f"Successfully placed {rectangles_placed} rectangles.")

    # --- Draw Randomized Circles (Non-Overlapping, Within Border) ---
    print(f"Attempting to place {NUM_RANDOM_CIRCLES} circles...")
    circles_placed = 0
    for _ in range(NUM_RANDOM_CIRCLES):
        placed = False
        for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
            max_possible_size_x = min(MAX_SHAPE_SIZE, INNER_WIDTH)
            max_possible_size_y = min(MAX_SHAPE_SIZE, INNER_HEIGHT)
            if max_possible_size_x < MIN_SHAPE_SIZE or max_possible_size_y < MIN_SHAPE_SIZE: break
            size_x = random.randint(MIN_SHAPE_SIZE, max_possible_size_x)
            size_y = random.randint(MIN_SHAPE_SIZE, max_possible_size_y)
            x1 = random.randint(INNER_X_MIN, INNER_X_MAX - size_x)
            y1 = random.randint(INNER_Y_MIN, INNER_Y_MAX - size_y)
            x2 = x1 + size_x
            y2 = y1 + size_y
            current_bounds = (x1, y1, x2, y2)
            overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)

            if not overlaps:
                circle_fill_color = get_random_color()
                circle_outline_color = get_random_color()
                circle_outline_width = random.randint(MIN_CIRCLE_OUTLINE, MAX_CIRCLE_OUTLINE)
                shape_id = canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=circle_fill_color,
                    outline=circle_outline_color,
                    width=circle_outline_width
                )
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                shape_data = {
                    'id': shape_id, 'type': 'oval',
                    'bounds': current_bounds, 'center': (center_x, center_y),
                    'fill': circle_fill_color, 'outline': circle_outline_color
                }
                placed_shapes_data.append(shape_data)
                placed = True
                circles_placed += 1
                break
    print(f"Successfully placed {circles_placed} circles.")

    # --- Draw Randomized Polygons (Non-Overlapping, Within Border) ---
    print(f"Attempting to place {NUM_RANDOM_POLYGONS} polygons...")
    polygons_placed = 0
    for _ in range(NUM_RANDOM_POLYGONS):
        placed = False
        for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
            max_radius = MAX_SHAPE_SIZE / 2
            center_buffer = max_radius + 5
            min_center_x = INNER_X_MIN + center_buffer
            max_center_x = INNER_X_MAX - center_buffer
            min_center_y = INNER_Y_MIN + center_buffer
            max_center_y = INNER_Y_MAX - center_buffer
            if min_center_x > max_center_x or min_center_y > max_center_y: break
            center_x = random.randint(int(min_center_x), int(max_center_x))
            center_y = random.randint(int(min_center_y), int(max_center_y))
            max_possible_avg_radius = min(center_x - INNER_X_MIN, INNER_X_MAX - center_x,
                                          center_y - INNER_Y_MIN, INNER_Y_MAX - center_y,
                                          MAX_SHAPE_SIZE / 2)
            if max_possible_avg_radius < MIN_SHAPE_SIZE / 2: continue
            avg_radius = random.uniform(MIN_SHAPE_SIZE / 2, max_possible_avg_radius)
            irregularity = random.uniform(0.1, 0.5)
            spikeyness = random.uniform(0.1, 0.6)
            num_vertices = random.randint(MIN_POLYGON_VERTICES, MAX_POLYGON_VERTICES)
            points = generate_random_polygon_points(center_x, center_y, avg_radius, irregularity, spikeyness, num_vertices)
            current_bounds = get_polygon_bounds(points)
            if current_bounds[0] < INNER_X_MIN or current_bounds[1] < INNER_Y_MIN or \
               current_bounds[2] > INNER_X_MAX or current_bounds[3] > INNER_Y_MAX: continue
            overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)

            if not overlaps:
                poly_fill_color = get_random_color()
                poly_outline_color = get_random_color()
                poly_outline_width = random.randint(MIN_POLYGON_OUTLINE, MAX_POLYGON_OUTLINE)
                shape_id = canvas.create_polygon(
                    points,
                    fill=poly_fill_color,
                    outline=poly_outline_color,
                    width=poly_outline_width
                )
                bound_center_x = (current_bounds[0] + current_bounds[2]) / 2
                bound_center_y = (current_bounds[1] + current_bounds[3]) / 2
                shape_data = {
                    'id': shape_id, 'type': 'polygon',
                    'bounds': current_bounds, 'center': (bound_center_x, bound_center_y),
                    'fill': poly_fill_color, 'outline': poly_outline_color
                }
                placed_shapes_data.append(shape_data)
                placed = True
                polygons_placed += 1
                break
    print(f"Successfully placed {polygons_placed} polygons.")

    # --- Draw Randomized Isometric Cubes (Non-Overlapping, Within Border) ---
    print(f"Attempting to place {NUM_RANDOM_CUBES} isometric cubes...")
    cubes_placed = 0
    for _ in range(NUM_RANDOM_CUBES):
        placed = False
        for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
            # Choose size and color
            cube_size = random.randint(MIN_CUBE_SIZE, MAX_CUBE_SIZE)
            cube_color = get_random_color()

            # Estimate bounds needed for center placement (conservative)
            est_width = cube_size * 0.866 * 2 # Width based on horizontal offsets
            est_height = cube_size * 2        # Height from top point to bottom point

            min_cx = INNER_X_MIN + est_width / 2
            max_cx = INNER_X_MAX - est_width / 2
            min_cy = INNER_Y_MIN + cube_size # Need space for top point
            max_cy = INNER_Y_MAX - cube_size # Need space for bottom point

            if min_cx >= max_cx or min_cy >= max_cy:
                break # Not enough space

            center_x = random.uniform(min_cx, max_cx)
            center_y = random.uniform(min_cy, max_cy)

            # Calculate potential bounds based on the chosen center and size
            offset_x = cube_size * 0.866
            potential_min_x = center_x - offset_x
            potential_max_x = center_x + offset_x
            potential_min_y = center_y - cube_size # Top point
            potential_max_y = center_y + cube_size # Bottom point
            potential_bounds = (potential_min_x, potential_min_y, potential_max_x, potential_max_y)

            overlaps = any(check_overlap(potential_bounds, s['bounds']) for s in placed_shapes_data)

            if not overlaps:
                actual_bounds = draw_isometric_cube(canvas, center_x, center_y, cube_size, cube_color)
                shape_data = {
                    'id': None, # No single ID
                    'type': 'isometric_cube',
                    'bounds': actual_bounds,
                    'center': (center_x, center_y),
                    'fill': cube_color,
                    'outline': 'black'
                }
                placed_shapes_data.append(shape_data)
                placed = True
                cubes_placed += 1
                break
    print(f"Successfully placed {cubes_placed} isometric cubes.")

    # --- Draw Randomized Isometric Pyramids (Non-Overlapping, Within Border) --- # <<< NEW SECTION
    print(f"Attempting to place {NUM_RANDOM_PYRAMIDS} isometric pyramids...")
    pyramids_placed = 0
    for _ in range(NUM_RANDOM_PYRAMIDS):
        placed = False
        for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
            # Choose size and color
            pyramid_base = random.randint(MIN_PYRAMID_BASE, MAX_PYRAMID_BASE)
            pyramid_height_factor = random.uniform(MIN_PYRAMID_HEIGHT_FACTOR, MAX_PYRAMID_HEIGHT_FACTOR)
            pyramid_color = get_random_color()
            pyramid_height = pyramid_base * pyramid_height_factor

            # Estimate bounds needed for center placement (conservative)
            est_width = pyramid_base * 0.866 # Base diagonal projection
            est_height = pyramid_height + (pyramid_base * 0.5 / 2) # Height + bit of base projection

            min_cx = INNER_X_MIN + est_width / 2
            max_cx = INNER_X_MAX - est_width / 2
            # Need space for apex above and base below center
            min_cy = INNER_Y_MIN + pyramid_height * 0.8 # Estimate apex position relative to center
            max_cy = INNER_Y_MAX - (pyramid_base * 0.5 / 2) * 1.2 # Estimate base bottom relative to center

            if min_cx >= max_cx or min_cy >= max_cy:
                break # Not enough space

            center_x = random.uniform(min_cx, max_cx)
            center_y = random.uniform(min_cy, max_cy)

            # Calculate potential bounds (rough estimate based on extremes)
            potential_min_x = center_x - est_width / 2
            potential_max_x = center_x + est_width / 2
            potential_min_y = center_y - pyramid_height * 0.8 # Approx apex y
            potential_max_y = center_y + (pyramid_base * 0.5 / 2) * 1.2 # Approx base bottom y
            potential_bounds = (potential_min_x, potential_min_y, potential_max_x, potential_max_y)

            overlaps = any(check_overlap(potential_bounds, s['bounds']) for s in placed_shapes_data)

            if not overlaps:
                actual_bounds = draw_isometric_pyramid(canvas, center_x, center_y, pyramid_base, pyramid_height_factor, pyramid_color)
                shape_data = {
                    'id': None, 'type': 'isometric_pyramid',
                    'bounds': actual_bounds, 'center': (center_x, center_y),
                    'fill': pyramid_color, 'outline': 'black'
                }
                placed_shapes_data.append(shape_data)
                placed = True
                pyramids_placed += 1
                break
    print(f"Successfully placed {pyramids_placed} isometric pyramids.")

    # --- Draw Randomized Isometric Prisms (Non-Overlapping, Within Border) --- # <<< NEW SECTION
    print(f"Attempting to place {NUM_RANDOM_PRISMS} isometric prisms...")
    prisms_placed = 0
    for _ in range(NUM_RANDOM_PRISMS):
        placed = False
        for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
            # Choose dimensions and color
            prism_w = random.randint(MIN_PRISM_DIM, MAX_PRISM_DIM)
            prism_d = random.randint(MIN_PRISM_DIM, MAX_PRISM_DIM)
            prism_h = random.randint(MIN_PRISM_DIM, MAX_PRISM_DIM)
            prism_color = get_random_color()

            # Estimate bounds needed for center placement (conservative)
            # Combine width and depth projections for horizontal estimate
            est_width = (prism_w + prism_d) * 0.866 / 2 * 2 # Full projected width
            # Combine height and depth/width projections for vertical estimate
            est_height = prism_h + (prism_w + prism_d) * 0.5 / 2 * 2 # Full projected height

            min_cx = INNER_X_MIN + est_width / 2
            max_cx = INNER_X_MAX - est_width / 2
            min_cy = INNER_Y_MIN + est_height / 2
            max_cy = INNER_Y_MAX - est_height / 2

            if min_cx >= max_cx or min_cy >= max_cy:
                break # Not enough space

            center_x = random.uniform(min_cx, max_cx)
            center_y = random.uniform(min_cy, max_cy)

            # Calculate potential bounds (rough estimate)
            potential_min_x = center_x - est_width / 2
            potential_max_x = center_x + est_width / 2
            potential_min_y = center_y - est_height / 2
            potential_max_y = center_y + est_height / 2
            potential_bounds = (potential_min_x, potential_min_y, potential_max_x, potential_max_y)

            overlaps = any(check_overlap(potential_bounds, s['bounds']) for s in placed_shapes_data)

            if not overlaps:
                actual_bounds = draw_isometric_prism(canvas, center_x, center_y, prism_w, prism_d, prism_h, prism_color)
                shape_data = {
                    'id': None, 'type': 'isometric_prism',
                    'bounds': actual_bounds, 'center': (center_x, center_y),
                    'fill': prism_color, 'outline': 'black'
                }
                placed_shapes_data.append(shape_data)
                placed = True
                prisms_placed += 1
                break
    print(f"Successfully placed {prisms_placed} isometric prisms.")


    # --- Draw Random Dots (Within Border) ---
    for _ in range(NUM_RANDOM_DOTS):
        dot_size = random.randint(MIN_DOT_SIZE, MAX_DOT_SIZE)
        x = random.randint(INNER_X_MIN, INNER_X_MAX - dot_size)
        y = random.randint(INNER_Y_MIN, INNER_Y_MAX - dot_size)
        canvas.create_oval(x, y, x + dot_size, y + dot_size, fill="black", outline="")

    # --- Draw Random Lines (Within Border) ---
    for _ in range(NUM_RANDOM_LINES):
        lx1 = random.randint(INNER_X_MIN, INNER_X_MAX)
        ly1 = random.randint(INNER_Y_MIN, INNER_Y_MAX)
        lx2 = random.randint(INNER_X_MIN, INNER_X_MAX)
        ly2 = random.randint(INNER_Y_MIN, INNER_Y_MAX)
        thickness = random.randint(MIN_LINE_THICKNESS, MAX_LINE_THICKNESS)
        line_color = get_random_color()
        canvas.create_line(lx1, ly1, lx2, ly2, width=thickness, fill=line_color)

    # --- Select Shapes for Animation ---
    # Filter out shapes without an ID (like the composite cubes/pyramids/prisms)
    candidate_shapes_data = [s for s in placed_shapes_data if s.get('id') is not None]
    animated_shapes = [] # Reset list for this run
    selected_animated_ids = set()

    if candidate_shapes_data:
        num_to_animate = min(NUM_ANIMATED_SHAPES, len(candidate_shapes_data))
        print(f"\nSelecting {num_to_animate} shapes for animation...")
        selected_candidates = random.sample(candidate_shapes_data, num_to_animate)

        for candidate in selected_candidates:
            shape_info = {
                'id': candidate['id'],
                'type': candidate['type'],
                'current_fill': candidate['fill'],
                'target_fill': get_random_color(),
                'current_outline': candidate['outline'],
                'target_outline': get_random_color(),
                'color_step': 0,
                'move_steps_remaining': 0,
                'dx': 0.0,
                'dy': 0.0
            }
            assign_new_target_position(shape_info)
            animated_shapes.append(shape_info)
            selected_animated_ids.add(candidate['id'])
            print(f"  Animating shape ID: {candidate['id']} ({candidate['type']})")
    else:
        print("\nNo suitable shapes were placed to animate.")

    # --- Draw Connecting Lines Between Static Shapes ---
    # Filter out shapes without an ID and those selected for animation
    static_shapes_to_connect = [s for s in placed_shapes_data if s.get('id') is not None and s['id'] not in selected_animated_ids]

    if len(static_shapes_to_connect) >= 2:
        print(f"\nDrawing {NUM_CONNECTIONS} connections between static shapes...")
        connections_drawn = 0
        attempts = 0
        max_connection_attempts = NUM_CONNECTIONS * 5

        while connections_drawn < NUM_CONNECTIONS and attempts < max_connection_attempts:
            attempts += 1
            try:
                shape1, shape2 = random.sample(static_shapes_to_connect, 2)
            except ValueError: # Should not happen if len >= 2, but safety first
                break

            center1 = shape1['center']
            center2 = shape2['center']

            line_id = canvas.create_line(
                center1[0], center1[1], center2[0], center2[1],
                width=CONNECTION_LINE_WIDTH,
                fill=CONNECTION_LINE_COLOR
            )
            canvas.tag_lower(line_id) # Attempt to draw lines behind shapes
            connections_drawn += 1
        print(f"  Drew {connections_drawn} connecting lines.")
    elif len(static_shapes_to_connect) < 2:
        print("\nNot enough static shapes placed to draw connections.")


    # --- Start the Animation Loop ---
    if animated_shapes:
        print("\nStarting animation loop...")
        root.after(100, update_animation, canvas, root)
    else:
         print("\nNo shapes selected for animation.")

    # --- Run the Tkinter loop ---
    print("Starting Tkinter main loop...")
    root.mainloop()
    print("Tkinter main loop exited.")

if __name__ == "__main__":
    main()
