import subprocess
import os
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger("uvicorn")

def parse_diff(diff_text: str) -> Dict[str, str]:
    """
    Parse a single diff text into a structured format.
    
    Args:
        diff_text: The complete diff text for a single file
        
    Returns:
        Dict containing filename and content
    """
    lines = diff_text.splitlines(keepends=True)
    if not lines:
        return None
        
    # First line should be "diff --git a/path/to/file b/path/to/file"
    first_line = lines[0]
    if not first_line.startswith('diff --git'):
        return None
        
    # Extract filename from the b/path/to/file part
    filename = first_line.split()[-1].lstrip('b/')
    
    return {
        'filename': filename,
        'content': ''.join(lines)
    }

def run_diff_command(command: str, git_root: Path) -> List[Dict[str, str]]:
    """
    Run the git diff command and split output by file.
    
    Args:
        command: The diff command to run (e.g. "git diff" or "git diff | grep foo")
        git_root: Path to the git repository root
        
    Returns:
        List of dicts containing filename and content for each file in the diff
        
    Raises:
        subprocess.SubprocessError: If the command fails
    """
    try:
        # Save current working directory
        original_cwd = os.getcwd()
        
        # Change to git root directory
        os.chdir(git_root)
        
        # Run the command through shell to support pipes
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        # Log any stderr output as errors
        if stderr:
            logger.error(f"Diff command stderr: {stderr}")
        
        if process.returncode != 0:
            raise subprocess.SubprocessError(
                f"Diff command failed with return code {process.returncode}"
            )
            
        # Split the diff output into per-file chunks
        if not stdout.strip():
            return []
            
        diffs = []
        current_diff = []
        
        for line in stdout.splitlines(keepends=True):
            if line.startswith('diff --git') and current_diff:
                # Parse and save the previous file's diff
                parsed_diff = parse_diff(''.join(current_diff))
                if parsed_diff:
                    diffs.append(parsed_diff)
                # Start new diff
                current_diff = [line]
            else:
                current_diff.append(line)
            
        # Parse and add the last file's diff
        if current_diff:
            parsed_diff = parse_diff(''.join(current_diff))
            if parsed_diff:
                diffs.append(parsed_diff)
            
        return diffs
        
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to run diff command: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error running diff command: {e}")
        raise
        
    finally:
        # Always restore original working directory
        os.chdir(original_cwd)