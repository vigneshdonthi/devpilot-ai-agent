import ast
import os
import re
import sys

from langchain_core.tools import tool


def get_project_imports(project_path: str) -> set[str]:
    """Scan Python files and return imported top-level module names."""

    imports = set()

    ignored_folders = {
        "venv",
        ".venv",
        ".git",
        "__pycache__",
        "node_modules",
    }

    for root, directories, files in os.walk(project_path):

        # Prevent os.walk() from entering ignored folders
        directories[:] = [
            directory
            for directory in directories
            if directory not in ignored_folders
        ]

        for filename in files:

            if not filename.endswith(".py"):
                continue

            file_path = os.path.join(root, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    code = file.read()

                tree = ast.parse(code)

            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):

                # import requests
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_level = alias.name.split(".")[0]
                        imports.add(top_level)

                # from django.http import JsonResponse
                elif isinstance(node, ast.ImportFrom):

                    if node.module:
                        top_level = node.module.split(".")[0]
                        imports.add(top_level)

    return imports


def get_requirements(requirements_path: str):
    """Read requirements.txt and extract package information."""

    packages = set()
    unpinned = []
    duplicates = []

    seen = set()

    with open(requirements_path, "r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            match = re.match(
                r"^([A-Za-z0-9_.-]+)\s*(==|>=|<=|~=|>|<|!=)?\s*(.*)$",
                line,
            )

            if not match:
                continue

            package = match.group(1)
            operator = match.group(2)
            version = match.group(3).strip()

            normalized = package.lower().replace("_", "-")

            if normalized in seen:
                duplicates.append(package)
            else:
                seen.add(normalized)

            packages.add(normalized)

            if not operator or not version:
                unpinned.append(package)

    return packages, unpinned, duplicates


@tool
def check_project_dependencies(
    project_path: str,
    requirements_path: str
) -> str:
    """Analyze a Python project's imports and requirements.txt to find potentially missing, unpinned, and duplicate dependencies."""

    if not os.path.isdir(project_path):
        return f"Project directory not found: {project_path}"

    if not os.path.isfile(requirements_path):
        return f"Requirements file not found: {requirements_path}"

    try:
        project_imports = get_project_imports(project_path)

        requirements, unpinned, duplicates = get_requirements(
            requirements_path
        )

        # Python standard-library modules
        standard_library = set(sys.stdlib_module_names)

        third_party_imports = {
            module
            for module in project_imports
            if module not in standard_library
        }

        # Find local modules/packages so we don't report them as dependencies
        local_modules = set()

        for item in os.listdir(project_path):

            item_path = os.path.join(project_path, item)

            if item.endswith(".py"):
                local_modules.add(item[:-3])

            elif os.path.isdir(item_path):
                if os.path.isfile(os.path.join(item_path, "__init__.py")):
                    local_modules.add(item)

        third_party_imports -= local_modules

        # Some import names differ from PyPI package names.
        import_to_package = {
            "dotenv": "python-dotenv",
            "sklearn": "scikit-learn",
            "cv2": "opencv-python",
            "PIL": "pillow",
            "yaml": "pyyaml",
        }

        expected_packages = {
            import_to_package.get(module, module)
            .lower()
            .replace("_", "-")
            for module in third_party_imports
        }

        missing = expected_packages - requirements

        report = f"""
Dependency Health Report
------------------------

Project:
{project_path}

Third-party imports detected:
{chr(10).join("- " + item for item in sorted(expected_packages)) if expected_packages else "None"}

Dependencies in requirements.txt:
{chr(10).join("- " + item for item in sorted(requirements)) if requirements else "None"}

Potentially missing dependencies:
{chr(10).join("- " + item for item in sorted(missing)) if missing else "None"}

Unpinned dependencies:
{chr(10).join("- " + item for item in sorted(set(unpinned))) if unpinned else "None"}

Duplicate dependencies:
{chr(10).join("- " + item for item in sorted(set(duplicates))) if duplicates else "None"}
"""

        return report.strip()

    except Exception as e:
        return f"Dependency analysis failed: {str(e)}"