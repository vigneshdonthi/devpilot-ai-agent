# ⚡ DevPilot

> An AI-powered developer assistant that can chat, analyze Python projects, explore GitHub repositories, inspect source code, check dependencies, and autonomously use developer tools.

DevPilot combines a conversational AI interface with an autonomous tool-using agent. It provides two modes:

- 💬 **Chat Mode** — Ask programming, AI, Python, Django, LangChain, and general technical questions.
- ⚡ **Agent Mode** — DevPilot autonomously selects and uses tools to complete developer tasks.

---

## 🌐 Live Demo

> 🚧 Deployment in progress

Once deployed, the live application will be available here:

```text
https://devpilot.streamlit.app
```

---

## ✨ Features

### ⚡ Agent Mode

DevPilot can understand a developer task, decide which tools are required, execute them, and generate a final response.

It can:

- Explore GitHub repositories
- Inspect repository structure
- Find important source files
- Read files directly from GitHub
- Explain unfamiliar source code
- Analyze Python projects
- Analyze Python source files
- Check project dependencies
- Detect missing dependencies
- Detect duplicate dependencies
- Detect unpinned dependencies
- Check Python package versions
- Perform multi-step tool workflows

### 💬 Chat Mode

DevPilot also works as a normal AI assistant without invoking developer tools.

Use Chat Mode to:

- Learn Python
- Ask programming questions
- Understand AI and machine learning
- Learn LangChain and LangGraph
- Understand AI agents
- Debug ideas
- Understand code
- Discuss software-development concepts

Responses are streamed progressively for a more interactive experience.

---

## 🧠 Example Agent Workflow

Suppose the user asks:

> Explore the Flask GitHub repository, find the main Flask application implementation file, read it, and explain what that file does.

DevPilot can automatically perform a workflow such as:

```text
User Request
     │
     ▼
Understand Task
     │
     ▼
get_github_repo_tree
     │
     ▼
Inspect Repository Structure
     │
     ▼
Identify src/flask/app.py
     │
     ▼
read_github_file
     │
     ▼
Analyze Source Code
     │
     ▼
Generate Explanation
```

The user doesn't need to manually choose each tool.

---

## 🏗️ Architecture

```text
                         User
                           │
                           ▼
                      DevPilot
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        💬 Chat Mode              ⚡ Agent Mode
              │                         │
              ▼                         ▼
        Language Model           LangChain Agent
                                        │
                                        ▼
                                  Tool Selection
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
               GitHub Tools        Project Tools        PyPI Tools
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                                        ▼
                                  Tool Results
                                        │
                                        ▼
                                 Language Model
                                        │
                                        ▼
                               Streaming Response
```

---

## 🛠️ Developer Tools

DevPilot currently contains several specialized tools.

| Tool | Purpose |
|---|---|
| Project Analyzer | Inspects the structure of a Python project |
| File Reader | Reads files from the current project |
| Code Analyzer | Analyzes Python source files |
| Dependency Checker | Checks dependencies against `requirements.txt` |
| Package Checker | Checks Python package versions using PyPI |
| GitHub Repository Analyzer | Retrieves repository information |
| GitHub Tree Explorer | Explores repository files and directories |
| GitHub File Reader | Reads individual source files directly from GitHub |

The AI agent determines when these tools should be used.

---

## 🐙 GitHub Repository Analysis

DevPilot can inspect public GitHub repositories.

Example:

```text
Explore https://github.com/pallets/flask and explain its architecture.
```

DevPilot can retrieve repository information and inspect its files before generating an explanation.

---

## 📖 GitHub Source Code Explanation

DevPilot can also locate and read specific implementation files.

Example:

```text
Explore https://github.com/pallets/flask,
find the main Flask application implementation file,
read it, and explain what that file does.
```

A possible tool sequence is:

```text
get_github_repo_tree
        │
        ▼
src/flask/app.py
        │
        ▼
read_github_file
        │
        ▼
Source Code
        │
        ▼
DevPilot Explanation
```

---

## 🔍 Python Project Analysis

DevPilot can analyze the Python project available in its runtime environment.

Example:

```text
Analyze my current Python project.

First inspect the project structure,
then analyze the Python source files,
check requirements.txt,
and give me the most important problems.
```

DevPilot can inspect:

- Project structure
- Python source files
- Functions
- Classes
- Imports
- Code quality
- Dependencies
- `requirements.txt`

