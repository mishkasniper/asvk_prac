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

        lines = body.decode().split('\n')

        tree_hash = ''
        for line in lines:
            if line.startswith('tree '):
                tree_hash = line[5:].strip()
                break

        obj_path = repo / "objects" / tree_hash[:2] / tree_hash[2:]
        header, _, tree_body = zlib.decompress(obj_path.read_bytes()).partition(b'\x00')

        while tree_body:
            treeobj, _, tree_body = tree_body.partition(b'\x00')
            tmode, tname = treeobj.split()
            num, tree_body = tree_body[:20], tree_body[20:]
            mode_str = tmode.decode()
            if mode_str.startswith('04') or mode_str == '40000':
                obj_type = 'tree'
            else:
                obj_type = 'blob'
            print(f"{obj_type} {num.hex()}    {tname.decode()}")

        
        
        

if __name__ == "__main__":
    main()