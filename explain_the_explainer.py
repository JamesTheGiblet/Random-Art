import textwrap

# Define the steps explaining 'the_explainer.py' script (formerly steps.py)
explainer_steps_data = [
    {
        # Updated description to refer to the_explainer.py
        "description": "0. **Purpose:** The `the_explainer.py` script is a meta-script. Its primary function is to generate a text file (`development_steps_with_code.txt`) that documents the development process and logic of the main application script (`3d_art.py`). It does this by storing descriptions and corresponding code snippets in a structured way.",
        "code_context": """
# (Conceptual overview of the_explainer.py's goal)
# It reads predefined steps and code examples related to 3d_art.py...
# ...and writes them into a formatted text file.
"""
    },
    {
        "description": "1. **Import `textwrap`:** The script begins by importing the `textwrap` module. This standard Python library is crucial for formatting the text content (both descriptions and code snippets) nicely within the output file, ensuring readability by controlling line wrapping and indentation.",
        "code_context": """
import textwrap
"""
    },
    {
        # Updated description
        "description": "2. **Define `steps_data` Structure:** The core content is stored in a list named `steps_data`. Each element in this list is a dictionary representing a single development step from `3d_art.py`. Each dictionary contains at least two keys:",
        "code_context": """
steps_data = [
    {
        "description": "...", # Text explaining a step in 3d_art.py
        "code": "\"\"\"...\"\"\""     # Code snippet illustrating that step
    },
    # ... more steps
]
"""
    },
    {
        # Updated description
        "description": "3. **Define Output Filename (for `the_explainer.py`):** A variable `filename` is defined within `the_explainer.py` to hold the name of the text file that script will create (e.g., `development_steps_with_code.txt`). This makes it easy to change the output file's name if needed.",
        "code_context": """
# Inside the_explainer.py:
filename = "development_steps_with_code.txt"
"""
    },
    {
        "description": "4. **File Handling (`try...with open`)**: The script uses a `try...except` block combined with `with open(...)` to safely handle file operations. `with open(...)` ensures the file is automatically closed even if errors occur. The file is opened in write mode (`'w'`) with UTF-8 encoding specified for better compatibility.",
        "code_context": """
# Inside the_explainer.py:
try:
    with open(filename, "w", encoding='utf-8') as f:
        # ... file writing operations ...
except IOError as e:
    # ... error handling ...
"""
    },
    {
        "description": "5. **Write Header:** Inside the `with` block, a title and a separator line are written to the beginning of the output file.",
        "code_context": """
# Inside the_explainer.py:
    with open(filename, "w", encoding='utf-8') as f:
        f.write("Development Steps for the Random 2D/3D Art Generator (with Code Snippets)\\n")
        f.write("=========================================================================\\n\\n")
        # ... rest of the writing ...
"""
    },
    {
        "description": "6. **Iterate and Format Content:** The script loops through each dictionary (`step_data`) in the `steps_data` list.",
        "code_context": """
# Inside the_explainer.py:
        for step_data in steps_data:
            # ... formatting and writing for each step ...
"""
    },
    {
        "description": "7. **Format Description:** Inside the loop, `textwrap.fill()` is used to format the `description` text. It wraps long lines to a specified width (80 characters) and applies indentation, making the descriptions easier to read in the text file.",
        "code_context": """
# Inside the_explainer.py:
            description_text = str(step_data.get("description", "Missing description"))
            description = textwrap.fill(description_text, width=80, initial_indent="", subsequent_indent="    ")
            f.write(description + "\\n\\n")
"""
    },
    {
        "description": "8. **Format Code Snippet:** The `code` snippet is retrieved. `textwrap.indent()` adds indentation to each line of the code. The indented code is then wrapped in Markdown-style code fences (```python ... ```) before being written to the file.",
        "code_context": """
# Inside the_explainer.py:
            code_text = step_data.get("code", "# No code snippet provided")
            f.write("```python\\n")
            indented_code = textwrap.indent(code_text.strip(), '    ')
            f.write(indented_code + "\\n")
            f.write("```\\n\\n")
"""
    },
    {
        # Updated description
        "description": "9. **Error Handling:** The `except` blocks catch potential errors during file writing (`IOError`), issues with the `steps_data` structure (`KeyError`), or any other unexpected problems (`Exception`), printing an informative message to the console if an error occurs.",
        "code_context": """
# Inside the_explainer.py:
except IOError as e:
    print(f"Error writing to file '{filename}': {e}")
except KeyError as e:
    print(f"Error: Missing key {e} in steps_data structure.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
"""
    },
    {
        # Updated description
        "description": "10. **Completion Message:** If the file is written successfully, a confirmation message is printed to the console.",
        "code_context": """
# Inside the_explainer.py:
    print(f"Successfully created '{filename}' with development steps and code snippets.")
"""
    }
]

# Define the filename for *this* script's output (explaining the_explainer.py)
# Updated filename to reflect what it's explaining
output_filename = "the_explainer_explanation.txt"

# Write the explanation of the_explainer.py to the new file
try:
    with open(output_filename, "w", encoding='utf-8') as f:
        # Updated title
        f.write("Explanation of the 'the_explainer.py' Script\n")
        f.write("==========================================\n\n")
        # Updated introductory sentence
        f.write("This file explains the structure and logic of the 'the_explainer.py' script, which itself generates documentation for '3d_art.py'.\n\n")

        for step_info in explainer_steps_data:
            # Write the description
            description_text = str(step_info.get("description", "Missing description"))
            description = textwrap.fill(description_text, width=80, initial_indent="", subsequent_indent="    ")
            f.write(description + "\n\n")

            # Write the code context snippet if it exists
            code_context_text = step_info.get("code_context")
            if code_context_text:
                f.write("```python\n")
                # Indent the code snippet for clarity within the file
                indented_code = textwrap.indent(code_context_text.strip(), '    ')
                f.write(indented_code + "\n")
                f.write("```\n\n") # Close the code block

    # Updated success message
    print(f"Successfully created '{output_filename}' explaining the 'the_explainer.py' script.")

except IOError as e:
    print(f"Error writing to file '{output_filename}': {e}")
except KeyError as e:
    print(f"Error: Missing key {e} in explainer_steps_data structure.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
