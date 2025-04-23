# save_utils.py

import tkinter as tk
from tkinter import filedialog, messagebox
import io
import os
import config # Needs canvas dimensions

# --- Dependencies for Export ---
# Pillow is needed for PNG export via PostScript
try:
    from PIL import Image, ImageTk # ImageTk might not be needed here but often used with Pillow+Tk
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    print("Warning: Pillow library not found. PNG export via PostScript will require manual conversion.")
    print("Install Pillow: pip install Pillow")

# svgwrite is needed for SVG export
try:
    import svgwrite
    _HAS_SVGWRITE = True
except ImportError:
    _HAS_SVGWRITE = False
    print("Warning: svgwrite library not found. SVG export will be disabled.")
    print("Install svgwrite: pip install svgwrite")

# Note: PNG export also relies on Ghostscript being installed and in the system PATH.
# This check is done implicitly when Pillow tries to open the PostScript data.


def export_to_png(canvas):
    """
    Prompts the user for a filename and exports the canvas content to a PNG file.
    Requires Pillow and Ghostscript. Falls back to saving PostScript if conversion fails.

    Args:
        canvas: The Tkinter Canvas object to export.
    """
    if not _HAS_PIL:
        messagebox.showerror("Missing Library", "PNG export requires the Pillow library.\nPlease install it (`pip install Pillow`).")
        return

    try:
        # 1. Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Canvas as PNG"
        )
        if not file_path:
            print("PNG Export cancelled.")
            return

        print(f"Exporting PNG to {file_path}...")

        # 2. Generate PostScript in memory
        ps_data = canvas.postscript(colormode='color')
        ps_bytes = ps_data.encode('utf-8') # Encode to bytes for Pillow

        # 3. Use Pillow to open the PostScript data and save as PNG
        try:
            # Pillow uses Ghostscript under the hood here
            img = Image.open(io.BytesIO(ps_bytes))
            img.save(file_path, "png")
            print(f"Successfully saved PNG to {file_path}")
            messagebox.showinfo("Export Successful", f"Saved PNG to:\n{file_path}")
        except Exception as pillow_e:
            # Pillow might raise an exception if Ghostscript isn't found or fails
            print(f"Error converting PostScript to PNG: {pillow_e}")
            # Fallback: Save the PostScript file directly for manual conversion
            ps_file_path = os.path.splitext(file_path)[0] + ".ps"
            try:
                with open(ps_file_path, "wb") as f:
                    f.write(ps_bytes)
                print(f"Saved PostScript file for manual conversion: {ps_file_path}")
                messagebox.showwarning("Conversion Failed",
                                       "Could not convert to PNG (Ghostscript missing or error).\n"
                                       f"Saved PostScript file instead:\n{ps_file_path}")
            except Exception as ps_e:
                 print(f"Could not save PostScript file: {ps_e}")
                 messagebox.showerror("Export Error", f"Could not convert to PNG or save PostScript file.\nError: {ps_e}")

    except tk.TclError as tcl_e:
         print(f"Tkinter error during PostScript generation: {tcl_e}")
         messagebox.showerror("Export Error", f"Error generating canvas data.\nTkinter Error: {tcl_e}")
    except Exception as e:
        print(f"An unexpected error occurred during PNG export: {e}")
        messagebox.showerror("Export Error", f"An unexpected error occurred.\nError: {e}")


