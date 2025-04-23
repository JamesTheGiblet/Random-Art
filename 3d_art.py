import tkinter as tk
from tkinter import messagebox
import random
import math
import config
import shapes_3d
import colour_utils # <<< Make sure filename matches (colour_utils.py)
import save_utils
import ui_controls  # <<< Import the UI controls module

# --- Global Variables ---
# (Keep animated_shapes, canvas, placed_shapes_data)
animated_shapes = []
canvas = None
placed_shapes_data = []
# Add a variable to hold the control panel instance
controls = None
# Add a variable to store the after ID for animation loop cancellation
animation_after_id = None

# --- Helper Functions ---
# (generate_random_polygon_points, check_overlap, get_polygon_bounds remain)
def generate_random_polygon_points(center_x, center_y, avg_radius, irregularity, spikeyness, num_vertices):
    """Generates points for a random polygon, respecting inner bounds."""
    points = []
    angle_step = 2 * math.pi / num_vertices
    for i in range(num_vertices):
        angle = i * angle_step
        radius = random.gauss(avg_radius, avg_radius * irregularity)
        radius = max(config.MIN_SHAPE_SIZE / 2, radius)
        angle += random.gauss(0, angle_step * spikeyness * 0.5)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        x = max(config.INNER_X_MIN, min(config.INNER_X_MAX, x))
        y = max(config.INNER_Y_MIN, min(config.INNER_Y_MAX, y))
        points.extend([x, y])
    return points

def check_overlap(box1, box2):
    """Checks if two bounding boxes (x1, y1, x2, y2) overlap."""
    if not box1 or len(box1) != 4 or not box2 or len(box2) != 4:
        return False
    if box1[0] > box1[2] or box1[1] > box1[3] or box2[0] > box2[2] or box2[1] > box2[3]:
        return False
    if box1[2] < box2[0] or box1[0] > box2[2] or box1[3] < box2[1] or box1[1] > box2[3]:
        return False
    return True

def get_polygon_bounds(points):
    """Calculates the bounding box (x1, y1, x2, y2) for a list of polygon points."""
    if not points or len(points) < 2: return (0, 0, 0, 0)
    x_coords = points[0::2]
    y_coords = points[1::2]
    if not x_coords or not y_coords: return (0,0,0,0)
    return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))


# --- Animation Logic ---
# (assign_new_target_position remains, but needs access to current animation speed)
def assign_new_target_position(shape_info, current_config):
    """Assigns a new random target position within INNER bounds for an animated shape."""
    global canvas
    if not canvas: return

    # ... (rest of the coordinate/size calculation is the same) ...
    if shape_info['type'] in ['rectangle', 'oval']:
        current_coords = canvas.coords(shape_info['id'])
        if not current_coords or len(current_coords) < 4:
             shape_info['move_steps_remaining'] = 0
             return
        curr_x1, curr_y1, curr_x2, curr_y2 = current_coords
        curr_w = curr_x2 - curr_x1
        curr_h = curr_y2 - curr_y1
    elif shape_info['type'] == 'polygon':
        try:
            current_coords = canvas.coords(shape_info['id'])
            bounds = get_polygon_bounds(current_coords)
            if not bounds or len(bounds) < 4:
                shape_info['move_steps_remaining'] = 0
                return
            curr_x1, curr_y1, curr_x2, curr_y2 = bounds
            curr_w = curr_x2 - curr_x1
            curr_h = curr_y2 - curr_y1
        except tk.TclError:
            shape_info['move_steps_remaining'] = 0
            return
    else:
        shape_info['move_steps_remaining'] = 0
        return

    min_x = config.INNER_X_MIN
    min_y = config.INNER_Y_MIN
    max_x = config.INNER_X_MAX - curr_w
    max_y = config.INNER_Y_MAX - curr_h

    if max_x <= min_x: max_x = min_x + 1
    if max_y <= min_y: max_y = min_y + 1

    target_x1 = random.randint(min_x, int(max_x))
    target_y1 = random.randint(min_y, int(max_y))

    current_pos_x = current_coords[0] if shape_info['type'] != 'polygon' else curr_x1
    current_pos_y = current_coords[1] if shape_info['type'] != 'polygon' else curr_y1

    delta_x = target_x1 - current_pos_x
    delta_y = target_y1 - current_pos_y
    distance = math.sqrt(delta_x**2 + delta_y**2)

    # <<< Use animation speed from current_config (passed from UI)
    anim_speed = current_config.get("MOVEMENT_SPEED", config.MOVEMENT_SPEED)
    if anim_speed <= 0: anim_speed = 0.1 # Prevent division by zero or no movement

    if distance < anim_speed:
        shape_info['move_steps_remaining'] = 0
        shape_info['dx'] = 0
        shape_info['dy'] = 0
    else:
        steps_needed = max(1, int(distance / anim_speed))
        shape_info['move_steps_remaining'] = steps_needed
        shape_info['dx'] = delta_x / steps_needed
        shape_info['dy'] = delta_y / steps_needed
        shape_info['target_coords'] = [target_x1, target_y1]


