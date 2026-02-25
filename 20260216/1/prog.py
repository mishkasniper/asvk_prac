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

def print_tree(tree_body):
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

def get_obj(repo, hash):
    obj_path = repo / "objects" / hash[:2] / hash[2:]
    header, _, body = zlib.decompress(obj_path.read_bytes()).partition(b'\x00')
    kind, size = header.split()
    return kind, body

def get_some_hash_from_commit(commit_body, some):
    some += ' '
    lines = commit_body.decode().split('\n')
    for line in lines:
        if line.startswith(some):
            return line[len(some):].strip()
    return None
            

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
        
        while commit_hash:
            kind, com_body = get_obj(repo, commit_hash)

            if kind != b'commit':
                break

            print(f"TREE for commit {commit_hash}")
        
            tree_hash = get_some_hash_from_commit(com_body, some='tree')

            kind, tree_body = get_obj(repo, tree_hash)
            print_tree(tree_body)
            
            commit_hash = get_some_hash_from_commit(com_body, some='parent')

if __name__ == "__main__":
    main()