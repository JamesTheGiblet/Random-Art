# shapes_3d.py
from colour_utils import adjust_brightness # Import the needed color utility

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
    canvas_obj.create_polygon(left_face, fill=left_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(right_face, fill=right_color, outline=outline_col, width=1)

    # Calculate the 2D bounding box
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
    p0 = (center_x - offset_x_w + offset_x_d, center_y + offset_y_w + offset_y_d - offset_y_h) # Bottom front-left
    p1 = (center_x + offset_x_w + offset_x_d, center_y - offset_y_w + offset_y_d - offset_y_h) # Bottom back-left (often hidden)
    p2 = (center_x + offset_x_w - offset_x_d, center_y - offset_y_w - offset_y_d - offset_y_h) # Bottom back-right
    p3 = (center_x - offset_x_w - offset_x_d, center_y + offset_y_w - offset_y_d - offset_y_h) # Bottom front-right
    p4 = (p0[0], p0[1] + height) # Top front-left
    p5 = (p1[0], p1[1] + height) # Top back-left (often hidden)
    p6 = (p2[0], p2[1] + height) # Top back-right
    p7 = (p3[0], p3[1] + height) # Top front-right

    # Define the three visible faces
    top_face = [p4, p5, p6, p7]
    left_face = [p0, p3, p7, p4]
    right_face = [p3, p2, p6, p7]

    # Simple shading
    top_color = adjust_brightness(color, 1.2)  # Lighter top
    left_color = adjust_brightness(color, 0.8) # Darker left
    right_color = adjust_brightness(color, 0.6) # Darkest right

    outline_col = "black"

    # Draw faces
    canvas_obj.create_polygon(left_face, fill=left_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(right_face, fill=right_color, outline=outline_col, width=1)
    canvas_obj.create_polygon(top_face, fill=top_color, outline=outline_col, width=1)

    # Calculate the 2D bounding box
    all_points = [p0, p1, p2, p3, p4, p5, p6, p7]
    all_x = [p[0] for p in all_points]
    all_y = [p[1] for p in all_points]
    bounds = (min(all_x), min(all_y), max(all_x), max(all_y))

    return bounds
