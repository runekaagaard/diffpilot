from typing import List, Dict, Union, Optional, Tuple
import hashlib
def run_diff_command(command: str, git_root: Path) -> Tuple[str, List[Dict[str, str]]]:
    """
    Run the git diff command and split output by file.
    
    Returns:
        Tuple of (checksum, diffs) where:
        - checksum is MD5 of the raw diff output
        - diffs is the list of parsed and prioritized diffs
    """
        # Calculate checksum of raw output
        checksum = hashlib.md5(stdout.encode()).hexdigest()
            
            return checksum, []
        return checksum, prioritize_diffs(diffs, git_root)