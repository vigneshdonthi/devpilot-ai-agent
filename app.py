import os
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path

import streamlit as st

from agent import agent, model


# =========================================================
# CONFIG
# =========================================================

MAX_ZIP_SIZE_MB = 50
MAX_EXTRACTED_SIZE_MB = 150
MAX_FILES = 2000

IGNORED_FOLDERS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
}


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DevPilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 3.5rem;
        padding-bottom: 6rem;
    }

    .devpilot-title {
        font-size: 2.4rem;
        font-weight: 750;
        line-height: 1.3;
        margin: 0;
        padding-top: 0.5rem;
    }

    .devpilot-subtitle {
        opacity: 0.65;
        margin-top: 0.3rem;
        margin-bottom: 1.5rem;
    }

    .welcome-box {
        padding: 25px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 16px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "chats" not in st.session_state:
    st.session_state.chats = {}


if "current_chat_id" not in st.session_state:

    chat_id = str(uuid.uuid4())

    st.session_state.current_chat_id = chat_id

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "mode": "Agent",
    }


if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


if "github_action" not in st.session_state:
    st.session_state.github_action = None


if "package_action" not in st.session_state:
    st.session_state.package_action = False


# Keep temporary uploaded projects alive during this session.
if "uploaded_projects" not in st.session_state:
    st.session_state.uploaded_projects = {}


# =========================================================
# CHAT FUNCTIONS
# =========================================================

def create_new_chat():

    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "mode": "Agent",
    }

    st.session_state.current_chat_id = chat_id

    st.session_state.pending_prompt = None
    st.session_state.github_action = None
    st.session_state.package_action = False


def get_current_chat():

    return st.session_state.chats[
        st.session_state.current_chat_id
    ]


def switch_chat(chat_id):

    st.session_state.current_chat_id = chat_id

    st.session_state.pending_prompt = None
    st.session_state.github_action = None
    st.session_state.package_action = False


def delete_chat(chat_id):

    if chat_id in st.session_state.chats:
        del st.session_state.chats[chat_id]

    # Remove temporary uploaded project belonging to this chat.
    project_data = st.session_state.uploaded_projects.pop(
        chat_id,
        None,
    )

    if project_data:

        temp_directory = project_data.get("temp_directory")

        if temp_directory and os.path.isdir(temp_directory):
            shutil.rmtree(
                temp_directory,
                ignore_errors=True,
            )

    if not st.session_state.chats:
        create_new_chat()

    else:
        st.session_state.current_chat_id = next(
            reversed(st.session_state.chats)
        )


def run_prompt(prompt):

    st.session_state.pending_prompt = prompt


# =========================================================
# ZIP FUNCTIONS
# =========================================================

def is_ignored_path(path_parts):

    return any(
        part in IGNORED_FOLDERS
        for part in path_parts
    )


def get_actual_project_root(extract_directory):

    """
    If the ZIP contains one root folder:

        project.zip
            my-project/
                app.py

    return my-project instead of the extraction directory.
    """

    items = [
        item
        for item in os.listdir(extract_directory)
        if item not in {"__MACOSX"}
    ]

    if len(items) == 1:

        possible_root = os.path.join(
            extract_directory,
            items[0],
        )

        if os.path.isdir(possible_root):
            return possible_root

    return extract_directory


