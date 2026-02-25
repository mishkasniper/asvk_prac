#!/usr/bin/env python3
import sys
import zlib
from pathlib import Path

def get_branches(repo):
    heads_dir = repo / "refs" / "heads"
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

    elif len(sys.argv) == 3:
        branch_name = sys.argv[2]
        branch_file = repo / "refs" / "heads" / branch_name

        if not branch_file.exists():
            print(f"error: branch {branch_name} not found")
            return

        commit_hash = branch_file.read_bytes().decode().strip()
        obj_path = repo / "objects" / commit_hash[:2] / commit_hash[2:]
        header, _, body = zlib.decompress(obj_path.read_bytes()).partition(b'\x00')
        kind, size = header.split()

        out = body.decode()
        print(out)
        

if __name__ == "__main__":
    main()