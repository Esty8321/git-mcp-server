# Git MCP Server 🚀

A local **Model Context Protocol (MCP) server**  that empowers AI coding agents to work with Git repositories in a safe, automated, and non-interactive way.

This project focuses on **developer productivity**: it enables AI agents to execute common Git workflows through explicit MCP tools, from cloning repositories
to committing changes and opening pull requests.

---

## 🌟Overview

Modern AI coding agents are excellent at writing and modifying code, but they often lack standardized, non-interactive access to version control workflows.

This project bridges that gap by exposing Git and GitHub operations as explicit MCP tools, allowing AI agents to operate on repositories safely and predictably without relying on terminal prompts or editors.

---

## 🏗️Architecture

- Runs locally on the developer's machine
- Exposes Git capabilities as MCP tools
- Executes Git and GitHub CLI commands via subprocesses
- Relies on existing local authentication (SSH, gh auth, credential manager)

---

## 🛠️Available Tools

### git_clone
Clone a remote repository into a local directory.

### git_diff
Generate diffs that can be used by AI agents to reason about changes and compose meaningful commit messages.

### git_commit
Stage changes and create a commit with a provided message.

### git_push
Push a branch to a remote repository.

### open_pr_to_base
Create a Pull Request using the GitHub CLI (`gh`).

### send_email
Send an email notification via SMTP.
This tool allows an AI agent to notify human reviewers when work is ready (for example, after opening a Pull Request).

#### Configuration (optional)

To enable email sending, create a `.env` file in the project root and provide the required SMTP settings.

Example `.env` file:

```env
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=

---

## 🔁 Example Workflow

1. Clone a repository using `git_clone`.
2. Modify code locally.
3. Inspect changes using `git_diff`.
4. Compose a commit message based on the diff and context.
5. Commit changes using `git_commit`.
6. Push the branch using `git_push`.
7. Attempt to open a Pull Request using `open_pr_to_base`.
8. Optionally notify reviewers using `send_email`.

---

## ⚙️Requirements
- Python 3.9+
- Git
- GitHub CLI (`gh`) for PR creation
- Local GitHub authentication
- MCP-compatible client (e.g. Claude Desktop)

---

## ▶️Running as a Local MCP Server

Install Python dependencies:
```bash
pip install -r requirements.txt
```
Setup:
1. Clone the repository to any local directory
2. Create a file named `mcp.json` in the project root
3. Copy the contents of `mcp.example.json`
4. Replace `<PATH_TO_YOUR_LOCAL_CLONE>` with your local path
5. Register the file in Claude Desktop → MCP → Add Local MCP

---

## 🚧 Future Improvements

The following features would further enhance the server:

- `git_pull` with conflict detection
- Automatic conflict resolution assistance
- Branch merging tools
- Rebase workflows
- Reviewer assignment for Pull Requests
- Commit message linting and enforcement

These additions would move the server closer to a more complete AI-assisted Git workflow toolkit.
