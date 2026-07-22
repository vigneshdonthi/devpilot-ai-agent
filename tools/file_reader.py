from langchain_core.tools import tool


@tool
def read_file(file_path: str) -> str:
    """Read the contents of a text or source code file."""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    except FileNotFoundError:
        return f"File not found: {file_path}"

    except Exception as e:
        return f"Error reading file: {str(e)}"