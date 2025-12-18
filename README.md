# NotebookLLM MCP Server
![PyPI](https://img.shields.io/pypi/v/notebookllm-mcp?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/notebookllm)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/notebookllm-mcp?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/notebookllm-mcp)
A Model Context Protocol server for working with Jupyter Notebooks (`.ipynb` files) in a way that is efficient for Large Language Models (LLMs). It converts notebooks to a simplified plain text format to reduce token usage and cost, and can convert them back.

## Available Tools

*   **`load_notebook`**: Loads a `.ipynb` file into memory.
    *   **Arguments**:
        *   `filepath` (string): The absolute path to the `.ipynb` file.
    *   **Returns**: (string) Success or failure message, including cell count.
*   **`notebook_to_plain_text`**: Converts a `.ipynb` file (loaded or from path) to a simplified plain text representation.
    *   **Arguments**:
        *   `input_filepath` (string, optional): Absolute path to the `.ipynb` file for on-the-fly conversion.
    *   **Returns**: (string) Plain text representation or error message.
*   **`plain_text_to_notebook_file`**: Converts plain text content back to a `.ipynb` file and saves it.
    *   **Arguments**:
        *   `plain_text_content` (string): Plain text content to convert.
        *   `output_filepath` (string): Absolute path to save the `.ipynb` file (must end with `.ipynb`).
    *   **Returns**: (string) Success or failure message.
*   **`add_code_cell_to_loaded_notebook`**: Adds a new code cell to the currently loaded notebook.
    *   **Arguments**:
        *   `code_content` (string): Source code for the new cell.
        *   `position` (integer, optional): Position to insert the cell (appends if `null`).
    *   **Returns**: (string) Success or failure message and current cell count.
*   **`add_markdown_cell_to_loaded_notebook`**: Adds a new markdown cell to the currently loaded notebook.
    *   **Arguments**:
        *   `markdown_content` (string): Markdown content for the new cell.
        *   `position` (integer, optional): Position to insert the cell (appends if `null`).
    *   **Returns**: (string) Success or failure message and current cell count.
*   **`save_loaded_notebook`**: Saves the currently loaded notebook to a file.
    *   **Arguments**:
        *   `output_filepath` (string, optional): Absolute path to save the `.ipynb` file (must end with `.ipynb`). Saves to original path if `null`.
    *   **Returns**: (string) Success or failure message.

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/), no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run `notebookllm_mcp`.

### Using PIP

Alternatively, you can install `notebookllm_mcp` via pip:

```bash
pip install notebookllm-mcp
```

After installation, you can run it as a script using:

```bash
python -m notebookllm_mcp
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

**Using uvx**
```json
{
  "mcpServers": {
    "notebookllm": {
      "command": "uvx",
      "args": ["notebookllm_mcp"]
    }
  }
}
```

**Using pip installation**
```json
{
  "mcpServers": {
    "notebookllm": {
      "command": "python",
      "args": ["-m", "notebookllm_mcp"]
    }
  }
}
```

### Configure for Zed

Add to your Zed `settings.json`:

**Using uvx**
```json
"context_servers": [
  "notebookllm": {
    "command": "uvx",
    "args": ["notebookllm_mcp"]
  }
],
```

**Using pip installation**
```json
"context_servers": {
  "notebookllm": {
    "command": "python",
    "args": ["-m", "notebookllm_mcp"]
  }
},
```

### Configure for VS Code

For quick installation, use one of the one-click install buttons below...

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=notebookllm&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22notebookllm_mcp%22%5D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=notebookllm&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22notebookllm_mcp%22%5D%7D&quality=insiders)

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS) and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.
> Note that the `mcp` key is needed when using the `mcp.json` file.

**Using uvx**
```json
{
  "mcp": {
    "servers": {
      "notebookllm": {
        "command": "uvx",
        "args": ["notebookllm_mcp"]
      }
    }
  }
}
```

**Using pip installation**
```json
{
  "mcp": {
    "servers": {
      "notebookllm": {
        "command": "python",
        "args": ["-m", "notebookllm_mcp"]
      }
    }
  }
}
```

## Example Interactions

1.  **Load a notebook:**
    ```json
    {
      "name": "load_notebook",
      "arguments": {
        "filepath": "/path/to/your/notebook.ipynb"
      }
    }
    ```
    **Response:**
    ```json
    {
      "message": "Notebook /path/to/your/notebook.ipynb loaded successfully. Cell count: 10"
    }
    ```

2.  **Convert loaded notebook to plain text:**
    ```json
    {
      "name": "notebook_to_plain_text",
      "arguments": {}
    }
    ```
    **Response:**
    ```text
    # CELL 1 CODE
    print("Hello World")

    # CELL 2 MARKDOWN
    This is a markdown cell.
    ...
    ```

3.  **Convert plain text back to a notebook file:**
    ```json
    {
      "name": "plain_text_to_notebook_file",
      "arguments": {
        "plain_text_content": "# CELL 1 CODE\nprint(\"Hello Again\")\n\n# CELL 2 MARKDOWN\nAnother markdown cell.",
        "output_filepath": "/path/to/your/new_notebook.ipynb"
      }
    }
    ```
    **Response:**
    ```json
    {
      "message": "Notebook saved to /path/to/your/new_notebook.ipynb"
    }
    ```

## Debugging

You can use the MCP inspector to debug the server. For `uvx` installations:

```bash
npx @modelcontextprotocol/inspector uvx notebookllm_mcp
```

Or if you've installed the package via pip:
```bash
npx @modelcontextprotocol/inspector python -m notebookllm_mcp
```

## Build

This package is typically installed via pip or used directly with `uvx`. If you are developing the package, you can build it using standard Python build tools.

```bash
python -m build
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests for bug fixes, new features, or improvements to documentation.

## License

This project is licensed under the MIT License.
