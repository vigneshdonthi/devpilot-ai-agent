import uuid

import streamlit as st

from agent import agent, model


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


    if not st.session_state.chats:

        create_new_chat()

    else:

        st.session_state.current_chat_id = next(
            reversed(st.session_state.chats)
        )


def run_prompt(prompt):

    st.session_state.pending_prompt = prompt


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

        response = model.invoke(title_prompt)

        title = response.content.strip()

        title = title.replace('"', "")
        title = title.replace("'", "")

        if len(title) > 45:
            title = title[:45]

        return title

    except Exception:

        words = prompt.split()

        return " ".join(words[:4]) or "New Chat"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚡ DevPilot")

    st.caption("AI Developer Assistant")


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

    st.markdown("### ⚡ Quick Actions")


    if st.button(
        "🐙 Explore GitHub",
        use_container_width=True,
    ):

        st.session_state.github_action = "architecture"

        st.session_state.package_action = False


    if st.button(
        "📖 Explain GitHub Code",
        use_container_width=True,
    ):

        st.session_state.github_action = "code"

        st.session_state.package_action = False


    if st.button(
        "🔍 Review Project",
        use_container_width=True,
    ):

        run_prompt(
            "Analyze my current Python project. "
            "Inspect its structure, source code and "
            "dependencies. Give me the most important "
            "problems and recommendations."
        )


    if st.button(
        "📦 Check Dependencies",
        use_container_width=True,
    ):

        run_prompt(
            "Analyze my current project's requirements.txt "
            "and identify missing, duplicate, unpinned or "
            "problematic dependencies."
        )


    if st.button(
        "🔄 Check PyPI Package",
        use_container_width=True,
    ):

        st.session_state.package_action = True

        st.session_state.github_action = None


    st.divider()


    # -----------------------------------------------------
    # RECENT CHATS
    # -----------------------------------------------------

    st.markdown("### 💬 Recent Chats")


    chat_items = list(
        st.session_state.chats.items()
    )

    chat_items.reverse()


    for chat_id, saved_chat in chat_items:

        title = saved_chat["title"]


        if chat_id == st.session_state.current_chat_id:

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

# Mode can only be selected before the conversation starts.

if not messages:

    mode = st.segmented_control(
        "Choose how you want to use DevPilot",
        options=[
            "⚡ Agent",
            "💬 Chat",
        ],
        default=(
            "⚡ Agent"
            if chat.get("mode", "Agent") == "Agent"
            else "💬 Chat"
        ),
        selection_mode="single",
        key=f"mode_{st.session_state.current_chat_id}",
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
            "⚡ **Agent Mode** — DevPilot can reason about "
            "your task and autonomously use developer tools."
        )


    else:

        st.caption(
            "💬 **Chat Mode** — Chat directly with DevPilot "
            "for programming, AI and general questions."
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

                st.session_state.github_action = "architecture"


            if st.button(
                "📦 Analyze Dependencies",
                use_container_width=True,
            ):

                run_prompt(
                    "Analyze my current project's "
                    "dependencies and identify potential "
                    "problems."
                )


        with col2:

            if st.button(
                "🔍 Review Python Project",
                use_container_width=True,
            ):

                run_prompt(
                    "Analyze my current Python project "
                    "and give me a code quality report."
                )


            if st.button(
                "📖 Explain GitHub Source Code",
                use_container_width=True,
            ):

                st.session_state.github_action = "code"


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


            if st.button(
                "🐍 Teach me Python",
                use_container_width=True,
            ):

                run_prompt(
                    "Teach me an important intermediate "
                    "Python concept with a simple example."
                )


        with col2:

            if st.button(
                "🔗 What is LangChain?",
                use_container_width=True,
            ):

                run_prompt(
                    "Explain LangChain simply and why "
                    "developers use it."
                )


            if st.button(
                "🤖 LLM vs AI Agent",
                use_container_width=True,
            ):

                run_prompt(
                    "Explain the difference between an "
                    "LLM and an AI agent simply."
                )


# =========================================================
# GITHUB QUICK ACTION FORM
# =========================================================

if st.session_state.github_action:

    action = st.session_state.github_action


    with st.form(
        "github_form"
    ):

        repository_url = st.text_input(
            "GitHub repository URL",
            placeholder=(
                "https://github.com/pallets/flask"
            ),
        )


        analyze_repo = st.form_submit_button(
            "Analyze Repository",
            type="primary",
        )


        if analyze_repo:

            repository_url = repository_url.strip()


            if repository_url:

                if action == "architecture":

                    run_prompt(
                        "Explore this GitHub repository, "
                        "identify the important files and "
                        "explain its architecture: "
                        f"{repository_url}"
                    )


                elif action == "code":

                    run_prompt(
                        "Explore this GitHub repository, "
                        "find the main application "
                        "implementation file, read it and "
                        "explain how it works: "
                        f"{repository_url}"
                    )


                st.session_state.github_action = None


            else:

                st.warning(
                    "Enter a GitHub repository URL."
                )


# =========================================================
# PYPI QUICK ACTION FORM
# =========================================================

if st.session_state.package_action:

    with st.form(
        "package_form"
    ):

        package_name = st.text_input(
            "Python package",
            placeholder="langchain",
        )


        check_package = st.form_submit_button(
            "Check Package",
            type="primary",
        )


        if check_package:

            package_name = package_name.strip()


            if package_name:

                run_prompt(
                    "Check the latest PyPI version of "
                    f"{package_name} and explain whether "
                    "my installed version should be updated."
                )


                st.session_state.package_action = False


            else:

                st.warning(
                    "Enter a Python package name."
                )


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
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Message DevPilot..."
)


# =========================================================
# HANDLE QUICK PROMPTS
# =========================================================

# Complete starter prompts execute immediately.

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
        # DEV PILOT RESPONSE
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
                    # COMPLETE
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


                    # =========================================
                    # STREAM DEVPILOT RESPONSE
                    # =========================================

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