def extract_uploaded_project(uploaded_file):

    """
    Safely extract an uploaded ZIP into a temporary directory.

    Returns:
        (project_path, temp_directory)
    """

    if uploaded_file is None:
        raise ValueError("No ZIP file was uploaded.")

    # -----------------------------------------------------
    # CHECK ZIP SIZE
    # -----------------------------------------------------

    uploaded_file.seek(0, os.SEEK_END)

    zip_size = uploaded_file.tell()

    uploaded_file.seek(0)

    max_zip_bytes = (
        MAX_ZIP_SIZE_MB
        * 1024
        * 1024
    )

    if zip_size > max_zip_bytes:

        raise ValueError(
            f"ZIP file is too large. "
            f"Maximum allowed size is "
            f"{MAX_ZIP_SIZE_MB} MB."
        )

    # -----------------------------------------------------
    # CREATE TEMP DIRECTORY
    # -----------------------------------------------------

    temp_directory = tempfile.mkdtemp(
        prefix="devpilot_"
    )

    extract_directory = os.path.join(
        temp_directory,
        "project",
    )

    os.makedirs(
        extract_directory,
        exist_ok=True,
    )

    extracted_size = 0
    extracted_files = 0

    max_extracted_bytes = (
        MAX_EXTRACTED_SIZE_MB
        * 1024
        * 1024
    )

    try:

        with zipfile.ZipFile(
            uploaded_file,
            "r",
        ) as zip_file:

            # ---------------------------------------------
            # VALIDATE ZIP
            # ---------------------------------------------

            for member in zip_file.infolist():

                member_path = Path(member.filename)

                # Reject absolute paths.
                if member_path.is_absolute():
                    raise ValueError(
                        "Unsafe ZIP file detected."
                    )

                # Reject ../ path traversal.
                if ".." in member_path.parts:
                    raise ValueError(
                        "Unsafe ZIP file detected."
                    )

                # Ignore unnecessary folders.
                if is_ignored_path(
                    member_path.parts
                ):
                    continue

                if member.is_dir():
                    continue

                extracted_files += 1

                if extracted_files > MAX_FILES:

                    raise ValueError(
                        "Repository contains too many files. "
                        f"Maximum allowed is {MAX_FILES}."
                    )

                extracted_size += member.file_size

                if (
                    extracted_size
                    > max_extracted_bytes
                ):

                    raise ValueError(
                        "Extracted project is too large. "
                        f"Maximum allowed size is "
                        f"{MAX_EXTRACTED_SIZE_MB} MB."
                    )

            # ---------------------------------------------
            # EXTRACT FILES MANUALLY
            # ---------------------------------------------

            for member in zip_file.infolist():

                member_path = Path(member.filename)

                if member_path.is_absolute():
                    continue

                if ".." in member_path.parts:
                    continue

                if is_ignored_path(
                    member_path.parts
                ):
                    continue

                destination = os.path.abspath(
                    os.path.join(
                        extract_directory,
                        member.filename,
                    )
                )

                extract_root = os.path.abspath(
                    extract_directory
                )

                # Extra path traversal protection.
                if os.path.commonpath(
                    [extract_root, destination]
                ) != extract_root:

                    raise ValueError(
                        "Unsafe ZIP path detected."
                    )

                if member.is_dir():

                    os.makedirs(
                        destination,
                        exist_ok=True,
                    )

                    continue

                os.makedirs(
                    os.path.dirname(destination),
                    exist_ok=True,
                )

                with zip_file.open(
                    member,
                    "r",
                ) as source:

                    with open(
                        destination,
                        "wb",
                    ) as target:

                        shutil.copyfileobj(
                            source,
                            target,
                        )

        project_path = get_actual_project_root(
            extract_directory
        )

        return (
            project_path,
            temp_directory,
        )

    except Exception:

        shutil.rmtree(
            temp_directory,
            ignore_errors=True,
        )

        raise


def save_uploaded_project(uploaded_file):

    """
    Extract the project and associate it with the
    current chat.
    """

    chat_id = st.session_state.current_chat_id

    # Remove previous uploaded project for this chat.
    old_project = (
        st.session_state.uploaded_projects.get(
            chat_id
        )
    )

    if old_project:

        old_temp_directory = old_project.get(
            "temp_directory"
        )

        if (
            old_temp_directory
            and os.path.isdir(old_temp_directory)
        ):

            shutil.rmtree(
                old_temp_directory,
                ignore_errors=True,
            )

    project_path, temp_directory = (
        extract_uploaded_project(
            uploaded_file
        )
    )

    st.session_state.uploaded_projects[
        chat_id
    ] = {
        "project_path": project_path,
        "temp_directory": temp_directory,
        "filename": uploaded_file.name,
    }

    return project_path