---

## 📦 Dependency Analysis

DevPilot can compare Python imports against `requirements.txt`.

It can identify issues such as:

```text
Missing dependencies
Unpinned dependencies
Duplicate dependencies
Invalid requirements
```

Example:

```text
Analyze my project dependencies using requirements.txt
and identify any problems.
```

---

## 🔄 PyPI Package Checking

DevPilot can check Python package information using PyPI.

Example:

```text
Check the latest PyPI version of langchain.
```

This is useful when reviewing dependency versions.

---

## 🌊 Streaming Responses

DevPilot streams model responses progressively instead of waiting for the entire answer before displaying it.

```text
DevPilot:

The Flask class is the central application
object responsible for routing, configuration...▌
```

Agent Mode can also display tool activity while processing a request.

```text
DevPilot is thinking...

🔧 get_github_repo_tree

🔧 read_github_file

Generating explanation...
```

---

## 💬 Multiple Conversations

DevPilot supports multiple chat sessions.

```text
Recent Chats

● Flask Architecture
  Python Project Review
  LangChain Dependencies
  AI Agent Explanation
```

Each conversation stores its own messages during the active application session.

---

## 📝 Automatic Chat Titles

DevPilot automatically generates short titles from the first message.

For example:

```text
User:

Explore the Flask repository and explain
the main application implementation.
```

can become:

```text
Flask Architecture
```

instead of displaying the entire prompt in the sidebar.

---

## 🔒 Conversation Mode Locking

A new conversation starts by allowing the user to choose:

```text
[ ⚡ Agent ] [ 💬 Chat ]
```

After the first message is sent, the mode becomes locked for that conversation and the selector disappears.

This prevents a conversation from unexpectedly switching between direct chat and autonomous agent execution.

---

## ⚡ Quick Actions

The Streamlit interface provides shortcuts for common developer tasks.

Examples:

```text
🐙 Explore GitHub

📖 Explain GitHub Code

🔍 Review Project

📦 Check Dependencies

🔄 Check PyPI Package
```

Chat Mode also provides starter prompts for learning and technical discussions.

---

## 🧰 Tech Stack

### Language

- Python

### AI / Agent Framework

- LangChain
- LangGraph

### Language Model

- Mistral AI

### User Interface

- Streamlit

### External Services

- GitHub
- PyPI

### Utilities

- Requests
- python-dotenv

---

## 📁 Project Structure

```text
devpilot/
│
├── app.py
├── main.py
├── agent.py
├── requirements.txt
├── .gitignore
│
└── tools/
    ├── __init__.py
    ├── code_analyzer.py
    ├── dependency_checker.py
    ├── file_reader.py
    ├── github_tool.py
    ├── package_checker.py
    └── project_analyzer.py
```

### `app.py`

Contains the Streamlit interface, including:

- Chat interface
- Agent/Chat mode selection
- Streaming output
- Multiple conversations
- Automatic chat titles
- Quick actions
- Tool activity display

### `agent.py`

Contains the DevPilot AI agent configuration.

It connects the language model with DevPilot's developer tools and allows the model to decide when tools should be called.

### `tools/`

Contains the individual developer tools available to the agent.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/vigneshdonthi/devpilot-ai-agent.git
```

Move into the project:

```bash
cd devpilot
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

```env
MISTRAL_API_KEY=your_mistral_api_key
```

Never commit your API key to GitHub.

Your `.gitignore` should include:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
```

---

## ▶️ Run Locally

Start DevPilot with:

```bash
streamlit run app.py
```

Streamlit will provide a local address, usually:

```text
http://localhost:8501
```

Open it in your browser.

---

## 🚀 Deployment

DevPilot can be deployed using Streamlit Community Cloud.

High-level deployment flow:

```text
Local DevPilot
      │
      ▼
    GitHub
      │
      ▼
Streamlit Community Cloud
      │
      ├── app.py
      ├── agent.py
      └── tools/
              │
              ▼
       External APIs / LLM
