# diffpilot

Diffpilot serves a local web interface for viewing git diffs across multiple columns on large monitors. Files can be grouped and sorted based on patterns and priorities, and tagged for better overview. All configuration is done in the diffpilot.yaml file in your git repository.

![Screenshot coming soon]()

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
  - title: "Django Models"
    glob: "*/models.py"
    priority: 10
    font_size: "90%"
    tags: [models, python, core]
  - title: "Tests"
    glob: "*/tests/*.py"
    priority: 8
    font_size: "85%"
    tags: [tests, python]

tags:
  models:
    css_class: "bg-primary"
  python:
    css_class: "custom-python"

extra_css: "./diffpilot.css"  # Optional
```

## Usage examples

```bash
# Start with 5 second refresh
diffpilot -n 5 .

# Use a different port
diffpilot -p 8080 /path/to/project

# Show staged changes
diffpilot . --diff-command="git diff --cached"

# Compare with main branch
diffpilot . --diff-command="git diff main..."

# Start with dark mode
diffpilot --dark-mode=on /path/to/project
```

## Options

```
-p, --port=NUMBER          Web server port (default: 3333)
-n, --interval=SECONDS     Refresh interval, can be fractional (default: 2.0)
--dark-mode=on|off        Enable dark mode (default: off)
--diff-command=COMMAND    Custom diff command
--no-open                 Don't open browser automatically
-h, --help               Show help message
```

## Tag styling

Tags are rendered as Bootstrap badges and can be styled using Bootstrap background classes or custom CSS. See the [Flatly theme badges](https://bootswatch.com/flatly/) for available styles.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://opensource.org/licenses/MIT)