# =========================================================
# AUTOMATIC CHAT TITLE
# =========================================================

def generate_title(prompt):

    try:

        title_prompt = f"""
Create a short title for this conversation.

Rules:
- 2 to 5 words
- Be specific
- No quotation marks
- No punctuation at the end
- Return only the title

User message:
{prompt}
"""

        response = model.invoke(
            title_prompt
        )

        title = response.content.strip()

        title = title.replace('"', "")
        title = title.replace("'", "")

        if len(title) > 45:
            title = title[:45]

        return title

    except Exception:

        words = prompt.split()

        return (
            " ".join(words[:4])
            or "New Chat"
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚡ DevPilot")

    st.caption(
        "AI Developer Assistant"
    )


    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "＋ New Chat",
        use_container_width=True,
        type="primary",
    ):

        create_new_chat()

        st.rerun()


    st.divider()


    # -----------------------------------------------------
    # QUICK ACTIONS
    # -----------------------------------------------------

    st.markdown(
        "### ⚡ Quick Actions"
    )


    if st.button(
        "🐙 Explore GitHub",
        use_container_width=True,
    ):

        st.session_state.github_action = (
            "architecture"
        )

        st.session_state.package_action = False

        st.rerun()


    if st.button(
        "📖 Explain GitHub Code",
        use_container_width=True,
    ):

        st.session_state.github_action = "code"

        st.session_state.package_action = False

        st.rerun()


    if st.button(
        "🔍 Review Project",
        use_container_width=True,
    ):

        st.session_state.github_action = "review"

        st.session_state.package_action = False

        st.rerun()


    if st.button(
        "📦 Check Dependencies",
        use_container_width=True,
    ):

        st.session_state.github_action = (
            "dependencies"
        )

        st.session_state.package_action = False

        st.rerun()


    if st.button(
        "🔄 Check PyPI Package",
        use_container_width=True,
    ):

        st.session_state.package_action = True

        st.session_state.github_action = None

        st.rerun()


    st.divider()


    # -----------------------------------------------------
    # RECENT CHATS
    # -----------------------------------------------------

    st.markdown(
        "### 💬 Recent Chats"
    )


    chat_items = list(
        st.session_state.chats.items()
    )

    chat_items.reverse()


    for chat_id, saved_chat in chat_items:

        title = saved_chat["title"]

        if (
            chat_id
            == st.session_state.current_chat_id
        ):

            title = "● " + title


        col1, col2 = st.columns(
            [5, 1],
            gap="small",
        )


        with col1:

            if st.button(
                title,
                key=f"open_{chat_id}",
                use_container_width=True,
            ):

                switch_chat(chat_id)

                st.rerun()


        with col2:

            if st.button(
                "×",
                key=f"delete_{chat_id}",
                help="Delete chat",
            ):

                delete_chat(chat_id)

                st.rerun()


# =========================================================
# CURRENT CHAT
# =========================================================

chat = get_current_chat()

messages = chat["messages"]


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="devpilot-title">
        ⚡ DevPilot
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="devpilot-subtitle">
        Your AI developer assistant for code,
        projects, dependencies and GitHub.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MODE SELECTOR
# =========================================================

if not messages:

    mode = st.segmented_control(
        "Choose how you want to use DevPilot",
        options=[
            "⚡ Agent",
            "💬 Chat",
        ],
        default=(
            "⚡ Agent"
            if chat.get(
                "mode",
                "Agent"
            ) == "Agent"
            else "💬 Chat"
        ),
        selection_mode="single",
        key=(
            f"mode_"
            f"{st.session_state.current_chat_id}"
        ),
    )


    if mode == "⚡ Agent":
        chat["mode"] = "Agent"

    elif mode == "💬 Chat":
        chat["mode"] = "Chat"