# (update_animation needs access to current config for speed)
def update_animation(canvas_obj, root, current_config):
    """The main animation loop function."""
    global animated_shapes, animation_after_id
    shapes_to_remove_indices = []

    for i, shape in enumerate(animated_shapes):
        shape_id = shape['id']
        try:
            # --- Update Color ---
            if shape['color_step'] < config.COLOR_FADE_STEPS:
                shape['color_step'] += 1
                factor = shape['color_step'] / config.COLOR_FADE_STEPS
                new_fill = colour_utils.interpolate_color(shape['current_fill'], shape['target_fill'], factor)
                new_outline = shape['current_outline']
                if 'target_outline' in shape:
                     new_outline = colour_utils.interpolate_color(shape['current_outline'], shape['target_outline'], factor)

                config_opts = {'fill': new_fill}
                if 'target_outline' in shape:
                    config_opts['outline'] = new_outline
                canvas_obj.itemconfig(shape_id, **config_opts)
            else:
                shape['current_fill'] = shape['target_fill']
                shape['target_fill'] = colour_utils.get_random_color()
                if 'target_outline' in shape:
                    shape['current_outline'] = shape['target_outline']
                    shape['target_outline'] = colour_utils.get_random_color()
                shape['color_step'] = 0

            # --- Update Position ---
            if shape['move_steps_remaining'] > 0:
                # ... (boundary check logic remains the same) ...
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

                if (next_x1 < config.INNER_X_MIN or next_x2 > config.INNER_X_MAX or
                    next_y1 < config.INNER_Y_MIN or next_y2 > config.INNER_Y_MAX):
                    shape['move_steps_remaining'] = 0
                    assign_new_target_position(shape, current_config) # Pass config
                else:
                    canvas_obj.move(shape_id, shape['dx'], shape['dy'])
                    shape['move_steps_remaining'] -= 1
            else:
                assign_new_target_position(shape, current_config) # Pass config

        except tk.TclError:
            if i not in shapes_to_remove_indices:
                 shapes_to_remove_indices.append(i)
        except Exception as e:
             print(f"Unexpected error updating item {shape_id}: {e}. Marking for removal.")
             if i not in shapes_to_remove_indices:
                 shapes_to_remove_indices.append(i)

    if shapes_to_remove_indices:
        # Remove shapes safely
        current_ids = {s['id'] for s in animated_shapes}
        animated_shapes = [s for i, s in enumerate(animated_shapes) if i not in shapes_to_remove_indices]
        remaining_ids = {s['id'] for s in animated_shapes}
        print(f"Removed {len(current_ids - remaining_ids)} shapes due to errors.")


    # Schedule the next update
    try:
        # Store the 'after' ID so we can cancel it if needed
        animation_after_id = root.after(config.UPDATE_INTERVAL_MS, update_animation, canvas_obj, root, current_config)
    except tk.TclError:
        print("Window closed, stopping animation loop.")
    except Exception as e:
        print(f"Error scheduling next animation frame: {e}")
        animation_after_id = None


