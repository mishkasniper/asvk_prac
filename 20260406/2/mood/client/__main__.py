import sys
import argparse
from .client import MUDClient

def main():
    parser = argparse.ArgumentParser(description='MOOD MUD Client')
    parser.add_argument('username', help='Your username')
    parser.add_argument('--file', help='Script file (.mood) with commands to execute')
    args = parser.parse_args()

    client = MUDClient(args.username)
    if args.file:
        client.run_script(args.file)
    else:
        client.cmdloop()

if __name__ == "__main__":
    main()