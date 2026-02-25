#!/usr/bin/env python3
import sys
import zlib
from pathlib import Path
 
SHIFT = "  "

def get_branches(repo_path):
    heads_dir = repo_path / "refs" / "heads"
    branches = []
    
    if heads_dir.exists():
        for branch_file in heads_dir.iterdir():
            if branch_file.is_file():
                branches.append(branch_file.name)
    
    return branches

def main():
    if len(sys.argv) < 2:
        print("use: <git path> [branch]")
        return
    
    repo = Path(sys.argv[1]) / ".git"

    if not repo.exists():
        print(f"error: {repo} not found")
        return
    
    if len(sys.argv) == 2:
        branches = get_branches(repo)
        for branch in branches:
            print(branch)

if __name__ == "__main__":
    main()