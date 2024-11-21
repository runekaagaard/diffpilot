import subprocess
import os
import logging
from typing import List
from pathlib import Path

logger = logging.getLogger("uvicorn")

def run_diff_command(command: str, git_root: Path) -> List[str]:
    """
    Run the git diff command and split output by file.
    
    Args:
        command: The diff command to run (e.g. "git diff" or "git diff | grep foo")
        git_root: Path to the git repository root
        
    Returns:
        List of file diffs, each including its diff header
        
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
        # A new file diff starts with "diff --git"
        if not stdout.strip():
            return []
            
        file_diffs = []
        current_diff = []
        
        for line in stdout.splitlines(keepends=True):
            if line.startswith('diff --git') and current_diff:
                # Save the previous file's diff
                file_diffs.append(''.join(current_diff))
                current_diff = []
            current_diff.append(line)
            
        # Add the last file's diff
        if current_diff:
            file_diffs.append(''.join(current_diff))
            
        return file_diffs
        
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to run diff command: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error running diff command: {e}")
        raise
        
    finally:
        # Always restore original working directory
        os.chdir(original_cwd)