# --- Art Generation Function ---
def generate_art(current_config):
    """Clears the canvas and generates new art based on the provided config."""
    global canvas, placed_shapes_data, animated_shapes, animation_after_id

    if not canvas:
        print("Canvas not initialized.")
        return

    print("\n--- Regenerating Art ---")
    current_config = current_config or {} # Ensure it's a dict

    # --- Clear Canvas and Data ---
    canvas.delete("all") # Remove all items from canvas
    placed_shapes_data = []
    animated_shapes = []

    # --- Cancel Previous Animation Loop (if running) ---
    if animation_after_id:
        try:
            canvas.after_cancel(animation_after_id)
            print("Cancelled previous animation loop.")
        except tk.TclError:
            pass # May already be cancelled or window closed
        animation_after_id = None

    # --- Get Values from UI/Config ---
    # Use .get() with fallback to original config module values
    num_rectangles = current_config.get("NUM_RANDOM_RECTANGLES", config.NUM_RANDOM_RECTANGLES)
    num_circles = current_config.get("NUM_RANDOM_CIRCLES", config.NUM_RANDOM_CIRCLES)
    num_polygons = current_config.get("NUM_RANDOM_POLYGONS", config.NUM_RANDOM_POLYGONS)
    num_cubes = current_config.get("NUM_RANDOM_CUBES", config.NUM_RANDOM_CUBES)
    num_pyramids = current_config.get("NUM_RANDOM_PYRAMIDS", config.NUM_RANDOM_PYRAMIDS)
    num_prisms = current_config.get("NUM_RANDOM_PRISMS", config.NUM_RANDOM_PRISMS)
    num_dots = current_config.get("NUM_RANDOM_DOTS", config.NUM_RANDOM_DOTS)
    num_lines = current_config.get("NUM_RANDOM_LINES", config.NUM_RANDOM_LINES)
    num_connections = current_config.get("NUM_CONNECTIONS", config.NUM_CONNECTIONS)
    num_animated = current_config.get("NUM_ANIMATED_SHAPES", config.NUM_ANIMATED_SHAPES)
    # Note: Animation speed is used within the animation loop itself

    # --- Generation Logic (using values obtained above) ---
    print("Drawing faint background shapes...")
    num_faint_shapes = random.randint(config.NUM_FAINT_SHAPES_MIN, config.NUM_FAINT_SHAPES_MAX)
    for _ in range(num_faint_shapes):
        # (Faint shape drawing logic remains the same, uses config directly for style)
        size_x = random.randint(int(config.CANVAS_WIDTH * config.FAINT_SHAPE_MIN_SCALE), int(config.CANVAS_WIDTH * config.FAINT_SHAPE_MAX_SCALE))
        size_y = random.randint(int(config.CANVAS_HEIGHT * config.FAINT_SHAPE_MIN_SCALE), int(config.CANVAS_HEIGHT * config.FAINT_SHAPE_MAX_SCALE))
        x1 = random.randint(-size_x // 3, config.CANVAS_WIDTH - (2 * size_x // 3))
        y1 = random.randint(-size_y // 3, config.CANVAS_HEIGHT - (2 * size_y // 3))
        x2 = x1 + size_x
        y2 = y1 + size_y
        faint_color = colour_utils.get_random_faint_color()
        if random.choice([True, False]):
             canvas.create_rectangle(x1, y1, x2, y2, fill=faint_color, outline="")
        else:
             canvas.create_oval(x1, y1, x2, y2, fill=faint_color, outline="")
    print(f"Faint background shapes drawn ({num_faint_shapes}).")

    # --- Draw Main Contrasting Background (Split) ---
    bg_color1 = colour_utils.get_random_color()
    bg_color2 = colour_utils.get_random_color()
    while bg_color1 == bg_color2: bg_color2 = colour_utils.get_random_color()
    split_direction = random.randint(0, 1)
    if split_direction == 0:
        canvas.create_rectangle(0, 0, config.CANVAS_WIDTH, config.CANVAS_HEIGHT / 2, fill=bg_color1, outline="")
        canvas.create_rectangle(0, config.CANVAS_HEIGHT / 2, config.CANVAS_WIDTH, config.CANVAS_HEIGHT, fill=bg_color2, outline="")
    else:
        canvas.create_rectangle(0, 0, config.CANVAS_WIDTH / 2, config.CANVAS_HEIGHT, fill=bg_color1, outline="")
        canvas.create_rectangle(config.CANVAS_WIDTH / 2, 0, config.CANVAS_WIDTH, config.CANVAS_HEIGHT, fill=bg_color2, outline="")

    # --- Draw the Border ---
    canvas.create_rectangle(0, 0, config.CANVAS_WIDTH, config.CANVAS_HEIGHT,
                            outline=config.BORDER_COLOR, width=config.BORDER_THICKNESS * 2)

    # --- Draw Randomized Rectangles ---
    print(f"Attempting to place {num_rectangles} rectangles...")
    rectangles_placed = 0
    for _ in range(num_rectangles): # Use UI value
        placed = False
        for attempt in range(config.SHAPE_PLACEMENT_ATTEMPTS):
            max_possible_size_x = min(config.MAX_SHAPE_SIZE, config.INNER_WIDTH)
            max_possible_size_y = min(config.MAX_SHAPE_SIZE, config.INNER_HEIGHT)
            if max_possible_size_x < config.MIN_SHAPE_SIZE or max_possible_size_y < config.MIN_SHAPE_SIZE: break
            size_x = random.randint(config.MIN_SHAPE_SIZE, max_possible_size_x)
            size_y = random.randint(config.MIN_SHAPE_SIZE, max_possible_size_y)
            x1 = random.randint(config.INNER_X_MIN, config.INNER_X_MAX - size_x)
            y1 = random.randint(config.INNER_Y_MIN, config.INNER_Y_MAX - size_y)
            x2 = x1 + size_x
            y2 = y1 + size_y
            current_bounds = (x1, y1, x2, y2)
            overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)
            if not overlaps:
                rect_fill_color = colour_utils.get_random_color()
                rect_outline_color = colour_utils.get_random_color()
                rect_outline_width = random.randint(config.MIN_RECT_OUTLINE, config.MAX_RECT_OUTLINE)
                shape_id = canvas.create_rectangle(x1, y1, x2, y2, fill=rect_fill_color, outline=rect_outline_color, width=rect_outline_width)
                center_x = (x1 + x2) / 2; center_y = (y1 + y2) / 2
                shape_data = {'id': shape_id, 'type': 'rectangle', 'bounds': current_bounds, 'center': (center_x, center_y), 'fill': rect_fill_color, 'outline': rect_outline_color}
                placed_shapes_data.append(shape_data)
                placed = True; rectangles_placed += 1; break
    print(f"Successfully placed {rectangles_placed} rectangles.")

    # --- Draw Randomized Circles ---
    print(f"Attempting to place {num_circles} circles...")
    circles_placed = 0
    for _ in range(num_circles): # Use UI value
        placed = False
        for attempt in range(config.SHAPE_PLACEMENT_ATTEMPTS):
            max_possible_size_x = min(config.MAX_SHAPE_SIZE, config.INNER_WIDTH)
            max_possible_size_y = min(config.MAX_SHAPE_SIZE, config.INNER_HEIGHT)
            if max_possible_size_x < config.MIN_SHAPE_SIZE or max_possible_size_y < config.MIN_SHAPE_SIZE: break
            size_x = random.randint(config.MIN_SHAPE_SIZE, max_possible_size_x)
            size_y = random.randint(config.MIN_SHAPE_SIZE, max_possible_size_y)
            x1 = random.randint(config.INNER_X_MIN, config.INNER_X_MAX - size_x)
            y1 = random.randint(config.INNER_Y_MIN, config.INNER_Y_MAX - size_y)
            x2 = x1 + size_x; y2 = y1 + size_y
            current_bounds = (x1, y1, x2, y2)
            overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)
            if not overlaps:
                circle_fill_color = colour_utils.get_random_color()
                circle_outline_color = colour_utils.get_random_color()
                circle_outline_width = random.randint(config.MIN_CIRCLE_OUTLINE, config.MAX_CIRCLE_OUTLINE)
                shape_id = canvas.create_oval(x1, y1, x2, y2, fill=circle_fill_color, outline=circle_outline_color, width=circle_outline_width)
                center_x = (x1 + x2) / 2; center_y = (y1 + y2) / 2
                shape_data = {'id': shape_id, 'type': 'oval', 'bounds': current_bounds, 'center': (center_x, center_y), 'fill': circle_fill_color, 'outline': circle_outline_color}
                placed_shapes_data.append(shape_data)
                placed = True; circles_placed += 1; break
    print(f"Successfully placed {circles_placed} circles.")

    # --- Draw Randomized Polygons ---
    print(f"Attempting to place {num_polygons} polygons...")
    polygons_placed = 0
    for _ in range(num_polygons): # Use UI value
        placed = False
        for attempt in range(config.SHAPE_PLACEMENT_ATTEMPTS):
            max_radius = config.MAX_SHAPE_SIZE / 2; center_buffer = max_radius + 5
            min_center_x = config.INNER_X_MIN + center_buffer; max_center_x = config.INNER_X_MAX - center_buffer
            min_center_y = config.INNER_Y_MIN + center_buffer; max_center_y = config.INNER_Y_MAX - center_buffer
            if min_center_x > max_center_x or min_center_y > max_center_y: break
            center_x = random.randint(int(min_center_x), int(max_center_x))
            center_y = random.randint(int(min_center_y), int(max_center_y))
            max_possible_avg_radius = min(center_x - config.INNER_X_MIN, config.INNER_X_MAX - center_x, center_y - config.INNER_Y_MIN, config.INNER_Y_MAX - center_y, config.MAX_SHAPE_SIZE / 2)
            if max_possible_avg_radius < config.MIN_SHAPE_SIZE / 2: continue
            avg_radius = random.uniform(config.MIN_SHAPE_SIZE / 2, max_possible_avg_radius)
            irregularity = random.uniform(0.1, 0.5); spikeyness = random.uniform(0.1, 0.6)
            num_vertices = random.randint(config.MIN_POLYGON_VERTICES, config.MAX_POLYGON_VERTICES)
            points = generate_random_polygon_points(center_x, center_y, avg_radius, irregularity, spikeyness, num_vertices)
            current_bounds = get_polygon_bounds(points)
            if current_bounds[0] < config.INNER_X_MIN or current_bounds[1] < config.INNER_Y_MIN or current_bounds[2] > config.INNER_X_MAX or current_bounds[3] > config.INNER_Y_MAX: continue
            overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)
            if not overlaps:
                poly_fill_color = colour_utils.get_random_color()
                poly_outline_color = colour_utils.get_random_color()
                poly_outline_width = random.randint(config.MIN_POLYGON_OUTLINE, config.MAX_POLYGON_OUTLINE)
                shape_id = canvas.create_polygon(points, fill=poly_fill_color, outline=poly_outline_color, width=poly_outline_width)
                bound_center_x = (current_bounds[0] + current_bounds[2]) / 2; bound_center_y = (current_bounds[1] + current_bounds[3]) / 2
                shape_data = {'id': shape_id, 'type': 'polygon', 'bounds': current_bounds, 'center': (bound_center_x, bound_center_y), 'fill': poly_fill_color, 'outline': poly_outline_color}
                placed_shapes_data.append(shape_data)
                placed = True; polygons_placed += 1; break
    print(f"Successfully placed {polygons_placed} polygons.")

    # --- Draw Randomized Isometric Cubes ---
    print(f"Attempting to place {num_cubes} isometric cubes...")
    cubes_placed = 0
    for _ in range(num_cubes): # Use UI value
        placed = False
        for attempt in range(config.SHAPE_PLACEMENT_ATTEMPTS):
            cube_size = random.randint(config.MIN_CUBE_SIZE, config.MAX_CUBE_SIZE)
            cube_color = colour_utils.get_random_color()
            est_width = cube_size * 0.866 * 2; est_height = cube_size * 2
            min_cx = config.INNER_X_MIN + est_width / 2; max_cx = config.INNER_X_MAX - est_width / 2
            min_cy = config.INNER_Y_MIN + cube_size; max_cy = config.INNER_Y_MAX - cube_size
            if min_cx >= max_cx or min_cy >= max_cy: break
            center_x = random.uniform(min_cx, max_cx); center_y = random.uniform(min_cy, max_cy)
            offset_x = cube_size * 0.866
            potential_bounds = (center_x - offset_x, center_y - cube_size, center_x + offset_x, center_y + cube_size)
            overlaps = any(check_overlap(potential_bounds, s['bounds']) for s in placed_shapes_data)
            if not overlaps:
                actual_bounds = shapes_3d.draw_isometric_cube(canvas, center_x, center_y, cube_size, cube_color)
                shape_data = {'id': None, 'type': 'isometric_cube', 'bounds': actual_bounds, 'center': (center_x, center_y), 'fill': cube_color, 'outline': 'black'}
                placed_shapes_data.append(shape_data)
                placed = True; cubes_placed += 1; break
    print(f"Successfully placed {cubes_placed} isometric cubes.")

    # --- Draw Randomized Isometric Pyramids ---
    print(f"Attempting to place {num_pyramids} isometric pyramids...")
    pyramids_placed = 0
    for _ in range(num_pyramids): # Use UI value
        placed = False
        for attempt in range(config.SHAPE_PLACEMENT_ATTEMPTS):
            pyramid_base = random.randint(config.MIN_PYRAMID_BASE, config.MAX_PYRAMID_BASE)
            pyramid_height_factor = random.uniform(config.MIN_PYRAMID_HEIGHT_FACTOR, config.MAX_PYRAMID_HEIGHT_FACTOR)
            pyramid_color = colour_utils.get_random_color()
            pyramid_height = pyramid_base * pyramid_height_factor
            est_width = pyramid_base * 0.866; est_height = pyramid_height + (pyramid_base * 0.5 / 2)
            min_cx = config.INNER_X_MIN + est_width / 2; max_cx = config.INNER_X_MAX - est_width / 2
            min_cy = config.INNER_Y_MIN + pyramid_height * 0.8; max_cy = config.INNER_Y_MAX - (pyramid_base * 0.5 / 2) * 1.2
            if min_cx >= max_cx or min_cy >= max_cy: break
            center_x = random.uniform(min_cx, max_cx); center_y = random.uniform(min_cy, max_cy)
            potential_bounds = (center_x - est_width / 2, center_y - pyramid_height * 0.8, center_x + est_width / 2, center_y + (pyramid_base * 0.5 / 2) * 1.2)
            overlaps = any(check_overlap(potential_bounds, s['bounds']) for s in placed_shapes_data)
            if not overlaps:
                actual_bounds = shapes_3d.draw_isometric_pyramid(canvas, center_x, center_y, pyramid_base, pyramid_height_factor, pyramid_color)
                shape_data = {'id': None, 'type': 'isometric_pyramid', 'bounds': actual_bounds, 'center': (center_x, center_y), 'fill': pyramid_color, 'outline': 'black'}
                placed_shapes_data.append(shape_data)
                placed = True; pyramids_placed += 1; break
    print(f"Successfully placed {pyramids_placed} isometric pyramids.")

    # --- Draw Randomized Isometric Prisms ---
    print(f"Attempting to place {num_prisms} isometric prisms...")
    prisms_placed = 0
    for _ in range(num_prisms): # Use UI value
        placed = False
        for attempt in range(config.SHAPE_PLACEMENT_ATTEMPTS):
            prism_w = random.randint(config.MIN_PRISM_DIM, config.MAX_PRISM_DIM)
            prism_d = random.randint(config.MIN_PRISM_DIM, config.MAX_PRISM_DIM)
            prism_h = random.randint(config.MIN_PRISM_DIM, config.MAX_PRISM_DIM)
            prism_color = colour_utils.get_random_color()
            est_width = (prism_w + prism_d) * 0.866; est_height = prism_h + (prism_w + prism_d) * 0.5
            min_cx = config.INNER_X_MIN + est_width / 2; max_cx = config.INNER_X_MAX - est_width / 2
            min_cy = config.INNER_Y_MIN + est_height / 2; max_cy = config.INNER_Y_MAX - est_height / 2
            if min_cx >= max_cx or min_cy >= max_cy: break
            center_x = random.uniform(min_cx, max_cx); center_y = random.uniform(min_cy, max_cy)
            potential_bounds = (center_x - est_width / 2, center_y - est_height / 2, center_x + est_width / 2, center_y + est_height / 2)
            overlaps = any(check_overlap(potential_bounds, s['bounds']) for s in placed_shapes_data)
            if not overlaps:
                actual_bounds = shapes_3d.draw_isometric_prism(canvas, center_x, center_y, prism_w, prism_d, prism_h, prism_color)
                shape_data = {'id': None, 'type': 'isometric_prism', 'bounds': actual_bounds, 'center': (center_x, center_y), 'fill': prism_color, 'outline': 'black'}
                placed_shapes_data.append(shape_data)
                placed = True; prisms_placed += 1; break
    print(f"Successfully placed {prisms_placed} isometric prisms.")

    # --- Draw Random Dots ---
    for _ in range(num_dots): # Use UI value
        dot_size = random.randint(config.MIN_DOT_SIZE, config.MAX_DOT_SIZE)
        x = random.randint(config.INNER_X_MIN, config.INNER_X_MAX - dot_size)
        y = random.randint(config.INNER_Y_MIN, config.INNER_Y_MAX - dot_size)
        canvas.create_oval(x, y, x + dot_size, y + dot_size, fill="black", outline="")

    # --- Draw Random Lines ---
    for _ in range(num_lines): # Use UI value
        lx1 = random.randint(config.INNER_X_MIN, config.INNER_X_MAX); ly1 = random.randint(config.INNER_Y_MIN, config.INNER_Y_MAX)
        lx2 = random.randint(config.INNER_X_MIN, config.INNER_X_MAX); ly2 = random.randint(config.INNER_Y_MIN, config.INNER_Y_MAX)
        thickness = random.randint(config.MIN_LINE_THICKNESS, config.MAX_LINE_THICKNESS)
        line_color = colour_utils.get_random_color()
        canvas.create_line(lx1, ly1, lx2, ly2, width=thickness, fill=line_color)

    # --- Select Shapes for Animation ---
    candidate_shapes_data = [s for s in placed_shapes_data if s.get('id') is not None]
    selected_animated_ids = set()
    if candidate_shapes_data:
        num_to_animate = min(num_animated, len(candidate_shapes_data)) # Use UI value
        print(f"\nSelecting {num_to_animate} shapes for animation...")
        if num_to_animate > 0:
            selected_candidates = random.sample(candidate_shapes_data, num_to_animate)
            for candidate in selected_candidates:
                shape_info = {
                    'id': candidate['id'], 'type': candidate['type'],
                    'current_fill': candidate['fill'], 'target_fill': colour_utils.get_random_color(),
                    'current_outline': candidate['outline'], 'target_outline': colour_utils.get_random_color(),
                    'color_step': 0, 'move_steps_remaining': 0, 'dx': 0.0, 'dy': 0.0
                }
                assign_new_target_position(shape_info, current_config) # Pass config
                animated_shapes.append(shape_info)
                selected_animated_ids.add(candidate['id'])
                print(f"  Animating shape ID: {candidate['id']} ({candidate['type']})")
        else:
             print("  Zero shapes selected for animation based on UI setting.")
    else:
        print("\nNo suitable shapes were placed to animate.")

    # --- Draw Connecting Lines ---
    static_shapes_to_connect = [s for s in placed_shapes_data if s.get('id') is not None and s['id'] not in selected_animated_ids]
    if len(static_shapes_to_connect) >= 2:
        print(f"\nDrawing {num_connections} connections between static shapes...")
        connections_drawn = 0; attempts = 0
        max_connection_attempts = num_connections * 5 # Use UI value
        while connections_drawn < num_connections and attempts < max_connection_attempts: # Use UI value
            attempts += 1
            try: shape1, shape2 = random.sample(static_shapes_to_connect, 2)
            except ValueError: break
            center1 = shape1['center']; center2 = shape2['center']
            line_id = canvas.create_line(center1[0], center1[1], center2[0], center2[1], width=config.CONNECTION_LINE_WIDTH, fill=config.CONNECTION_LINE_COLOR)
            canvas.tag_lower(line_id)
            connections_drawn += 1
        print(f"  Drew {connections_drawn} connecting lines.")
    elif len(static_shapes_to_connect) < 2:
        print("\nNot enough static shapes placed to draw connections.")

    # --- Start the Animation Loop ---
    if animated_shapes:
        print("\nStarting animation loop...")
        # Pass the current_config dict to the animation loop
        update_animation(canvas, canvas.winfo_toplevel(), current_config) # Use winfo_toplevel to get root
    else:
         print("\nNo shapes selected for animation.")

    print("--- Art Generation Complete ---")


