import requests

from langchain_core.tools import tool


@tool
def check_package_version(package_name: str) -> str:
    """Get the latest available version and basic information for a Python package from PyPI."""

    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 404:
            return f"Package not found on PyPI: {package_name}"

        if response.status_code != 200:
            return (
                "PyPI request failed with status "
                f"{response.status_code}"
            )

        data = response.json()

        info = data.get("info", {})

        name = info.get("name")
        version = info.get("version")
        summary = info.get("summary")
        python_requirement = info.get("requires_python")

        report = f"""
PyPI Package Information
------------------------

Package:
{name}

Latest Version:
{version}

Description:
{summary or "No description available"}

Required Python Version:
{python_requirement or "Not specified"}
"""

        return report.strip()

    except requests.RequestException as e:
        return f"PyPI connection error: {str(e)}"

    except Exception as e:
        return f"Package lookup failed: {str(e)}"