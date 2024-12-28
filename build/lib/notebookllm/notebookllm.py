import nbformat
from nbformat import v4
from jupyter_client import KernelManager
import json
import os
import uuid
from typing import Dict, List, Any, Union, Tuple
import re
import textwrap


class Notebook:
    """Represents a Jupyter Notebook and provides methods for interaction."""

    def __init__(self, filepath: str = None):
        """
        Initializes a Notebook object.

        Args:
            filepath (str, optional): Path to the .ipynb file. If None, creates a new empty notebook. Defaults to None.
        """
        self.filepath = filepath
        self._notebook = self.load_notebook_from_file(filepath) if filepath else v4.new_notebook()
        self._kernel_manager = None
        self._kernel_client = None
        self.kernel_id = None

    def load_notebook_from_file(self, filepath: str) -> nbformat.NotebookNode:
        """Loads a notebook from the given file path.

        Args:
            filepath (str): The path to the .ipynb file.

        Returns:
            nbformat.NotebookNode: The loaded notebook object.

        Raises:
             FileNotFoundError: If the specified file does not exist.
             nbformat.reader.NotJSONError: If the file is not a valid JSON.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file '{filepath}' was not found.")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return nbformat.read(f, as_version=4)
        except json.decoder.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON in {filepath}: {e}")

    @property
    def cells(self) -> List[Dict[str, Any]]:
        """Returns a list of cell dictionaries.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing cells.
        """
        return self._notebook.cells

    @property
    def metadata(self) -> Dict[str, Any]:
        """Returns the notebook's metadata.

        Returns:
            Dict[str, Any]: A dictionary containing metadata.
        """
        return self._notebook.metadata

    def add_code_cell(self, source: str, position: int = None) -> None:
        """Adds a new code cell to the notebook.

        Args:
            source (str): The code to add to the cell.
            position (int, optional): The position at which to insert the cell. If None, appends to end. Defaults to None.
        """
        cell = v4.new_code_cell(source=source)
        self.insert_cell_at_position(cell, position)

    def add_markdown_cell(self, source: str, position: int = None) -> None:
        """Adds a new markdown cell to the notebook.

        Args:
             source (str): The markdown to add to the cell.
            position (int, optional): The position at which to insert the cell. If None, appends to end. Defaults to None.
        """
        cell = v4.new_markdown_cell(source=source)
        self.insert_cell_at_position(cell, position)

    def add_raw_cell(self, source: str, position: int = None, **kwargs) -> None:
        """Adds a new raw cell to the notebook.

        Args:
            source (str): The content of the raw cell.
            position (int, optional): The position at which to insert the cell. If None, appends to end. Defaults to None.
            **kwargs: Any additional arguments that need to passed to the raw cell such as  `metadata`
        """
        cell = v4.new_raw_cell(source=source, **kwargs)
        self.insert_cell_at_position(cell, position)

    def insert_cell_at_position(self, cell: Dict, position: int = None) -> None:
        """Inserts a cell at the specified position.

        Args:
            cell (Dict): The cell to insert.
            position (int, optional): The position at which to insert the cell. If None, appends to the end. Defaults to None.

        Raises:
            ValueError: if the given postion is out of range
        """
        if position is None:
            self._notebook.cells.append(cell)
        elif 0 <= position <= len(self._notebook.cells):
            self._notebook.cells.insert(position, cell)
        else:
            raise ValueError("Invalid position for cell insertion")

    def delete_cell(self, index: int) -> None:
        """Deletes a cell at the specified index.

        Args:
            index (int): The index of the cell to delete.

        Raises:
            IndexError: If the given index is out of range.
        """
        try:
            del self._notebook.cells[index]
        except IndexError:
            raise IndexError(f"Cell index {index} is out of range.")

    def edit_cell(self, index: int, source: str, cell_type: str = None) -> None:
        """Edits a cell at the specified index.
        Args:
            index (int): The index of the cell to edit.
            source (str): The new source for the cell
            cell_type (str, optional): The cell type to change the cell into (if desired). Defaults to None which keeps the cell type.

        Raises:
            IndexError: If the given index is out of range.
            ValueError: If cell_type is provided, but it isn't a valid type
        """
        try:
            cell = self._notebook.cells[index]
            if cell_type:
                if cell_type not in ("code", "markdown", "raw"):
                    raise ValueError(
                        f"Invalid cell type '{cell_type}'. Must be 'code', 'markdown', or 'raw'."
                    )

                cell.cell_type = cell_type
            cell.source = source

        except IndexError:
            raise IndexError(f"Cell index {index} is out of range.")

    def set_metadata(self, key: str, value: Any) -> None:
        """Sets a metadata entry for the notebook.

         Args:
            key (str): metadata key to be set
            value (Any): metadata value to set
         """
        self._notebook.metadata[key] = value

    def start_kernel(self, kernel_name: str = "python3"):
        """Starts a Jupyter kernel for code execution.

          Args:
            kernel_name (str, optional): The name of the kernel to start. Defaults to "python3".
         """
        if self._kernel_manager is None:
            self._kernel_manager = KernelManager(kernel_name=kernel_name)
            self._kernel_manager.start_kernel()
            self._kernel_client = self._kernel_manager.client()
            self._kernel_client.start_channels()
            self.kernel_id = self._kernel_manager.kernel.kernel_id
        else:
            return self._kernel_client

    def is_kernel_connected(self) -> bool:
        """Checks if a kernel client is available
           Returns:
             bool: True if a kernel client is available, else False
        """
        return self._kernel_client and self._kernel_client.is_alive()

    def execute_cell(self, index: int, timeout: int = 60, iopub_timeout: int = 5) -> Dict[str, List[Union[str, Dict[str, Any]]]]:
        """Executes a code cell at the specified index and returns the output.

         Args:
            index (int): The index of the code cell to execute.

         Returns:
            Dict[str, Any]: A dictionary containing execution output (stdout, stderr, display data),
            or an error message if the cell is not code.

         Raises:
           IndexError: If the given index is out of range.
         """
        if not self.is_kernel_connected():
            raise RuntimeError(
                "Kernel is not running, please call 'start_kernel()' before execution."
            )

        try:
            cell = self._notebook.cells[index]
            if cell.cell_type != "code":
                raise ValueError("Cell is not a code cell.")

            msg_id = self._kernel_client.execute(cell.source)
            reply = self._kernel_client.get_shell_msg(timeout=60, stop_on_error=True)

            if reply["content"]["status"] == "error":
                raise RuntimeError(f"Error executing cell: {reply['content']}")

            output = {"stdout": [], "stderr": [], "display_data": []}
            while True:
                try:
                    msg = self._kernel_client.get_iopub_msg(timeout=5)
                    if msg["parent_header"]["msg_id"] == msg_id:
                        msg_type = msg["msg_type"]

                        if msg_type == "stream":
                            if msg["content"]["name"] == "stdout":
                                output["stdout"].append(msg["content"]["text"])
                            else:
                                output["stderr"].append(msg["content"]["text"])
                        elif msg_type == "display_data":
                            output["display_data"].append(msg["content"]["data"])
                        elif msg_type == "error":
                            output["stderr"].append(msg["content"])
                        elif msg_type == "status":
                            if msg["content"]["execution_state"] == "idle":
                                break
                except TimeoutError:
                    output["stderr"].append("Timeout during cell execution.")
                    break

            return output

        except IndexError:
            raise IndexError(f"Cell index {index} is out of range.")

    def stop_kernel(self):
        """Stops the current kernel and releases resources."""
        if self._kernel_manager:
            self._kernel_client.stop_channels()
            self._kernel_manager.shutdown_kernel()
            self._kernel_manager = None
            self._kernel_client = None
            self.kernel_id = None

    def save(self, filepath: str = None) -> None:
        """Saves the notebook to the specified file path.

         Args:
            filepath (str, optional): The file path to save the notebook to. If None, saves to the original file. Defaults to None.

        Raises:
            ValueError: If neither a file path is passed, or a file has not been specified upon initialization
         """

        if filepath is None and self.filepath is None:
            raise ValueError("No file specified for saving the notebook")

        save_path = filepath if filepath else self.filepath
        with open(save_path, "w", encoding="utf-8") as f:
            nbformat.write(self._notebook, f)
        if filepath:
            self.filepath = filepath

    def to_plain_text(self) -> str:
        """
        Converts the notebook content to a simplified plain text (.py ,.txt or .r file) representation.
         Each code and markdown cell is extracted into the string
         code cells are prefixed with '#CODE:'
         markdown cells are prefixed with '#MARKDOWN:'
        Returns:
            str: The plain text representation of the notebook.
        """
        text_parts = []
        for cell in self._notebook.cells:
            if cell.cell_type == "code":
                 text_parts.append(f"# %% [code]\n{textwrap.dedent(cell.source)}")
            elif cell.cell_type == "markdown":
                 text_parts.append(f"# %% [markdown]\n{textwrap.dedent(cell.source)}")
        return "\n".join(text_parts)

    @staticmethod
    def from_plain_text(text: str) -> "Notebook":
        """Converts text representation (.py,.txt or .r) into a notebook object

           Args:
               text: The plain text representation (.py,.txt or .r file) to be converted to a notebook
          Returns:
            Notebook: The plain text representation of the notebook.
          """
        notebook = Notebook()
        lines = text.splitlines()
        i = 0
        if not any(line.strip().startswith("# %% [") for line in lines):
            notebook.add_code_cell(text)
            return notebook
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("# %% [code]"):
                source = ""
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("# %% ["):
                    source += lines[i] + "\n"
                    i += 1
                notebook.add_code_cell(source.strip())
            elif line.startswith("# %% [markdown]"):
                source = ""
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("# %% ["):
                    source += lines[i] + "\n"
                    i += 1
                notebook.add_markdown_cell(source.strip())
            else:
                i += 1
                continue
        return notebook

    def __repr__(self):
        """Returns a string representation of the notebook object.
         Returns:
             str: A string representation of the notebook
         """
        if self.filepath:
            return f"Notebook(filepath='{self.filepath}')"