```

### Deployment steps

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Select the DevPilot repository.
4. Select `app.py` as the application entry point.
5. Add `MISTRAL_API_KEY` to Streamlit Secrets.
6. Deploy the application.
7. Add the deployed URL to this README and the GitHub repository About section.

---

## 🔐 Streamlit Secrets

When deploying, don't upload `.env`.

Configure the key through Streamlit's secret settings:

```toml
MISTRAL_API_KEY = "your_mistral_api_key"
```

The application can then access the API key in the deployed environment.

---

## 💡 Example Prompts

### GitHub architecture

```text
Explore https://github.com/pallets/flask
and explain the architecture of the project.
```

### Source-code exploration

```text
Explore https://github.com/pallets/flask,
find the main Flask application implementation file,
read it, and explain how it works.
```

### Python project review

```text
Analyze my current Python project.
Inspect the structure, source code and dependencies.
Give me the most important problems.
```

### Dependency analysis

```text
Analyze requirements.txt and identify
missing, duplicate or problematic dependencies.
```

### Package checking

```text
Check the latest PyPI version of langchain.
```

### Normal chat

```text
Explain LangChain simply.
```

```text
What is an AI agent?
```

```text
Explain the difference between an LLM
and an AI agent.
```

---

## 📸 Screenshots

Screenshots will be added after deployment.

Recommended screenshots:

### DevPilot Home

```text
Add screenshot here
```

### Agent Mode

```text
Add screenshot here
```

### GitHub Repository Analysis

```text
Add screenshot here
```

### Tool Execution

```text
Add screenshot here
```

### Chat Mode

```text
Add screenshot here
```

---

## 🎬 Demo

A short demonstration GIF/video will be added showing:

```text
Open DevPilot
      ↓
Select Agent Mode
      ↓
Enter GitHub repository
      ↓
DevPilot explores repository
      ↓
Tools execute
      ↓
Response streams
      ↓
Repository explanation
```

---

## 🗺️ Roadmap

Future versions of DevPilot may include:

- [ ] Persistent chat history
- [ ] SQLite/PostgreSQL storage
- [ ] User authentication
- [ ] GitHub authentication
- [ ] Private GitHub repository support
- [ ] GitHub token integration
- [ ] File uploads
- [ ] ZIP project uploads
- [ ] Repository cloning
- [ ] Repository-wide semantic search
- [ ] RAG over large codebases
- [ ] Vector database integration
- [ ] Code embeddings
- [ ] Automated code suggestions
- [ ] Code refactoring suggestions
- [ ] Automated test generation
- [ ] Documentation generation
- [ ] Security analysis
- [ ] Git diff analysis
- [ ] Pull request analysis
- [ ] Multi-agent workflows
- [ ] Persistent agent memory
- [ ] React/Next.js frontend
- [ ] Separate FastAPI backend

---

## ⚠️ Current Limitations

### Local project access

DevPilot's local project tools operate on files available to the machine where DevPilot is running.

When deployed to Streamlit Community Cloud, DevPilot cannot directly inspect files stored on a visitor's computer.

GitHub repository analysis works remotely because repository information is retrieved through GitHub.

Future versions can solve this by supporting:

- Project uploads
- ZIP uploads
- GitHub repository cloning
- Repository-based analysis

### Chat persistence

Current chat history is stored in Streamlit session state.

This means conversations are not permanently stored across all application restarts or sessions.

Persistent database-backed chat history is planned for a future version.

---

## 🔒 Security

DevPilot uses environment variables for sensitive credentials.

Never commit:

```text
.env
API keys
Access tokens
Credentials
.streamlit/secrets.toml
```

If an API key is accidentally pushed to a public repository, revoke it immediately and generate a new key.

---

## 🎯 Project Goals

DevPilot was built to explore how modern AI agents can assist developers by combining:

- LLM reasoning
- Tool calling
- Repository exploration
- Source-code analysis
- Dependency analysis
- Conversational interfaces
- Multi-step autonomous workflows

The goal is to move beyond a basic chatbot and build an assistant capable of interacting with real developer resources.

---

## 👨‍💻 Author

**Vignesh**

Computer Science & Engineering graduate interested in:

- AI Engineering
- Generative AI
- Agentic AI
- Python
- Backend Development
- LLM Applications

---

## 🤝 Feedback

Feedback, suggestions, and ideas for improving DevPilot are welcome.

If you encounter an issue, you can open a GitHub issue describing the problem.

---

## ⭐ Support

If you find DevPilot useful or interesting, consider giving the repository a ⭐.

It helps support the project and its continued development.

---

<p align="center">
  <b>⚡ DevPilot — AI that doesn't just answer. It works with developer tools.</b>
</p>