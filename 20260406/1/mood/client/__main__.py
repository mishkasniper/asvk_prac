import sys
from .client import MUDClient

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m mood.client <username>")
        sys.exit(1)
    MUDClient(sys.argv[1]).cmdloop()

if __name__ == "__main__":
    main()