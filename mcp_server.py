import os
from mcp.server.fastmcp import FastMCP  # Add MCP import
from notebookllm import Notebook


mcp = FastMCP(name="NotebookLLMServer", description="A server to efficiently interact with Jupyter Notebooks by converting them to token-friendly plain text. This process significantly saves costs and improves processing speed when working with LLMs.")

# Store the loaded notebook in memory.
loaded_notebook: Notebook | None = None
loaded_notebook_path: str | None = None

@mcp.tool()
def load_notebook(filepath: str) -> str:
    """Loads a .ipynb file into memory. Prepares notebook for efficient, cost-effective text-based operations with LLMs.
    Args:
        filepath (str): The absolute path to the .ipynb file.
    Returns:
        str: A message indicating success or failure, including cell count for context.
    """
    global loaded_notebook, loaded_notebook_path
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
        if not filepath.endswith(".ipynb"):
            return "Error: Filepath must be for a .ipynb file."
        loaded_notebook = Notebook(filepath)
        loaded_notebook_path = filepath
        return f"Successfully loaded notebook: {filepath}. It has {len(loaded_notebook.cells)} cells. Ready for efficient text conversion."
    except Exception as e:
        loaded_notebook = None
        loaded_notebook_path = None
        return f"Error loading notebook: {str(e)}"

@mcp.tool()
def notebook_to_plain_text(input_filepath: str | None = None) -> str:
    """Converts a .ipynb file to a simplified plain text representation, stripping metadata to save tokens and reduce LLM processing costs and time.
    If input_filepath is provided, it loads and converts that file.
    Otherwise, it efficiently converts the currently loaded notebook.

    Args:
        input_filepath (str, optional): The absolute path to the .ipynb file for on-the-fly conversion.
    Returns:
        str: The token-efficient plain text representation of the notebook or an error message.
    """
    global loaded_notebook
    try:
        notebook_to_convert = None
        status_prefix = ""
        if input_filepath:
            if not os.path.exists(input_filepath):
                return f"Error: Input file not found at {input_filepath}"
            if not input_filepath.endswith(".ipynb"):
                return "Error: Input filepath must be for a .ipynb file."
            notebook_to_convert = Notebook(input_filepath)
            status_prefix = f"Converted notebook from {input_filepath}."
        elif loaded_notebook:
            notebook_to_convert = loaded_notebook
            status_prefix = "Converted currently loaded notebook."
        else:
            return "Error: No notebook loaded and no input_filepath provided. Use load_notebook() or provide input_filepath for efficient conversion."

        plain_text = notebook_to_convert.to_plain_text()
        return f"{status_prefix} Plain text (optimized for token and cost savings):\n\n{plain_text}"
    except Exception as e:
        return f"Error converting notebook to plain text: {str(e)}"

@mcp.tool()
def plain_text_to_notebook_file(plain_text_content: str, output_filepath: str) -> str:
    """Converts token-efficient plain text content (with special markers) back to a .ipynb file and saves it. Enables cost-effective round-trip editing with LLMs.

    Args:
        plain_text_content (str): The plain text content (optimized for LLMs) to convert.
        output_filepath (str): The absolute path where the .ipynb file should be saved. Must end with '.ipynb'.
    Returns:
        str: A message indicating success or failure of the save operation.
    """
    global loaded_notebook, loaded_notebook_path
    try:
        if not output_filepath.endswith(".ipynb"):
            return "Error: Output filepath must end with .ipynb"

        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        new_notebook = Notebook.from_plain_text(plain_text_content)
        new_notebook.save(output_filepath)
        # Update the loaded notebook to the one just created and saved
        loaded_notebook = new_notebook
        loaded_notebook_path = output_filepath
        return f"Successfully converted plain text to notebook and saved to: {output_filepath}. It is now the active notebook, enabling further efficient operations."
    except Exception as e:
        return f"Error converting plain text to notebook: {str(e)}"

@mcp.tool()
def add_code_cell_to_loaded_notebook(code_content: str, position: int | None = None) -> str:
    """Adds a new code cell to the currently loaded notebook. Efficiently modifies the notebook structure in memory.

    Args:
        code_content (str): The source code for the new cell.
        position (int, optional): The position at which to insert the cell. Appends if None for quick addition.
    Returns:
        str: A message indicating success or failure and current cell count.
    """
    global loaded_notebook
    if not loaded_notebook:
        return "Error: No notebook is currently loaded. Use load_notebook() first for efficient cell manipulation."
    try:
        loaded_notebook.add_code_cell(source=code_content, position=position)
        return f"Added code cell. Loaded notebook now has {len(loaded_notebook.cells)} cells. Modification was efficient."
    except Exception as e:
        return f"Error adding code cell: {str(e)}"

@mcp.tool()
def add_markdown_cell_to_loaded_notebook(markdown_content: str, position: int | None = None) -> str:
    """Adds a new markdown cell to the currently loaded notebook. Efficiently updates the notebook's narrative content.

    Args:
        markdown_content (str): The markdown content for the new cell.
        position (int, optional): The position at which to insert the cell. Appends if None for quick addition.
    Returns:
        str: A message indicating success or failure and current cell count.
    """
    global loaded_notebook
    if not loaded_notebook:
        return "Error: No notebook is currently loaded. Use load_notebook() first for efficient cell manipulation."
    try:
        loaded_notebook.add_markdown_cell(source=markdown_content, position=position)
        return f"Added markdown cell. Loaded notebook now has {len(loaded_notebook.cells)} cells. Modification was efficient."
    except Exception as e:
        return f"Error adding markdown cell: {str(e)}"

@mcp.tool()
def save_loaded_notebook(output_filepath: str | None = None) -> str:
    """Saves the currently loaded notebook to a file. Efficiently persists changes made in memory.
    If output_filepath is provided, saves to that path.
    Otherwise, saves to its original path, ensuring data integrity with minimal overhead.

    Args:
        output_filepath (str, optional): The absolute path to save the .ipynb file. Must end with '.ipynb'.
    Returns:
        str: A message indicating success or failure of the save operation.
    """
    global loaded_notebook, loaded_notebook_path
    if not loaded_notebook:
        return "Error: No notebook is currently loaded. Use load_notebook() first to enable saving."
    try:
        save_path = output_filepath
        if save_path:
            if not save_path.endswith(".ipynb"):
                return "Error: Output filepath must end with .ipynb"
            # Ensure the directory for the output file exists
            output_dir = os.path.dirname(save_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
        elif loaded_notebook_path:
            save_path = loaded_notebook_path
        else:
            return "Error: No output path specified and the notebook was not loaded from a file. Cannot efficiently save."

        loaded_notebook.save(save_path)
        if output_filepath: # If a new path was provided, update the loaded_notebook_path
            loaded_notebook_path = output_filepath
        return f"Successfully and efficiently saved notebook to: {save_path}"
    except Exception as e:
        return f"Error saving notebook: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
