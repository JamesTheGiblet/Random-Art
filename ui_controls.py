# ui_controls.py
import tkinter as tk
from tkinter import ttk # For themed widgets like Scale
import config # To get default values

class ControlPanel(tk.Frame):
    """A Tkinter frame containing controls for art generation parameters."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.config(bd=2, relief=tk.GROOVE) # Add some visual separation

        # --- Tkinter Variables ---
        # Use DoubleVar for sliders, IntVar for counts
        self.num_rectangles = tk.IntVar(value=config.NUM_RANDOM_RECTANGLES)
        self.num_circles = tk.IntVar(value=config.NUM_RANDOM_CIRCLES)
        self.num_polygons = tk.IntVar(value=config.NUM_RANDOM_POLYGONS)
        self.num_cubes = tk.IntVar(value=config.NUM_RANDOM_CUBES)
        self.num_pyramids = tk.IntVar(value=config.NUM_RANDOM_PYRAMIDS)
        self.num_prisms = tk.IntVar(value=config.NUM_RANDOM_PRISMS)
        self.num_dots = tk.IntVar(value=config.NUM_RANDOM_DOTS)
        self.num_lines = tk.IntVar(value=config.NUM_RANDOM_LINES)
        self.num_connections = tk.IntVar(value=config.NUM_CONNECTIONS)
        self.num_animated = tk.IntVar(value=config.NUM_ANIMATED_SHAPES)
        self.animation_speed = tk.DoubleVar(value=config.MOVEMENT_SPEED)

        # Store variables in a dictionary for easier access
        self.vars = {
            "NUM_RANDOM_RECTANGLES": self.num_rectangles,
            "NUM_RANDOM_CIRCLES": self.num_circles,
            "NUM_RANDOM_POLYGONS": self.num_polygons,
            "NUM_RANDOM_CUBES": self.num_cubes,
            "NUM_RANDOM_PYRAMIDS": self.num_pyramids,
            "NUM_RANDOM_PRISMS": self.num_prisms,
            "NUM_RANDOM_DOTS": self.num_dots,
            "NUM_RANDOM_LINES": self.num_lines,
            "NUM_CONNECTIONS": self.num_connections,
            "NUM_ANIMATED_SHAPES": self.num_animated,
            "MOVEMENT_SPEED": self.animation_speed,
        }

        self.create_widgets()

    def create_widgets(self):
        """Creates and packs the control widgets."""
        row_num = 0

        # --- Shape Counts ---
        tk.Label(self, text="Shape Counts:", font=('Arial', 10, 'bold')).grid(row=row_num, column=0, columnspan=2, sticky='w', padx=5, pady=(5,2))
        row_num += 1

        self._add_slider("Rectangles:", self.num_rectangles, 0, 20, row_num)
        row_num += 1
        self._add_slider("Circles:", self.num_circles, 0, 20, row_num)
        row_num += 1
        self._add_slider("Polygons:", self.num_polygons, 0, 20, row_num)
        row_num += 1
        self._add_slider("Cubes:", self.num_cubes, 0, 10, row_num)
        row_num += 1
        self._add_slider("Pyramids:", self.num_pyramids, 0, 10, row_num)
        row_num += 1
        self._add_slider("Prisms:", self.num_prisms, 0, 10, row_num)
        row_num += 1

        # --- Decorative Elements ---
        tk.Label(self, text="Decorations:", font=('Arial', 10, 'bold')).grid(row=row_num, column=0, columnspan=2, sticky='w', padx=5, pady=(10,2))
        row_num += 1
        self._add_slider("Dots:", self.num_dots, 0, 100, row_num)
        row_num += 1
        self._add_slider("Lines:", self.num_lines, 0, 30, row_num)
        row_num += 1
        self._add_slider("Connections:", self.num_connections, 0, 20, row_num)
        row_num += 1

        # --- Animation ---
        tk.Label(self, text="Animation:", font=('Arial', 10, 'bold')).grid(row=row_num, column=0, columnspan=2, sticky='w', padx=5, pady=(10,2))
        row_num += 1
        self._add_slider("Animated Shapes:", self.num_animated, 0, 10, row_num)
        row_num += 1
        self._add_slider("Anim Speed:", self.animation_speed, 0.1, 5.0, row_num, resolution=0.1)
        row_num += 1


    def _add_slider(self, label_text, variable, from_, to, row, resolution=1):
        """Helper to add a label and a scale (slider)."""
        label = tk.Label(self, text=label_text)
        label.grid(row=row, column=0, sticky='w', padx=5, pady=2)

        slider = ttk.Scale(
            self,
            orient=tk.HORIZONTAL,
            variable=variable,
            from_=from_,
            to=to,
            # resolution=resolution, # ttk.Scale doesn't have resolution
            length=150
        )
        # For ttk.Scale, we can manually update a label to show the value if needed,
        # or rely on the user knowing the range. For simplicity, we omit the value label here.
        # If using tk.Scale, you can add resolution and showvalue=True/False
        slider.grid(row=row, column=1, sticky='ew', padx=5, pady=2)

        # Add a label to display the current value (optional but helpful)
        value_label = tk.Label(self, textvariable=variable, width=4)
        value_label.grid(row=row, column=2, sticky='e', padx=(0, 5), pady=2)


    def get_values(self):
        """Returns a dictionary of the current values from the controls."""
        # Ensure integer values for counts
        return {key: var.get() for key, var in self.vars.items()}

# --- Example Usage (for testing ui_controls.py directly) ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("UI Controls Test")
    panel = ControlPanel(root)
    panel.pack(padx=10, pady=10, fill="both", expand=True)

    def show_values():
        print(panel.get_values())

    test_button = tk.Button(root, text="Show Values", command=show_values)
    test_button.pack(pady=5)

    root.mainloop()
