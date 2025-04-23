# color_utils.py
import random
import config # Needs config for faint color defaults

def get_random_color():
    """Generates a random hex color code."""
    return f'#{random.randint(0, 0xFFFFFF):06x}'

def get_random_faint_color(min_brightness=config.FAINT_COLOR_MIN_BRIGHTNESS,
                           max_brightness=config.FAINT_COLOR_MAX_BRIGHTNESS):
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

def hex_to_rgb(hex_color):
    """Converts a hex color string (e.g., '#ffffff') to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6: return (0, 0, 0) # Return black for invalid format
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        print(f"Warning: Invalid hex color value '{hex_color}'. Using black.")
        return (0, 0, 0) # Return black for invalid hex values

def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple to a hex color string."""
    try:
        rgb_clamped = tuple(max(0, min(255, int(c))) for c in rgb)
        return f'#{rgb_clamped[0]:02x}{rgb_clamped[1]:02x}{rgb_clamped[2]:02x}'
    except (ValueError, TypeError):
        print(f"Warning: Invalid RGB value '{rgb}'. Using black.")
        return '#000000'

def interpolate_color(color1_hex, color2_hex, factor):
    """Finds a color between color1 and color2. factor = 0.0 -> color1, factor = 1.0 -> color2."""
    rgb1 = hex_to_rgb(color1_hex)
    rgb2 = hex_to_rgb(color2_hex)
    # Clamp factor
    factor = max(0.0, min(1.0, factor))
    try:
        new_rgb = [rgb1[i] + (rgb2[i] - rgb1[i]) * factor for i in range(3)]
        return rgb_to_hex(tuple(new_rgb))
    except (IndexError, TypeError):
         print(f"Warning: Error interpolating colors '{color1_hex}' and '{color2_hex}'. Using color1.")
         return color1_hex


def adjust_brightness(hex_color, factor):
    """Adjusts the brightness of a hex color by a factor. Clamps result between #000000 and #ffffff."""
    rgb = hex_to_rgb(hex_color)
    if factor < 0: factor = 0 # Prevent negative factors

    try:
        # Adjust each component, clamping between 0 and 255
        new_rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
        return rgb_to_hex(new_rgb)
    except (TypeError):
        print(f"Warning: Error adjusting brightness for '{hex_color}'. Returning original.")
        return hex_color
