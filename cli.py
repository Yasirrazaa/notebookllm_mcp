
import argparse
from notebookllm import Notebook
import sys

def main():
    """
    Entry point for the notebookllm command-line tool.

    Parses command-line arguments and performs the appropriate action
    based on the provided command.
    """
    parser = argparse.ArgumentParser(
        description="Convert between .ipynb, .py, and plain text formats for LLMs"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Convert .ipynb to plain text
    to_text_parser = subparsers.add_parser(
        "to_text", help="Convert .ipynb to a simplified plain text format"
    )
    to_text_parser.add_argument("ipynb_file", help="Path to the .ipynb file")
    to_text_parser.add_argument(
        "--output", "-o", help="Path to save the plain text output", default=None
    )

 # Convert .py to .ipynb
    py_to_ipynb_parser = subparsers.add_parser(
        "to_ipynb", help="Convert .py,.txt or .r file to a .ipynb format"
    )
    py_to_ipynb_parser.add_argument("py_file", help="Path to the .py,.txt or .r file")
    py_to_ipynb_parser.add_argument(
        "--output", "-o", help="Path to save the .ipynb output", default=None
    )

    args = parser.parse_args()

    if args.command == "to_text":
         try:
            notebook = Notebook(args.ipynb_file)
            plain_text = notebook.to_plain_text()
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                  f.write(plain_text)
                print(f"Saved to {args.output}")
            else:
                print(plain_text)

         except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "to_ipynb":
        try:
            with open(args.py_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            notebook = Notebook.from_plain_text(file_content)
            if args.output:
               notebook.save(args.output)
               print(f"Saved to {args.output}")
            else:
               notebook.save("output.ipynb")
               print("Saved to output.ipynb")

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
