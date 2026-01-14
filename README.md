# Auto-Research Agent (ARAP)

[English](README.md) | [中文](README_zh.md)

**A practical toolkit that turns your coding agent into an autonomous academic researcher.**

This repository provides the protocols and tools necessary for AI Agents (such as GitHub Copilot, Cursor, Windsurf) to conduct **fully automated, deep, and systematic literature surveys**. 

By combining a rigorous Standard Operating Procedure with executable tools, it guides the agent through a complete "Funnel Process": from wide scoping to intelligent selection, and finally to deep analysis and report generation.

## 🚀 Key Philosophy

1.  **Agent-First Design**: This is not just a library for humans. It is a "driver" for Agents. By reading the `research_rules.md`, the Agent "learns" how to behave like a researcher.
2.  **Protocol-Driven Automation**: The core is the `research_rules.md` which defines strict phases (Deep Research Funnel). The Agent simply follows the instructions step-by-step.
3.  **Extensible & Customizable**:
    *   **Workflows**: You can modify `research_rules.md` to change the research logic (e.g., add a "Peer Review" phase).
    *   **Skills**: You can add new tools to the `skills/` directory (e.g., Google Scholar scrapers, vector database connectors) to enhance the agent's capabilities.

## 📂 Project Structure

```text
.
├── AGENT_SKILLS_GUIDE.md   # The "User Manual" for Agents on how to use tools
├── research_rules.md       # The "Brain": SOP and Logic for the research workflow
├── requirements.txt        # Python dependencies
├── skills/                 # The "Hands": Executable tools
│   └── arxiv/              # Example skill: ArXiv search & retrieval
│       ├── SKILL.md        
│       └── scripts/        
└── surveys/                # The "Workspace": Where research happens
    └── 20260114_MyTopic/   # All artifacts (PDFs, Notes, Reports) go here
```

## 🛠️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/auto-research-agent.git
cd auto-research-agent

# 2. Install dependencies (Crucial for the agent to run scripts)
pip install -r requirements.txt
```

## 📖 How to Use (with AI Agents)

**You don't need to run scripts manually.** Your job is to set the stage and let the Agent perform the work.

### Step 1: Open in Your AI Editor
Open this folder in VS Code (with GitHub Copilot) or Cursor.

### Step 2: Instruct the Agent
Open the Chat/Composer panel and prompt:

> "I want to conduct a deep survey on **[Your Topic Here]**. Please read `research_rules.md` and `AGENT_SKILLS_GUIDE.md` to understand your role and available tools. Then, help me start with Phase 1: Pre-research & Proposal."

### Step 3: Follow the Agent
The Agent will:
1.  **Propose a plan**: Create a `research_plan.md` for you to review.
2.  **Execute Search**: Call the `skills/arxiv/scripts/arxiv_cli.py` tool.
3.  **Download & Read**: Use `markitdown` to process PDFs.
4.  **Write Report**: Generate the final survey.

*You just need to review its outputs and say "Proceed" or "Revise".*

## 🧩 Customizing Your Agent

### Modifying the Workflow
Edit `research_rules.md`. For example, if you want the agent to always translate the final report into Chinese, add a rule in "Phase 6":
> "Constraint: The final report `03_Survey_Report.md` must be written in Chinese."

### Adding New Skills
1.  Create a folder `skills/new_tool/`.
2.  Add a python script in `skills/new_tool/scripts/`.
3.  Write a `SKILL.md` to explain *when* and *how* the Agent should use this tool.
4.  Add the reference to `AGENT_SKILLS_GUIDE.md`.

## 📄 License
[MIT](LICENSE)
