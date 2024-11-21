from typing import List, Dict, Union, Optional
import yaml
from fnmatch import fnmatch
    """Run the git diff command and split output by file."""
        # Parse all diffs first
        
        # Prioritize and sort the diffs
        return prioritize_diffs(diffs, git_root)
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