import os
from langchain_core.tools import tool


@tool
def analyze_project_structure(directory_path: str) -> str:
    """Analyze a project's directory structure and return its files and folders."""

    if not os.path.exists(directory_path):
        return f"Directory not found: {directory_path}"

    if not os.path.isdir(directory_path):
        return f"Not a directory: {directory_path}"

    structure = []

    try:
        for root, directories, files in os.walk(directory_path):

            # Ignore unnecessary folders
            directories[:] = [
                directory
                for directory in directories
                if directory not in {
                    "venv",
                    ".venv",
                    ".git",
                    "__pycache__",
                    "node_modules"
                }
            ]

            level = root.replace(directory_path, "").count(os.sep)

            indent = "    " * level

            folder_name = os.path.basename(root)

            structure.append(f"{indent}{folder_name}/")

            file_indent = "    " * (level + 1)

            for file in files:
                structure.append(f"{file_indent}{file}")

        return "\n".join(structure)

    except Exception as e:
        return f"Error analyzing project: {str(e)}"