# =========================================================
# MODE DESCRIPTION
# =========================================================

if not messages:

    if chat["mode"] == "Agent":

        st.caption(
            "⚡ **Agent Mode** — DevPilot can reason "
            "about your task and autonomously use "
            "developer tools."
        )

    else:

        st.caption(
            "💬 **Chat Mode** — Chat directly with "
            "DevPilot for programming, AI and "
            "general questions."
        )


# =========================================================
# WELCOME SCREEN
# =========================================================

if not messages:

    # =====================================================
    # AGENT MODE
    # =====================================================

    if chat["mode"] == "Agent":

        st.markdown(
            """
            <div class="welcome-box">

            <h3>What should DevPilot work on?</h3>

            Explore repositories, inspect source code,
            review Python projects and analyze dependencies.

            </div>
            """,
            unsafe_allow_html=True,
        )


        col1, col2 = st.columns(2)


        with col1:

            if st.button(
                "🐙 Explore GitHub Repository",
                use_container_width=True,
            ):

                st.session_state.github_action = (
                    "architecture"
                )

                st.session_state.package_action = False

                st.rerun()


            if st.button(
                "📦 Analyze Dependencies",
                use_container_width=True,
            ):

                st.session_state.github_action = (
                    "dependencies"
                )

                st.session_state.package_action = False

                st.rerun()


        with col2:

            if st.button(
                "🔍 Review Python Project",
                use_container_width=True,
            ):

                st.session_state.github_action = (
                    "review"
                )

                st.session_state.package_action = False

                st.rerun()


            if st.button(
                "📖 Explain GitHub Source Code",
                use_container_width=True,
            ):

                st.session_state.github_action = "code"

                st.session_state.package_action = False

                st.rerun()


    # =====================================================
    # CHAT MODE
    # =====================================================

    else:

        st.markdown(
            """
            <div class="welcome-box">

            <h3>Chat with DevPilot</h3>

            Ask DevPilot about programming, AI, Python,
            Django, LangChain, machine learning or
            anything else you want to understand.

            </div>
            """,
            unsafe_allow_html=True,
        )


        col1, col2 = st.columns(2)


        with col1:

            if st.button(
                "🧠 What is an AI Agent?",
                use_container_width=True,
            ):

                run_prompt(
                    "Explain what an AI agent is simply "
                    "with an example."
                )

                st.rerun()


            if st.button(
                "🐍 Teach me Python",
                use_container_width=True,
            ):

                run_prompt(
                    "Teach me an important intermediate "
                    "Python concept with a simple example."
                )

                st.rerun()


        with col2:

            if st.button(
                "🔗 What is LangChain?",
                use_container_width=True,
            ):

                run_prompt(
                    "Explain LangChain simply and why "
                    "developers use it."
                )

                st.rerun()


            if st.button(
                "🤖 LLM vs AI Agent",
                use_container_width=True,
            ):

                run_prompt(
                    "Explain the difference between an "
                    "LLM and an AI agent simply."
                )

                st.rerun()


# =========================================================
# DISPLAY EXISTING CHAT
# =========================================================

for message in messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# PROJECT / GITHUB QUICK ACTION
# =========================================================