def export_to_svg(canvas, placed_shapes_data):
    """
    Prompts the user for a filename and exports the generated art scene to an SVG file.
    Requires svgwrite. Reconstructs the scene based on stored data.

    Args:
        canvas: The Tkinter Canvas object (used for reference, not direct export).
        placed_shapes_data: A list of dictionaries containing data about each placed shape.
                            (Needs to be comprehensive for accurate SVG).
    """
    if not _HAS_SVGWRITE:
        messagebox.showerror("Missing Library", "SVG export requires the svgwrite library.\nPlease install it (`pip install svgwrite`).")
        return

    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            title="Save Art as SVG"
        )
        if not file_path:
            print("SVG Export cancelled.")
            return

        print(f"Exporting SVG to {file_path}...")
        dwg = svgwrite.Drawing(file_path, size=(config.CANVAS_WIDTH, config.CANVAS_HEIGHT), profile='full') # Use 'full' for gradients etc. if needed

        # --- Group for background elements ---
        bg_group = dwg.g(id='background')
        dwg.add(bg_group)

        # --- Re-draw Backgrounds ---
        # TODO: This requires storing/accessing background info (faint shapes, split colors)
        # Example placeholder: Add a simple white background rect
        bg_group.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
        print("SVG Export: Background drawing is currently a placeholder.")

        # --- Group for main shapes ---
        shapes_group = dwg.g(id='shapes')
        dwg.add(shapes_group)

        # --- Re-draw Placed Shapes ---
        # This relies heavily on the structure and completeness of placed_shapes_data
        for shape_data in placed_shapes_data:
            fill = shape_data.get('fill', 'none')
            stroke = shape_data.get('outline', 'none')
            # Attempt to get stroke width, default to 1 if not specified or invalid
            try:
                # Tkinter width might be stored if shape has ID, otherwise default
                item_id = shape_data.get('id')
                if item_id:
                    stroke_width = canvas.itemcget(item_id, 'width')
                    # Ensure it's a valid number, default if not
                    stroke_width = float(stroke_width) if stroke_width else 1.0
                else:
                    # For composite shapes (like 3D), default outline width
                    stroke_width = 1.0
            except (tk.TclError, ValueError):
                stroke_width = 1.0 # Default on error

            # Ensure stroke is 'none' if width is 0 or less
            if stroke_width <= 0:
                stroke = 'none'
                stroke_width = 0

            shape_type = shape_data.get('type', 'unknown')
            bounds = shape_data.get('bounds')

            try:
                if shape_type == 'rectangle' and bounds:
                    x1, y1, x2, y2 = bounds
                    shapes_group.add(dwg.rect(insert=(x1, y1), size=(x2 - x1, y2 - y1),
                                     fill=fill, stroke=stroke, stroke_width=stroke_width))
                elif shape_type == 'oval' and bounds:
                     x1, y1, x2, y2 = bounds
                     cx = (x1 + x2) / 2
                     cy = (y1 + y2) / 2
                     rx = abs(x2 - x1) / 2
                     ry = abs(y2 - y1) / 2
                     shapes_group.add(dwg.ellipse(center=(cx, cy), r=(rx, ry),
                                         fill=fill, stroke=stroke, stroke_width=stroke_width))
                elif shape_type == 'polygon' and shape_data.get('id'):
                     # Get points directly from canvas item if possible
                     points_list = canvas.coords(shape_data['id'])
                     shapes_group.add(dwg.polygon(points=points_list,
                                         fill=fill, stroke=stroke, stroke_width=stroke_width))
                elif shape_type in ['isometric_cube', 'isometric_pyramid', 'isometric_prism']:
                    # TODO: This needs the most work. Requires storing individual face data
                    # (points and color) when the shape is initially drawn, or recalculating them.
                    # Placeholder: Draw a simple rectangle at the bounds
                    if bounds:
                        x1, y1, x2, y2 = bounds
                        shapes_group.add(dwg.rect(insert=(x1, y1), size=(x2 - x1, y2 - y1),
                                         fill=fill, stroke='grey', stroke_dasharray="5,5"))
                    print(f"SVG Export: 3D shape '{shape_type}' drawing is a placeholder.")

                # TODO: Add handling for dots, lines, connection lines by iterating
                # through their respective data structures (if they exist separately)

            except Exception as shape_e:
                print(f"SVG Export: Error drawing shape {shape_data.get('id', 'N/A')} ({shape_type}): {shape_e}")


        # --- Draw Border (Optional) ---
        # dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'),
        #                  fill='none', stroke=config.BORDER_COLOR, stroke_width=config.BORDER_THICKNESS))

        dwg.save(pretty=True) # pretty=True adds indentation
        print(f"Successfully saved SVG to {file_path}")
        messagebox.showinfo("Export Successful", f"Saved SVG to:\n{file_path}\n(Note: SVG export might be incomplete)")

    except Exception as e:
        print(f"An unexpected error occurred during SVG export: {e}")
        messagebox.showerror("Export Error", f"An unexpected error occurred during SVG export.\nError: {e}")