# --- Main Application Setup ---
def main():
    global canvas, controls # Make controls global

    root = tk.Tk()
    root.title("Generative Art Studio") # New title

    # --- Create Main Frames ---
    # Frame for controls on the left
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Frame for canvas and save buttons on the right/main area
    canvas_frame = tk.Frame(root)
    canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # --- Create Control Panel ---
    controls = ui_controls.ControlPanel(control_frame)
    controls.pack(fill=tk.Y)

    # --- Create Canvas ---
    canvas = tk.Canvas(canvas_frame, width=config.CANVAS_WIDTH, height=config.CANVAS_HEIGHT, bg="grey") # Temp bg
    canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # --- Create Button Frame (below canvas) ---
    button_frame = tk.Frame(canvas_frame)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    # --- Define Command Functions for Buttons ---
    def trigger_regenerate():
        if controls:
            current_config_values = controls.get_values()
            generate_art(current_config_values)
        else:
            messagebox.showerror("Error", "Control panel not available.")

    def trigger_save_png():
        if canvas:
            save_utils.export_to_png(canvas)
        else:
            messagebox.showerror("Error", "Canvas not available for export.")

    def trigger_save_svg():
        global placed_shapes_data # Need access to this global
        if canvas and placed_shapes_data is not None:
            save_utils.export_to_svg(canvas, placed_shapes_data)
        else:
            messagebox.showerror("Error", "Canvas or shape data not available for export.")

    # --- Add Buttons to the Frame ---
    regenerate_button = tk.Button(button_frame, text="Regenerate Art", command=trigger_regenerate, width=15)
    regenerate_button.pack(side=tk.LEFT, padx=10)

    png_button = tk.Button(button_frame, text="Save as PNG", command=trigger_save_png, width=15)
    png_button.pack(side=tk.LEFT, padx=10)

    svg_button = tk.Button(button_frame, text="Save as SVG", command=trigger_save_svg, width=15)
    svg_button.pack(side=tk.LEFT, padx=10)

    # --- Initial Art Generation ---
    # Generate art once on startup using default values from the controls
    initial_config = controls.get_values() if controls else {}
    generate_art(initial_config)

    # --- Run the Tkinter loop ---
    print("Starting Tkinter main loop...")
    root.mainloop()
    print("Tkinter main loop exited.")

if __name__ == "__main__":
    main()
    print("Program finished.")
    # Cleanup or additional logic can go here if needed
    # Note: The canvas and controls are cleaned up automatically when the window closes.