if st.session_state.github_action:

    action = st.session_state.github_action


    # -----------------------------------------------------
    # EXPLORE GITHUB
    # -----------------------------------------------------

    if action == "architecture":

        st.markdown(
            "#### 🐙 Explore GitHub Repository"
        )

        st.caption(
            "Enter a public GitHub repository and "
            "DevPilot will explore its structure."
        )


        with st.form(
            "github_architecture_form",
            clear_on_submit=True,
        ):

            repository_url = st.text_input(
                "GitHub repository URL",
                placeholder=(
                    "https://github.com/pallets/flask"
                ),
            )


            col1, col2 = st.columns(2)


            with col1:

                submit = st.form_submit_button(
                    "Analyze Repository",
                    type="primary",
                    use_container_width=True,
                )


            with col2:

                cancel = st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )


            if cancel:

                st.session_state.github_action = None

                st.rerun()


            if submit:

                repository_url = (
                    repository_url.strip()
                )


                if not repository_url:

                    st.warning(
                        "Enter a GitHub repository URL."
                    )


                elif not repository_url.startswith(
                    (
                        "https://github.com/",
                        "http://github.com/",
                    )
                ):

                    st.warning(
                        "Enter a valid GitHub repository URL."
                    )


                else:

                    run_prompt(
                        "Explore this GitHub repository. "
                        "Use the GitHub repository tools to "
                        "inspect its actual repository tree. "
                        "Identify important files and "
                        "directories and explain the project "
                        "architecture. Do not invent files: "
                        f"{repository_url}"
                    )

                    st.session_state.github_action = None

                    st.rerun()


    # -----------------------------------------------------
    # EXPLAIN GITHUB CODE
    # -----------------------------------------------------

    elif action == "code":

        st.markdown(
            "#### 📖 Explain GitHub Source Code"
        )

        st.caption(
            "Enter a public GitHub repository and "
            "DevPilot will inspect and explain its "
            "implementation."
        )


        with st.form(
            "github_code_form",
            clear_on_submit=True,
        ):

            repository_url = st.text_input(
                "GitHub repository URL",
                placeholder=(
                    "https://github.com/pallets/flask"
                ),
            )


            col1, col2 = st.columns(2)


            with col1:

                submit = st.form_submit_button(
                    "Explain Code",
                    type="primary",
                    use_container_width=True,
                )


            with col2:

                cancel = st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )


            if cancel:

                st.session_state.github_action = None

                st.rerun()


            if submit:

                repository_url = (
                    repository_url.strip()
                )


                if not repository_url:

                    st.warning(
                        "Enter a GitHub repository URL."
                    )


                elif not repository_url.startswith(
                    (
                        "https://github.com/",
                        "http://github.com/",
                    )
                ):

                    st.warning(
                        "Enter a valid GitHub repository URL."
                    )


                else:

                    run_prompt(
                        "Explore this GitHub repository "
                        "using GitHub tools. Inspect the "
                        "repository tree, identify the main "
                        "implementation files, read the "
                        "actual source code and explain how "
                        "the project works. Do not guess "
                        "uninspected files: "
                        f"{repository_url}"
                    )

                    st.session_state.github_action = None

                    st.rerun()


    # -----------------------------------------------------
    # REVIEW PROJECT / DEPENDENCIES
    # -----------------------------------------------------

    elif action in {
        "review",
        "dependencies",
    }:

        if action == "review":

            st.markdown(
                "#### 🔍 Review Project"
            )

            st.caption(
                "Review a GitHub repository or upload "
                "a local/private repository as a ZIP."
            )

        else:

            st.markdown(
                "#### 📦 Check Dependencies"
            )

            st.caption(
                "Check dependencies from a GitHub "
                "repository or an uploaded ZIP project."
            )


        # -------------------------------------------------
        # PROJECT SOURCE
        # -------------------------------------------------

        source = st.segmented_control(
            "Project source",
            options=[
                "🐙 GitHub Repository",
                "📁 Upload Repository",
            ],
            default="🐙 GitHub Repository",
            selection_mode="single",
            key=f"project_source_{action}",
        )


        # =================================================
        # GITHUB SOURCE
        # =================================================

        if source == "🐙 GitHub Repository":

            with st.form(
                f"github_{action}_form",
                clear_on_submit=True,
            ):

                repository_url = st.text_input(
                    "GitHub repository URL",
                    placeholder=(
                        "https://github.com/user/project"
                    ),
                )


                col1, col2 = st.columns(2)


                with col1:

                    submit = (
                        st.form_submit_button(
                            (
                                "Review Project"
                                if action == "review"
                                else "Check Dependencies"
                            ),
                            type="primary",
                            use_container_width=True,
                        )
                    )


                with col2:

                    cancel = (
                        st.form_submit_button(
                            "Cancel",
                            use_container_width=True,
                        )
                    )


                if cancel:

                    st.session_state.github_action = None

                    st.rerun()


                if submit:

                    repository_url = (
                        repository_url.strip()
                    )


                    if not repository_url:

                        st.warning(
                            "Enter a GitHub repository URL."
                        )


                    elif not repository_url.startswith(
                        (
                            "https://github.com/",
                            "http://github.com/",
                        )
                    ):

                        st.warning(
                            "Enter a valid GitHub repository URL."
                        )


                    else:

                        if action == "review":

                            run_prompt(
                                "Review this GitHub repository. "
                                "This is a GitHub repository, so "
                                "use only the GitHub repository "
                                "tools for repository inspection. "
                                "First inspect the repository "
                                "tree, then read important source "
                                "and configuration files. Identify "
                                "confirmed issues, potential "
                                "issues and practical "
                                "recommendations. Base findings "
                                "only on files you actually "
                                "inspect: "
                                f"{repository_url}"
                            )


                        else:

                            run_prompt(
                                "Analyze the dependencies of this "
                                "GitHub repository. This is a "
                                "GitHub repository, so use GitHub "
                                "tools rather than local "
                                "filesystem tools. Inspect the "
                                "repository tree and locate actual "
                                "dependency files such as "
                                "requirements.txt, pyproject.toml, "
                                "Pipfile, poetry.lock, setup.py, "
                                "setup.cfg or package.json. Read "
                                "only files that actually exist "
                                "and report dependency issues "
                                "based on their contents: "
                                f"{repository_url}"
                            )


                        st.session_state.github_action = None

                        st.rerun()


        # =================================================
        # ZIP UPLOAD SOURCE
        # =================================================

        elif source == "📁 Upload Repository":

            st.info(
                "Upload your project as a `.zip` file. "
                "Folders such as `.git`, `venv`, `.venv`, "
                "`node_modules` and `__pycache__` are ignored."
            )


            uploaded_file = st.file_uploader(
                "Upload project ZIP",
                type=["zip"],
                key=f"project_zip_{action}",
                help=(
                    f"Maximum ZIP size: "
                    f"{MAX_ZIP_SIZE_MB} MB"
                ),
            )


            col1, col2 = st.columns(2)


            with col1:

                analyze_uploaded = st.button(
                    (
                        "Review Uploaded Project"
                        if action == "review"
                        else "Check Uploaded Dependencies"
                    ),
                    type="primary",
                    use_container_width=True,
                    key=f"analyze_upload_{action}",
                )


            with col2:

                cancel_upload = st.button(
                    "Cancel",
                    use_container_width=True,
                    key=f"cancel_upload_{action}",
                )


            if cancel_upload:

                st.session_state.github_action = None

                st.rerun()


            if analyze_uploaded:

                if uploaded_file is None:

                    st.warning(
                        "Upload a project ZIP first."
                    )


                else:

                    try:

                        with st.spinner(
                            "Preparing project..."
                        ):

                            project_path = (
                                save_uploaded_project(
                                    uploaded_file
                                )
                            )


                        if action == "review":

                            run_prompt(
                                "Review the uploaded project "
                                "located at this local filesystem "
                                "directory:\n\n"
                                f"{project_path}\n\n"
                                "This is an extracted uploaded "
                                "project, NOT a GitHub repository. "
                                "Use the local project tools. "
                                "Start with "
                                "analyze_project_structure using "
                                "the exact directory above. Then "
                                "inspect relevant source files "
                                "using read_file and "
                                "analyze_python_code when useful. "
                                "If requirements.txt exists, "
                                "analyze dependencies using "
                                "check_project_dependencies. "
                                "Report confirmed issues, "
                                "potential issues and practical "
                                "recommendations. Do not inspect "
                                "files outside this project "
                                "directory."
                            )


                        else:

                            requirements_path = os.path.join(
                                project_path,
                                "requirements.txt",
                            )

                            run_prompt(
                                "Analyze dependencies for the "
                                "uploaded project located at this "
                                "local filesystem directory:\n\n"
                                f"{project_path}\n\n"
                                "This is an extracted uploaded "
                                "project, NOT a GitHub repository. "
                                "Use local project tools. Start "
                                "with analyze_project_structure. "
                                "If requirements.txt exists, use "
                                "check_project_dependencies with "
                                "these paths:\n\n"
                                f"project_path = {project_path}\n"
                                f"requirements_path = "
                                f"{requirements_path}\n\n"
                                "Do not assume requirements.txt "
                                "exists. If the project uses a "
                                "different dependency format, "
                                "inspect that file and clearly "
                                "explain the current tool "
                                "limitation."
                            )


                        st.session_state.github_action = None

                        st.rerun()


                    except zipfile.BadZipFile:

                        st.error(
                            "The uploaded file is not a "
                            "valid ZIP archive."
                        )


                    except ValueError as e:

                        st.error(
                            str(e)
                        )


                    except Exception as e:

                        st.error(
                            "Could not prepare the project: "
                            f"{str(e)}"
                        )


