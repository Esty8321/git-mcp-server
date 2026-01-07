# Git MCP Server 🚀

A local **Model Context Protocol (MCP) server**  that empowers AI coding agents to work with Git repositories in a safe, automated, and non-interactive way.

This project focuses on **developer productivity**: it enables AI agents to execute common Git workflows through explicit MCP tools, from cloning repositories
to committing changes and opening pull requests.

---

## 🌟 Overview

Modern AI coding agents are excellent at writing and modifying code, but they often lack standardized, non-interactive access to version control workflows.

This project bridges that gap by exposing Git and GitHub operations as explicit MCP tools, allowing AI agents to operate on repositories safely and predictably without relying on terminal prompts or editors.

---

## 🏗️ Architecture

- Runs locally on the developer's machine
- Exposes Git capabilities as MCP tools
- Executes Git and GitHub CLI commands via subprocesses
- Relies on existing local authentication (SSH, gh auth, credential manager)

---

## 🛠️ Available Tools

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
FROM_EMAIL=
```

---

## 🔁 Example Workflow

1. Clone a repository using `git_clone`.
2. Modify code locally.
3. Inspect changes using `git_diff`.
4. Compose a commit message based on the diff and context.
5. Commit changes using `git_commit`.
6. Push the branch using `git_push`.
7. Open a Pull Request using `open_pr_to_base`.
8. Optionally notify reviewers using `send_email`.

---

## ⚙️ Requirements
- Python 3.9+
- Git
- GitHub CLI (`gh`) for PR creation
- Local GitHub authentication
- MCP-compatible client (e.g. Claude Desktop)

---

## ▶️ Running as a Local MCP Server

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

## 🧾 Error Codes Reference

The MCP server returns structured error codes to allow AI agents and humans
to understand failures programmatically and recover gracefully.

### Common Error Codes

| Code | Meaning | Typical Tool | How to Fix |
|-----|--------|-------------|-----------|
| `invalid_input` | Input validation failed | Any tool | Check required fields and constraints |
| `not_a_directory` | Path exists but is not a directory | git_clone | Provide a directory path |
| `not_a_git_repo` | Path is not a Git repository | git_status / git_diff / git_commit / git_push | Ensure `.git` exists |
| `dest_not_directory` | Destination exists but is not a directory | git_clone | Choose a directory path |
| `dest_dir_not_empty` | Destination directory is not empty | git_clone | Use an empty directory |
| `command_timeout` | Command exceeded the allowed timeout | Any git/gh command | Increase timeout or check network |
| `command_failed` | Command exited with non-zero status | Any git/gh command | Inspect stderr and follow hint |
| `gh_not_configured` | GitHub CLI is not authenticated | open_pr_to_base | Run `gh auth login` |
| `email_config_missing` | SMTP configuration missing | send_email | Set SMTP vars in `.env` |
| `email_send_failed` | SMTP send failed | send_email | Verify credentials and SMTP host |
| `branch_detect_failed` | Current branch could not be detected | git_push / open_pr_to_base | Ensure repo has commits |
| `on_base_branch` | Attempted PR from base branch | open_pr_to_base | Switch to a feature branch |

---

## 🧰 Troubleshooting

### 1) `git_push` fails (authentication / permission)
**Symptoms:**
- `error.code = command_failed`
- stderr mentions authentication, permission denied, or could not read username.

**Fix:**
- Prefer SSH remote + SSH keys, or configure credentials ahead of time.
- This server runs non-interactively, so it will not open login prompts.

---

### 2) `open_pr_to_base` fails with "No commits between ..."
**Symptoms:**
- stderr contains: `No commits between <base> and <branch>`

**Fix:**
- Ensure you committed changes on the feature branch.
- Ensure the branch is pushed: run `git_push` with `set_upstream=true` on first push.

---

### 3) `send_email` fails with SMTP_PORT / config missing
**Symptoms:**
- `SMTP_PORT` is None / `EMAIL_CONFIG_MISSING`

**Fix:**
- Verify `.env` is loaded (correct path).
- Ensure these variables exist: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL
- Example: `SMTP_PORT=587`

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

---





