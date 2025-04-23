import textwrap

# Define the steps taken during development, now including code snippets
steps_data = [
    {
        "description": "0. **Defining the Algorithm:** Before coding, the overall approach was planned:",
        "code": """
# Algorithm Outline:
# 1. Setup: Initialize Tkinter window and canvas. Define constants for size, counts, colors, etc.
# 2. Background Layers:
#    - Draw large, faint shapes covering the whole canvas (underneath everything).
#    - Draw a main contrasting background (e.g., split colors).
# 3. Border: Draw a thick border defining the main content area. Calculate inner bounds.
# 4. Shape Placement (Iterative Non-Overlapping):
#    - Maintain a list (`placed_shapes_data`) of placed shapes and their bounding boxes/data.
#    - For each type of shape (rectangle, circle, polygon, cube, pyramid, prism):
#        - Loop for the desired number of shapes.
#        - Inside the loop, attempt placement multiple times (`SHAPE_PLACEMENT_ATTEMPTS`):
#            - Randomly determine shape parameters (size, position, color) respecting INNER bounds.
#            - Calculate the potential bounding box.
#            - Check if the potential box overlaps with any in `placed_shapes_data` using `check_overlap`.
#            - If no overlap:
#                - Draw the shape(s) on the canvas.
#                - Store its data (ID if applicable, type, bounds, center, colors) in `placed_shapes_data`.
#                - Mark as placed and break the attempt loop.
# 5. Decorative Elements: Add random dots and lines within the inner bounds (can overlap).
# 6. Animation Setup:
#    - Filter `placed_shapes_data` for shapes with Tkinter IDs (animatable).
#    - Randomly select a subset (`NUM_ANIMATED_SHAPES`) of these.
#    - Store animation state (target position, target color, steps remaining) for each selected shape.
# 7. Connecting Lines:
#    - Filter `placed_shapes_data` for static shapes (with IDs, not animated).
#    - If enough static shapes exist, randomly pick pairs and draw lines between their centers. Draw these lines underneath other elements (`tag_lower`).
# 8. Animation Loop (`update_animation`):
#    - Scheduled using `root.after`.
#    - For each animated shape:
#        - Interpolate color towards the target color.
#        - Move the shape slightly towards its target position.
#        - Check for boundary collisions within INNER bounds.
#        - If target color/position reached, assign new random targets.
#        - Handle potential errors (e.g., shape deleted).
# 9. Run: Start the Tkinter main loop (`root.mainloop()`).

# Key Logic:
# - Bounding Box Collision: The core of non-overlapping placement relies on accurately calculating and checking bounding boxes.
# - Data Management: Storing comprehensive shape data (`placed_shapes_data`) is crucial for collision detection, animation selection, and drawing connections.
# - Layering: Drawing elements in a specific order (backgrounds first, border, shapes, decorations, connections) creates visual depth. `tag_lower` helps adjust stacking.
# - Animation State: Managing state (current/target values, steps) allows for smooth transitions over time.
"""
    },
    {
        "description": "1. **Initial Setup:** Created a basic Tkinter window and canvas.",
        "code": """
import tkinter as tk

root = tk.Tk()
root.title("Initial Setup")
canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()
# root.mainloop() # Main loop added later
"""
    },
    {
        "description": "2. **Basic Shapes:** Added fundamental shapes like a fixed rectangle, circle, and line.",
        "code": """
# Draw a rectangle
canvas.create_rectangle(50, 50, 200, 150, fill="blue")
# Draw a circle
canvas.create_oval(250, 100, 350, 200, fill="red")
# Draw a line
canvas.create_line(400, 50, 550, 150, width=3, fill="green")
"""
    },
    {
        "description": "3. **Adding Dots:** Introduced small circles (dots) at random positions.",
        "code": """
import random

for _ in range(20): # Example number of dots
    x, y = random.randint(0, 600), random.randint(0, 400)
    # Initial fixed size dots
    canvas.create_oval(x, y, x + 3, y + 3, fill="black", outline="")
"""
    },
    {
        "description": "4. **Randomization Introduction:** Started randomizing properties - specifically the size of the dots.",
        "code": """
for _ in range(20):
    x, y = random.randint(0, 600), random.randint(0, 400)
    # Generate a random size for the dot
    dot_size = random.randint(1, 6)
    # Use the random size
    canvas.create_oval(x, y, x + dot_size, y + dot_size, fill="black", outline="")
"""
    },
    {
        "description": "5. **Random Lines:** Added multiple lines with random start/end points, random thicknesses, and random colors.",
        "code": """
def get_random_color():
    return f'#{random.randint(0, 0xFFFFFF):06x}'

NUM_RANDOM_LINES = 15
for _ in range(NUM_RANDOM_LINES):
    x1 = random.randint(0, CANVAS_WIDTH)
    y1 = random.randint(0, CANVAS_HEIGHT)
    x2 = random.randint(0, CANVAS_WIDTH)
    y2 = random.randint(0, CANVAS_HEIGHT)
    thickness = random.randint(MIN_LINE_THICKNESS, MAX_LINE_THICKNESS)
    line_color = get_random_color()
    canvas.create_line(x1, y1, x2, y2, width=thickness, fill=line_color)
"""
    },
    {
        "description": "6. **Randomizing Shapes (Rectangle):** Modified the initial rectangle to have random position, size, fill color, outline color, and outline thickness.",
        "code": """
# Generate random coordinates, ensuring x1 < x2 and y1 < y2
x1 = random.randint(0, CANVAS_WIDTH - 1)
y1 = random.randint(0, CANVAS_HEIGHT - 1)
x2 = random.randint(x1 + 1, CANVAS_WIDTH)
y2 = random.randint(y1 + 1, CANVAS_HEIGHT)

rect_fill_color = get_random_color()
rect_outline_color = get_random_color()
rect_outline_width = random.randint(MIN_RECT_OUTLINE, MAX_RECT_OUTLINE)

canvas.create_rectangle(
    x1, y1, x2, y2,
    fill=rect_fill_color,
    outline=rect_outline_color,
    width=rect_outline_width
)
"""
    },
    {
        "description": "7. **Multiple Random Rectangles:** Extended the randomization to draw multiple rectangles, each with unique random properties.",
        "code": """
NUM_RANDOM_RECTANGLES = 5
for _ in range(NUM_RANDOM_RECTANGLES):
    # (Code for generating random x1, y1, x2, y2, colors, width as in step 6)
    # ...
    canvas.create_rectangle(...) # Draw inside the loop
"""
    },
    {
        "description": "8. **Multiple Random Circles:** Applied the same randomization logic to circles (ovals), drawing multiple instances.",
        "code": """
NUM_RANDOM_CIRCLES = 5
for _ in range(NUM_RANDOM_CIRCLES):
    # Generate random coordinates for the bounding box (x1, y1, x2, y2)
    # ...
    circle_fill_color = get_random_color()
    circle_outline_color = get_random_color()
    circle_outline_width = random.randint(MIN_CIRCLE_OUTLINE, MAX_CIRCLE_OUTLINE)
    canvas.create_oval(
        x1, y1, x2, y2,
        fill=circle_fill_color,
        outline=circle_outline_color,
        width=circle_outline_width
    )
"""
    },
    {
        "description": "9. **Adding Polygons:** Introduced polygon shapes, generated using a helper function to create random vertices around a center point. Added multiple random polygons.",
        "code": """
import math

def generate_random_polygon_points(...):
    # ... (logic to calculate points using math.sin, math.cos)
    return points # Returns list like [x1, y1, x2, y2, ...]

NUM_RANDOM_POLYGONS = 4
for _ in range(NUM_RANDOM_POLYGONS):
    # Determine center, radius, vertices etc.
    # ...
    points = generate_random_polygon_points(...)
    poly_fill_color = get_random_color()
    poly_outline_color = get_random_color()
    poly_outline_width = random.randint(MIN_POLYGON_OUTLINE, MAX_POLYGON_OUTLINE)
    canvas.create_polygon(
        points,
        fill=poly_fill_color,
        outline=poly_outline_color,
        width=poly_outline_width
    )
"""
    },
    {
        "description": "10. **Contrasting Background:** Implemented a background composed of two randomly colored rectangles, split either horizontally or vertically.",
        "code": """
bg_color1 = get_random_color()
bg_color2 = get_random_color()
# ... (ensure colors differ)
split_direction = random.randint(0, 1) # 0=horizontal, 1=vertical

if split_direction == 0: # Horizontal split
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT / 2, fill=bg_color1, outline="")
    canvas.create_rectangle(0, CANVAS_HEIGHT / 2, CANVAS_WIDTH, CANVAS_HEIGHT, fill=bg_color2, outline="")
else: # Vertical split
    canvas.create_rectangle(0, 0, CANVAS_WIDTH / 2, CANVAS_HEIGHT, fill=bg_color1, outline="")
    canvas.create_rectangle(CANVAS_WIDTH / 2, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill=bg_color2, outline="")
"""
    },
    {
        "description": "11. **Non-Overlapping Shapes & Data Structure:** Implemented logic to prevent the main shapes from overlapping, storing shape data (not just bounds) in a list.",
        "code": """
placed_shapes_data = [] # List to store dictionaries like {'id': ..., 'type': ..., 'bounds': ...}

def check_overlap(box1, box2):
    # ... (returns True if boxes overlap, False otherwise)
    pass

# Inside shape generation loops (rect, circle, polygon):
for attempt in range(SHAPE_PLACEMENT_ATTEMPTS):
    # Generate potential bounds (current_bounds) and other shape data
    # ...
    overlaps = any(check_overlap(current_bounds, s['bounds']) for s in placed_shapes_data)

    if not overlaps:
        # Draw the shape
        shape_id = canvas.create_rectangle(...) # or create_oval/create_polygon
        shape_data = {'id': shape_id, 'type': 'rectangle', 'bounds': current_bounds, ...}
        placed_shapes_data.append(shape_data) # Store full data
        break # Exit attempt loop
"""
    },
    {
        "description": "12. **Adding Border and Constraints:** Defined a border, calculated inner bounds, constrained element generation to within these bounds, and drew the border.",
        "code": """
BORDER_THICKNESS = 15
INNER_X_MIN = BORDER_THICKNESS
INNER_Y_MIN = BORDER_THICKNESS
INNER_X_MAX = CANVAS_WIDTH - BORDER_THICKNESS
INNER_Y_MAX = CANVAS_HEIGHT - BORDER_THICKNESS

# Draw the border itself
canvas.create_rectangle(
    0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
    outline=BORDER_COLOR, width=BORDER_THICKNESS * 2
)

# Example: Constraining rectangle generation
size_x = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
size_y = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
# Generate top-left corner within the allowed inner area
x1 = random.randint(INNER_X_MIN, INNER_X_MAX - size_x)
y1 = random.randint(INNER_Y_MIN, INNER_Y_MAX - size_y)
x2 = x1 + size_x
y2 = y1 + size_y

# Similar constraints applied to circle, polygon, line, and dot generation
"""
    },
    {
        "description": "13. **Faint Background Shapes:** Added large, faint rectangles/ovals drawn underneath everything else for texture.",
        "code": """
def get_random_faint_color(...):
    # ... (generates light hex colors)
    pass

# Drawn *before* the main background split
num_faint_shapes = random.randint(4, 8)
for _ in range(num_faint_shapes):
    # Generate large size and position (can extend beyond canvas)
    # ...
    faint_color = get_random_faint_color()
    if random.choice([True, False]):
         canvas.create_rectangle(x1, y1, x2, y2, fill=faint_color, outline="")
    else:
         canvas.create_oval(x1, y1, x2, y2, fill=faint_color, outline="")
"""
    },
    {
        "description": "14. **Isometric Cube:** Added a function to draw a simulated 3D cube using isometric projection and simple shading. Integrated non-overlapping placement.",
        "code": """
def adjust_brightness(hex_color, factor):
    # ... (helper for shading)
    pass

def draw_isometric_cube(canvas_obj, center_x, center_y, size, color):
    # Calculate 7 visible points based on center and size
    # Define 3 faces (top, left, right) using points
    # Calculate shaded colors using adjust_brightness
    # Draw the 3 polygons (faces)
    # Return the 2D bounding box
    pass

# In main placement section:
# Loop NUM_RANDOM_CUBES:
#   Loop SHAPE_PLACEMENT_ATTEMPTS:
#     Choose size, color, center (within inner bounds, considering estimated size)
#     Calculate potential bounds
#     Check overlap with placed_shapes_data
#     If no overlap:
#       actual_bounds = draw_isometric_cube(...)
#       Store shape data (id=None, type='isometric_cube', bounds=actual_bounds, ...)
#       break
"""
    },
    {
        "description": "15. **Isometric Pyramid & Prism:** Added functions similar to the cube for drawing isometric square pyramids and rectangular prisms, with non-overlapping placement.",
        "code": """
def draw_isometric_pyramid(canvas_obj, center_x, center_y, base_size, height_factor, color):
    # Calculate apex and base corner points
    # Define visible faces (e.g., 2 triangles)
    # Calculate shaded colors
    # Draw the polygons
    # Return bounding box
    pass

def draw_isometric_prism(canvas_obj, center_x, center_y, width, depth, height, color):
    # Calculate 8 corner points based on dimensions
    # Define 3 visible faces (top, left, right)
    # Calculate shaded colors
    # Draw the polygons
    # Return bounding box
    pass

# In main placement section (similar loops as for cube):
# Place Pyramids...
# Place Prisms...
#   (Ensure overlap checks use the bounds returned by the draw functions)
#   Store shape data (id=None, type='isometric_pyramid'/'isometric_prism', ...)
"""
    },
    {
        "description": "16. **Animation Implementation:** Added core animation logic: selecting shapes, assigning targets, and updating position/color over time.",
        "code": """
animated_shapes = [] # List to hold animation state dictionaries

def hex_to_rgb / rgb_to_hex / interpolate_color:
    # ... (color manipulation helpers)
    pass

def assign_new_target_position(shape_info):
    # Get current coords and size
    # Calculate random target x, y within INNER bounds
    # Calculate distance, steps needed based on MOVEMENT_SPEED
    # Store dx, dy, move_steps_remaining in shape_info
    pass

def update_animation(canvas_obj, root):
    # Loop through animated_shapes:
    #   Update color: interpolate towards target_fill/target_outline
    #   Update position: move by dx, dy if steps remaining > 0
    #   Check boundaries: if hit edge, stop movement, assign new target
    #   If target reached (color/position): assign new random targets
    #   Handle errors (tk.TclError if shape deleted)
    # Schedule next call: root.after(UPDATE_INTERVAL_MS, update_animation, ...)
    pass

# In main, after placing shapes:
# Filter placed_shapes_data for items with an 'id'
# Select random subset for animation
# Initialize animation state dictionary for each selected shape
# Start the loop: root.after(100, update_animation, ...)
"""
    },
    {
        "description": "17. **Connecting Lines:** Added logic to draw lines connecting the centers of *static* (non-animated) shapes.",
        "code": """
# In main, after selecting animated shapes:
# Filter placed_shapes_data for shapes with 'id' NOT in animated_shapes set
static_shapes_to_connect = [...]

if len(static_shapes_to_connect) >= 2:
    # Loop NUM_CONNECTIONS:
    #   Randomly sample 2 different shapes from static_shapes_to_connect
    #   Get their 'center' coordinates
    #   Draw a line between centers (canvas.create_line)
    #   Lower the line behind other elements: canvas.tag_lower(line_id)
"""
    },
    {
        "description": "18. **Configuration Separation:** Moved all constants (sizes, counts, colors, animation parameters) from the main script (`3d_art.py`) into a dedicated `config.py` file. The main script now imports this module.",
        "code": """
# In config.py:
CANVAS_WIDTH = 600
NUM_RANDOM_DOTS = 30
# ... all other constants ...

# In 3d_art.py:
import config
# ... use config.CANVAS_WIDTH, config.NUM_RANDOM_DOTS etc. ...
"""
    },
    {
        "description": "19. **Color Utilities Separation:** Extracted color helper functions (`get_random_color`, `get_random_faint_color`, `hex_to_rgb`, `rgb_to_hex`, `interpolate_color`, `adjust_brightness`) into a new `colour_utils.py` module (Note: filename might be `color_utils.py`). Other modules now import these functions as needed.",
        "code": """
# In colour_utils.py (or color_utils.py):
import config # May need config for defaults
import random

def get_random_color(): ...
def adjust_brightness(hex_color, factor): ...
# ... other color functions ...

# In 3d_art.py:
import colour_utils # or color_utils
# ... use colour_utils.get_random_color(), colour_utils.interpolate_color() ...

# In shapes_3d.py:
from colour_utils import adjust_brightness # or color_utils
# ... use adjust_brightness() ...
"""
    },
    {
        "description": "20. **3D Shapes Separation:** Moved the isometric drawing functions (`draw_isometric_cube`, `draw_isometric_pyramid`, `draw_isometric_prism`) into a dedicated `shapes_3d.py` module. This module imports `adjust_brightness` from `colour_utils`. The main script now imports and uses these functions from `shapes_3d`.",
        "code": """
# In shapes_3d.py:
from colour_utils import adjust_brightness # or color_utils

def draw_isometric_cube(...): ...
def draw_isometric_pyramid(...): ...
def draw_isometric_prism(...): ...

# In 3d_art.py:
import shapes_3d
# ...
#   actual_bounds = shapes_3d.draw_isometric_cube(...)
# ...
"""
    },
    {
        "description": "21. **Save Utilities Separation:** Created a `save_utils.py` module to handle exporting the canvas content. It includes functions `export_to_png` (using Pillow/Ghostscript) and `export_to_svg` (using svgwrite, requiring scene reconstruction). The main script imports this module and adds buttons to trigger these functions.",
        "code": """
# In save_utils.py:
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image # Requires Pillow
import svgwrite      # Requires svgwrite
import io, os, config

def export_to_png(canvas): ...
def export_to_svg(canvas, placed_shapes_data): ... # Needs more data for full export

# In 3d_art.py:
import save_utils
# ... setup ...
png_button = tk.Button(..., command=lambda: save_utils.export_to_png(canvas))
svg_button = tk.Button(..., command=lambda: save_utils.export_to_svg(canvas, placed_shapes_data))
"""
    },
    # --- NEW STEP HERE ---
    {
        "description": "22. **UI Controls Implementation:** Added a `ui_controls.py` module defining a `ControlPanel` class with Tkinter sliders (`ttk.Scale`) to adjust parameters like shape counts and animation speed. Refactored `3d_art.py` to include this panel, extract generation logic into `generate_art(config)`, and add a 'Regenerate Art' button.",
        "code": """
# In ui_controls.py:
import tkinter as tk
from tkinter import ttk
import config

class ControlPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        # ... create tk.IntVar/DoubleVar for parameters ...
        # ... create ttk.Scale widgets linked to variables ...
    def get_values(self):
        # ... return dictionary of current values ...

# In 3d_art.py:
import ui_controls
# ... global controls = None ...

def generate_art(current_config):
    # ... clear canvas ...
    # ... get values from current_config dict ...
    # ... draw elements based on retrieved values ...
    # ... setup animation using current_config ...

def main():
    # ... setup root, frames ...
    global controls
    controls = ui_controls.ControlPanel(control_frame)
    controls.pack(...)
    # ... setup canvas ...
    regenerate_button = tk.Button(..., command=lambda: generate_art(controls.get_values()))
    # ... setup save buttons ...
    generate_art(controls.get_values()) # Initial generation
    root.mainloop()
"""
    }
]

# Define the filename
filename = "development_steps_with_code.txt"

# Write the steps and code snippets to the file
try:
    with open(filename, "w", encoding='utf-8') as f: # Added encoding for broader compatibility
        f.write("Development Steps for the Random 2D/3D Art Generator (with Code Snippets)\n")
        f.write("=========================================================================\n\n")
        for step_data in steps_data:
            # Write the description
            # Ensure description is treated as a string
            description_text = str(step_data.get("description", "Missing description"))
            description = textwrap.fill(description_text, width=80, initial_indent="", subsequent_indent="    ")
            f.write(description + "\n\n")

            # Write the code snippet in a formatted block
            code_text = step_data.get("code", "# No code snippet provided")
            f.write("```python\n")
            # Indent the code snippet for clarity within the file
            indented_code = textwrap.indent(code_text.strip(), '    ')
            f.write(indented_code + "\n")
            f.write("```\n\n") # Close the code block

    print(f"Successfully created '{filename}' with development steps and code snippets.")

except IOError as e:
    print(f"Error writing to file '{filename}': {e}")
except KeyError as e:
    print(f"Error: Missing key {e} in steps_data structure.")
except Exception as e: # Catch other potential errors
    print(f"An unexpected error occurred: {e}")
