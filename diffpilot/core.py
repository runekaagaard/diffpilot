import subprocess
import os
import logging
from typing import List, Dict, Union, Optional
from pathlib import Path
import yaml
from fnmatch import fnmatch

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
    """Run the git diff command and split output by file."""
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
            
        # Parse all diffs first
        diffs = []
        current_diff = []
        
        for line in stdout.splitlines(keepends=True):
            if line.startswith('diff --git') and current_diff:
                parsed_diff = parse_diff(''.join(current_diff))
                if parsed_diff:
                    diffs.append(parsed_diff)
                current_diff = [line]
            else:
                current_diff.append(line)
            
        if current_diff:
            parsed_diff = parse_diff(''.join(current_diff))
            if parsed_diff:
                diffs.append(parsed_diff)
        
        # Prioritize and sort the diffs
        return prioritize_diffs(diffs, git_root)
        
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to run diff command: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error running diff command: {e}")
        raise
        
    finally:
        # Always restore original working directory
        os.chdir(original_cwd)

def load_config(git_root: Path) -> Dict:
    """Load diffpilot.yaml configuration file"""
    config_path = git_root / "diffpilot.yaml"
    if not config_path.exists():
        return {"file_groups": [], "tags": {}, "config_path": None}
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
        config['config_path'] = str(config_path)
        return config

def match_file_group(filename: str, group: Dict) -> bool:
    """Check if filename matches group's glob pattern(s)"""
    glob_patterns = group['glob']
    if isinstance(glob_patterns, str):
        glob_patterns = [glob_patterns]
    
    return any(fnmatch(filename, pattern) for pattern in glob_patterns)

def find_matching_group(filename: str, file_groups: List[Dict]) -> Optional[Dict]:
    """Find the first group that matches the filename"""
    for group in file_groups:
        if match_file_group(filename, group):
            return group
    return None

def prioritize_diffs(diffs: List[Dict], git_root: Path) -> List[Dict]:
    """
    Prioritize diffs based on diffpilot.yaml configuration.
    First matching group wins (first match in the list).
    Unmatched files go last.
    
    Args:
        diffs: List of diffs from run_diff_command
        git_root: Path to git repository root
        
    Returns:
        Sorted list of diffs with added priority and tags
    """
    config = load_config(git_root)
    file_groups = config.get('file_groups', [])
    tags_config = config.get('tags', {})
    
    # Enhance diffs with priority and tags
    enhanced_diffs = []
    for diff in diffs:
        filename = diff['filename']
        matching_group = find_matching_group(filename, file_groups)
        
        if matching_group:
            # Add group information to diff
            diff['priority'] = matching_group.get('priority', 0)
            diff['tags'] = matching_group.get('tags', [])
            diff['group_title'] = matching_group.get('title', '')
        else:
            # Default values for unmatched files - highest priority to go last
            diff['priority'] = 1000000
            diff['tags'] = []
            diff['group_title'] = 'Ungrouped'
            
        enhanced_diffs.append(diff)
    
    # Sort by priority (lowest first) and then by filename
    return sorted(enhanced_diffs, key=lambda x: (x['priority'], x['filename']))