# =========================================================
# PYPI QUICK ACTION
# =========================================================

if st.session_state.package_action:

    st.markdown(
        "#### 🔄 Check PyPI Package"
    )

    st.caption(
        "Enter a Python package and DevPilot will "
        "check its latest PyPI information."
    )


    with st.form(
        "package_form",
        clear_on_submit=True,
    ):

        package_name = st.text_input(
            "Python package",
            placeholder="langchain",
        )


        col1, col2 = st.columns(2)


        with col1:

            check_package = (
                st.form_submit_button(
                    "Check Package",
                    type="primary",
                    use_container_width=True,
                )
            )


        with col2:

            cancel_package = (
                st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )
            )


        if cancel_package:

            st.session_state.package_action = False

            st.rerun()


        if check_package:

            package_name = (
                package_name.strip()
            )


            if not package_name:

                st.warning(
                    "Enter a Python package name."
                )


            else:

                run_prompt(
                    "Check the latest PyPI version of "
                    f"{package_name} and explain whether "
                    "my installed version should be "
                    "updated."
                )


                st.session_state.package_action = False

                st.rerun()


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Message DevPilot..."
)


# =========================================================
# HANDLE QUICK PROMPTS
# =========================================================

if st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None


# =========================================================
# PROCESS MESSAGE
# =========================================================

