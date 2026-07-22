from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI

from tools.file_reader import read_file
from tools.project_analyzer import analyze_project_structure
from tools.code_analyzer import analyze_python_code
from tools.dependency_checker import check_project_dependencies
#from tools.github_tool import get_github_repo_info
from tools.github_tool import (
    get_github_repo_info,
    get_github_repo_tree,
    read_github_file,
)#here internally we have three tools
from tools.package_checker import check_package_version
from langgraph.checkpoint.memory import InMemorySaver

# Load environment variables from .env
load_dotenv()

SYSTEM_PROMPT = """
You are DevPilot, an autonomous software engineering analysis agent.

Your job is to analyze Python projects, source code, dependencies,
GitHub repositories, and Python packages using the tools available to you.

Rules:

1. Use tools whenever the user's request requires information about
   files, projects, repositories, dependencies, or package versions.

2. Base technical findings on tool results.
   Do not invent problems that were not detected by the tools.

3. Clearly distinguish between:
   - Confirmed issues
   - Potential issues
   - Recommendations

4. Do not claim that an import is unused unless a tool explicitly
   reports it as unused.

5. Do not claim that error handling is missing unless the analysis
   explicitly supports that conclusion.

6. When analyzing a project, inspect the project structure first when
   necessary before deciding which files or tools to use.

7. Do not analyze generated or dependency directories such as:
   venv, .venv, .git, __pycache__, or node_modules.

8. When dependency versions need current information, use the package
   version tool rather than relying on your internal knowledge.

9. Prioritize confirmed problems by severity:
   CRITICAL, HIGH, MEDIUM, or LOW.

10. Keep the final report concise and actionable.
"""
# Create the LLM
model = ChatMistralAI(
    model="mistral-small-latest"
)


# Tools available to DevPilot

tools = [
    read_file,
    analyze_project_structure,
    analyze_python_code,
    check_project_dependencies,
    get_github_repo_info,
    get_github_repo_tree,
    read_github_file,
    check_package_version,
]

memory = InMemorySaver()
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=memory,
)


