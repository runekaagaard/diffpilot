#!/usr/bin/env python3
import argparse
import sys
import webbrowser
from pathlib import Path
import uvicorn
import os
import subprocess
from diffpilot.main import app
from diffpilot.core import load_config

def validate_git_branch(git_project_path, branch_name):
    """
    Validate if the given branch exists in the git repository
    
    Args:
        git_project_path (Path): Path to the git repository
        branch_name (str): Name of the branch to validate
    
    Returns:
        bool: True if branch exists, False otherwise
    """
    try:
        # Change to the git project directory
        original_dir = os.getcwd()
        os.chdir(git_project_path)
        
        # Run git command to check branch existence
        result = subprocess.run(
            ['git', 'show-ref', '--verify', f'refs/heads/{branch_name}'],
            capture_output=True,
            text=True
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        return result.returncode == 0
    except Exception:
        return False

def get_diff_command(args, git_project_path):
    """
    Determine the appropriate diff command based on CLI arguments
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments
        git_project_path (Path): Path to the git repository
    
    Returns:
        str: Diff command to be used
    """
    if args.diff_local:
        return 'git ls-files --others --exclude-standard -z | xargs -0 -I {{}} git diff /dev/null {{}}; git diff HEAD'
    
    if args.diff_branch:
        # Validate the branch name
        if not validate_git_branch(git_project_path, args.diff_branch):
            print(f"Error: Branch '{args.diff_branch}' does not exist", file=sys.stderr)
            sys.exit(1)
        
        return f'git ls-files --others --exclude-standard -z | xargs -0 -I {{}} git diff /dev/null {{}}; git diff $(git merge-base {args.diff_branch} HEAD)'
    
    return args.diff_command

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

    diff_group = parser.add_mutually_exclusive_group()
    diff_group.add_argument(
        "--diff-command",
        default="git diff --color=never",
        help="""Custom diff command (default: "git diff --color=never")
                Example: --diff-command="git diff master...HEAD"
                Example: --diff-command="git diff --cached\""""
    )
    diff_group.add_argument(
        "--diff-local",
        action="store_true",
        help="Show diffs for untracked and modified local files"
    )
    diff_group.add_argument(
        "--diff-branch",
        type=str,
        help="Compare current branch with specified branch"
    )

    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't automatically open browser window on startup"
    )

    parser.add_argument(
        "--window-title",
        default="Diffpilot",
        help="Set the window title (default: Diffpilot)"
    )

    return parser.parse_args()

def main():
    args = parse_args()
    
    # Validate git project path
    if not args.git_project_path.exists() or not (args.git_project_path / ".git").is_dir():
        print(f"Error: Invalid git repository: {args.git_project_path}", file=sys.stderr)
        sys.exit(1)

    # Determine diff command
    diff_command = get_diff_command(args, args.git_project_path)

    # Set configuration in app.extra before running
    app.extra['config'] = {
        'interval': args.interval,
        'git_project_path': str(args.git_project_path.absolute()),
        'diff_command': diff_command,
        'port': args.port,
        'window_title': args.window_title
    }

    # Configure uvicorn server
    config = uvicorn.Config(
        "diffpilot.main:app", 
        host="127.0.0.1", 
        port=args.port,
        reload=True,
        reload_dirs=[str(Path(__file__).parent)]
    )
    
    # Optional browser opening
    if not args.no_open:
        webbrowser.open(f"http://127.0.0.1:{args.port}")
        
    # Create and run server
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main() 