#!/usr/bin/env python3
import argparse
import sys
import webbrowser
from pathlib import Path
import uvicorn
import os
from diffpilot.main import app

def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        Diffpilot serves a local web interface for viewing git diffs across multiple
        columns on large monitors. Files can be grouped and sorted based on patterns
        and priorities, and tagged for better overview. All configuration is done in
        the diffpilot.yaml file in your git repository.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "git_project_path",
        type=Path,
        help="Path to git project"
    )

    parser.add_argument(
        "-p", "--port",
        type=int,
        default=3333,
        help="Specify the port number for the web server (default: 3333)"
    )

    parser.add_argument(
        "-n", "--interval",
        type=float,
        default=2.0,
        help="Refresh interval in seconds, can be fractional (default: 2.0)"
    )

    parser.add_argument(
        "--dark-mode",
        choices=["on", "off"],
        default="on",
        help="Enable or disable dark mode (default: off)"
    )

    parser.add_argument(
        "--diff-command",
        default="git diff --color=never",
        help="""Custom diff command (default: "git diff --color=never")
                Example: --diff-command="git diff master...HEAD"
                Example: --diff-command="git diff --cached\""""
    )

    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't automatically open browser window on startup"
    )

    return parser.parse_args()

async def open_browser():
    """Opens the browser after the server starts"""
    if should_open_browser:
        webbrowser.open(f"http://127.0.0.1:{args.port}")

def main():
    args = parse_args()
    
    # Validate that the provided path exists
    if not args.git_project_path.exists():
        print(f"Error: Path does not exist: {args.git_project_path}", file=sys.stderr)
        sys.exit(1)

    # Validate that the provided path is a git repository
    git_dir = args.git_project_path / ".git"
    if not git_dir.is_dir():
        print(f"Error: Not a git repository: {args.git_project_path}", file=sys.stderr)
        sys.exit(1)

    # Set environment variables for the FastAPI app
    os.environ["DIFFPILOT_DARK_MODE"] = args.dark_mode
    os.environ["DIFFPILOT_REFRESH_INTERVAL"] = str(args.interval)
    os.environ["DIFFPILOT_GIT_PROJECT_PATH"] = str(args.git_project_path.absolute())
    os.environ["DIFFPILOT_DIFF_COMMAND"] = args.diff_command

    # Store whether to open browser in global scope so the coroutine can access it
    global should_open_browser
    should_open_browser = not args.no_open

    # Configure and start uvicorn
    config = uvicorn.Config(
        "diffpilot.main:app",
        host="127.0.0.1",
        port=args.port,
        reload=True,
        reload_dirs=[str(Path(__file__).parent)],
        # callback_notify=[open_browser]  # Pass as a list of coroutines
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main() 