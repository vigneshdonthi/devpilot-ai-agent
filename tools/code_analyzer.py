import ast
import os

from langchain_core.tools import tool


@tool
def analyze_python_code(file_path: str) -> str:
    """Analyze a Python file for syntax, functions, classes, imports, and basic code-quality issues."""

    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    if not file_path.endswith(".py"):
        return "Only Python (.py) files are supported."

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

        tree = ast.parse(code)

    except SyntaxError as e:
        return (
            f"Syntax error in {file_path}\n"
            f"Line: {e.lineno}\n"
            f"Message: {e.msg}"
        )

    except Exception as e:
        return f"Error analyzing file: {str(e)}"

    functions = []
    classes = []
    imports = []
    issues = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

            # Check function length
            if hasattr(node, "end_lineno"):
                length = node.end_lineno - node.lineno + 1

                if length > 50:
                    issues.append(
                        f"Function '{node.name}' is long ({length} lines)."
                    )

            # Check missing docstring
            if ast.get_docstring(node) is None:
                issues.append(
                    f"Function '{node.name}' has no docstring."
                )

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

            if ast.get_docstring(node) is None:
                issues.append(
                    f"Class '{node.name}' has no docstring."
                )

        elif isinstance(node, ast.Import):

            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            imports.append(module)

        elif isinstance(node, ast.ExceptHandler):

            # Detect: except: pass
            if (
                len(node.body) == 1
                and isinstance(node.body[0], ast.Pass)
            ):
                issues.append(
                    f"Empty exception handler near line {node.lineno}."
                )

    line_count = len(code.splitlines())

    if not issues:
        issues.append("No basic code-quality issues detected.")

    report = f"""
Python Code Analysis
--------------------
File: {file_path}
Lines: {line_count}

Functions:
{", ".join(functions) if functions else "None"}

Classes:
{", ".join(classes) if classes else "None"}

Imports:
{", ".join(imports) if imports else "None"}

Potential Issues:
{chr(10).join("- " + issue for issue in issues)}
"""

    return report.strip()