if prompt:

    prompt = prompt.strip()


    if prompt:

        # =================================================
        # AUTOMATIC TITLE
        # =================================================

        if chat["title"] == "New Chat":

            chat["title"] = generate_title(
                prompt
            )


        # =================================================
        # SAVE USER MESSAGE
        # =================================================

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )


        # =================================================
        # DISPLAY USER MESSAGE
        # =================================================

        with st.chat_message("user"):

            st.markdown(prompt)


        # =================================================
        # DEVPILOT RESPONSE
        # =================================================

        with st.chat_message("assistant"):

            final_response = ""


            # =================================================
            # AGENT MODE
            # =================================================

            if chat["mode"] == "Agent":

                config = {
                    "configurable": {
                        "thread_id":
                            st.session_state.current_chat_id
                    }
                }


                status = st.status(
                    "DevPilot is thinking...",
                    expanded=True,
                )


                response_placeholder = st.empty()

                tools_seen = set()


                try:

                    stream = agent.stream(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt,
                                }
                            ]
                        },
                        config=config,
                        stream_mode=[
                            "updates",
                            "messages",
                        ],
                    )


                    for stream_mode, data in stream:

                        # =====================================
                        # TOOL ACTIVITY
                        # =====================================

                        if stream_mode == "updates":

                            if not isinstance(
                                data,
                                dict
                            ):
                                continue


                            for node_name, update in data.items():

                                if not isinstance(
                                    update,
                                    dict
                                ):
                                    continue


                                update_messages = (
                                    update.get(
                                        "messages",
                                        []
                                    )
                                )


                                for update_message in update_messages:

                                    tool_calls = getattr(
                                        update_message,
                                        "tool_calls",
                                        None,
                                    )


                                    if tool_calls:

                                        for tool_call in tool_calls:

                                            tool_name = (
                                                tool_call.get(
                                                    "name",
                                                    "tool",
                                                )
                                            )


                                            tool_args = (
                                                tool_call.get(
                                                    "args",
                                                    {},
                                                )
                                            )


                                            signature = (
                                                tool_name,
                                                str(tool_args),
                                            )


                                            if signature not in tools_seen:

                                                tools_seen.add(
                                                    signature
                                                )


                                                status.write(
                                                    f"🔧 **{tool_name}**"
                                                )


                                                if tool_args:

                                                    status.caption(
                                                        str(
                                                            tool_args
                                                        )
                                                    )


                        # =====================================
                        # STREAM RESPONSE
                        # =====================================

                        elif stream_mode == "messages":

                            if not isinstance(
                                data,
                                tuple
                            ):
                                continue


                            message_chunk, metadata = data


                            if (
                                metadata.get(
                                    "langgraph_node"
                                )
                                == "tools"
                            ):
                                continue


                            content = getattr(
                                message_chunk,
                                "content",
                                "",
                            )


                            if (
                                isinstance(content, str)
                                and content
                            ):

                                final_response += content


                                response_placeholder.markdown(
                                    final_response + "▌"
                                )


                    # =========================================
                    # FALLBACK
                    # =========================================

                    if not final_response:

                        state = agent.get_state(
                            config
                        )


                        state_messages = (
                            state.values.get(
                                "messages",
                                []
                            )
                        )


                        if state_messages:

                            final_response = (
                                state_messages[-1].content
                            )


                    response_placeholder.markdown(
                        final_response
                    )


                    # =========================================
                    # COMPLETE STATUS
                    # =========================================

                    if tools_seen:

                        tool_count = len(
                            tools_seen
                        )


                        status.update(
                            label=(
                                f"Completed · "
                                f"{tool_count} tool"
                                f"{'s' if tool_count != 1 else ''} used"
                            ),
                            state="complete",
                            expanded=False,
                        )


                    else:

                        status.update(
                            label="Completed",
                            state="complete",
                            expanded=False,
                        )


                except Exception as e:

                    final_response = (
                        "DevPilot encountered an error:"
                        "\n\n"
                        f"`{str(e)}`"
                    )


                    response_placeholder.markdown(
                        final_response
                    )


                    status.update(
                        label="Something went wrong",
                        state="error",
                        expanded=True,
                    )


            # =================================================
            # CHAT MODE
            # =================================================

            else:

                response_placeholder = st.empty()


                try:

                    chat_messages = []


                    for message in messages:

                        chat_messages.append(
                            {
                                "role":
                                    message["role"],

                                "content":
                                    message["content"],
                            }
                        )


                    for chunk in model.stream(
                        chat_messages
                    ):

                        content = chunk.content


                        if (
                            isinstance(content, str)
                            and content
                        ):

                            final_response += content


                            response_placeholder.markdown(
                                final_response + "▌"
                            )


                    response_placeholder.markdown(
                        final_response
                    )


                except Exception as e:

                    final_response = (
                        "DevPilot encountered an error:"
                        "\n\n"
                        f"`{str(e)}`"
                    )


                    response_placeholder.markdown(
                        final_response
                    )


        # =================================================
        # SAVE RESPONSE
        # =================================================

        messages.append(
            {
                "role": "assistant",
                "content": final_response,
            }
        )


        # =================================================
        # RERUN
        # =================================================

        st.rerun()