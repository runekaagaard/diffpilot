import subprocess
import os
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger("uvicorn")

def get_language(filename: str) -> str:
    """Determine the programming language based on file extension"""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'markup',
        '.xml': 'markup',
        '.css': 'css',
        '.scss': 'scss',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.md': 'markdown',
        '.sh': 'bash',
        '.bash': 'bash',
        '.rst': 'rest',
    }
    ext = Path(filename).suffix.lower()
    return ext_map.get(ext, 'diff')

def delete_metadata(diff_text: str) -> str:
    """
    Remove git diff metadata from the beginning of the diff.
    Handles various edge cases like binary files and permission changes.
    
    Args:
        diff_text: Raw git diff output for a single file
        
    Returns:
        Cleaned diff text without metadata
    """
    lines = diff_text.splitlines(keepends=True)
    if not lines:
        return ""
    
    # Handle special cases first
    for line in lines:
        if line.startswith('Binary files') or line.startswith('Only in'):
            return diff_text  # Return full text for special diffs
    
    # Find the position after the last metadata line
    for i, line in enumerate(lines):
        # Standard diff metadata ends with +++ line
        if line.startswith('+++'):
            return ''.join(lines[i + 1:])
        # But some diffs might be different:
        # - Mode changes only show mode lines
        # - New files might not have --- line
        # - Deleted files might not have +++ line
        elif line.startswith('@@'):
            return ''.join(lines[i:])
            
    # If we didn't find any markers, return original
    return diff_text

def parse_diff(diff_text: str) -> Dict[str, str]:
    """Parse a single diff text into a structured format."""
    lines = diff_text.splitlines(keepends=True)
    if not lines:
        return None
        
    first_line = lines[0]
    if not first_line.startswith('diff --git'):
        return None
        
    # Extract filename from the b/path/to/file part
    filename = first_line.split()[-1].lstrip('b/')
    language = get_language(filename)
    
    # Detect file status by looking at the actual diff content
    status = "Modified"  # Default status
    for line in lines:
        if line.startswith('new file mode'):
            status = "Added"
            break
        elif line.startswith('deleted file mode'):
            status = "Deleted"
            break
        elif line.startswith("@@"):
            break
    
    # Clean the diff content
    cleaned_content = delete_metadata(diff_text)
    
    return {
        'filename': filename,
        'language': language,
        'status': status,
        'content': cleaned_content
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