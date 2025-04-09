![diffpilot](assets/logo.svg)

# diffpilot

Diffpilot serves a local web interface for viewing git diffs across multiple columns on large monitors. Files can be grouped and sorted based on patterns and priorities, and tagged for better overview. All configuration is done in the diffpilot.yaml file in your git repository.

![screenshot](assets/screenshot.png)

## Installation

```bash
pip install diffpilot
```

## Quick start

```bash
cd /path/to/your/repo
diffpilot .
```

Point your browser to http://localhost:3333 if it doesn't open automatically.

## Configuration

Create a `diffpilot.yaml` in your repository root:

```yaml
file_groups:
  - title: "Python Modules"
    glob: "*.py"
    priority: 1
    tags: [Backend]

  - title: "Frontend"
    glob: 
      - "*.html"
      - "*.css"
      - "*.js"
    priority: 2
    tags: [Frontend]

  - title: "Documentation"
    glob: 
      - "*.md"
      - "*.man"
    priority: 3
    tags: [Documentation]

  - title: "Other"
    glob: "**"
    priority: 4 
    tags: [Other]

tags:
  Backend:
    css_class: "bg-success"
  Frontend:
    css_class: "bg-dark"
  Documentation:
    css_class: "bg-info"
  Other:
    css_class: "bg-light"
```

## Usage examples

```bash
# Show all changes, including:
# - Untracked files not yet in git
# - Modified tracked files
# - Staged changes
# - Uncommitted changes
# Runs two git commands:
# 1. Show diffs for untracked files
# 2. Show diffs for tracked changes
diffpilot . --diff-local

# Show changes in current branch compared to main, including:
# - Untracked files not yet in git
# - Modified tracked files
# - Staged changes
# - Uncommitted changes
# - Differences from the point where current branch diverged from main
# Runs two git commands:
# 1. Show diffs for untracked files
# 2. Show diffs compared to branch divergence point
diffpilot . --diff-branch main

# Start with 5 second refresh
diffpilot -n 5 .

# Use a different port
diffpilot -p 8080 /path/to/project

# Show staged changes
diffpilot . --diff-command="git diff --cached"

# Set custom window title
diffpilot . --window-title "My Project Diffs"
```

## Options

```
-p, --port=NUMBER         Web server port (default: 3333)
-n, --interval=SECONDS    Refresh interval, can be fractional (default: 2.0)
--diff-command=COMMAND    Custom diff command
--diff-local              Show all uncommitted changes (untracked, modified, staged)
--diff-branch=BRANCH      Show changes in current branch compared to specified branch
--window-title=TITLE      Set custom window title (default: Diffpilot)
--no-open                 Don't open browser automatically
-h, --help                Show help message
```

## File Groups Matching

When multiple file groups match a file, the **first matching group** in the configuration file will be used for priority, and tags. Order your file groups from most specific to most general.

## Tag styling

Tags are rendered as Bootstrap badges and can be styled using Bootstrap background classes or custom CSS. See the [Flatly theme badges](https://bootswatch.com/flatly/) for available styles.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://opensource.org/licenses/MIT)

## My Other LLM Projects

- **[MCP Alchemy](https://github.com/runekaagaard/mcp-alchemy)** - Connect Claude Desktop to databases for exploring schema and running SQL.
- **[MCP Redmine](https://github.com/runekaagaard/mcp-redmine)** - Let Claude Desktop manage your Redmine projects and issues.
- **[MCP Notmuch Sendmail](https://github.com/runekaagaard/mcp-notmuch-sendmail)** - Email assistant for Claude Desktop using notmuch.
- **[Claude Local Files](https://github.com/runekaagaard/claude-local-files)** - Access local files in Claude Desktop artifacts.