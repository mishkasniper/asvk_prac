"""MUD client with cmd interface and asynchronous message receiving."""
import socket
from shlex import split
from cowsay import list_cows

import cmd
import threading
import sys
import readline
import time
import webbrowser
from pathlib import Path
from unittest.mock import MagicMock


class MUDClient(cmd.Cmd):
    """Command-line client for MOOD MUD."""

    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "(MUD) "

    def __init__(self, username, host='localhost', port=1337, testing=False):
        """Connect to server, login, start message receiver thread."""
        super().__init__()
        self.username = username
        if testing:
            self.sock = None
            self.running = False
            self.send_command = MagicMock()
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.settimeout(1.0)
        self.sock.sendall(f"login {username}\n".encode())
        resp = self.sock.recv(1024).decode().strip()
        if resp != "login_ok":
            print("Login failed:", resp)
            sys.exit(1)
        print("Connected to server.")
        self.running = True
        self.receiver = threading.Thread(target=self.receive_messages)
        self.receiver.start()

    def run_script(self, filename):
        """Execute commands from a script file with 1 second delay between sends."""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: script file '{filename}' not found.")
            self.sock.close()
            return
        except Exception as e:
            print(f"Error reading script: {e}")
            self.sock.close()
            return

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            self.onecmd(line)
            time.sleep(1)

        self.send_command("exit")
        time.sleep(0.5)
        self.running = False
        self.receiver.join(timeout=2)
        self.sock.close()
        print("Script finished.")

    def do_sayall(self, arg):
        """Send a message to all players. Usage: sayall <message>."""
        if not arg:
            print("Usage: sayall <message>")
            return
        try:
            self.send_command(f"sayall {arg}")
        except Exception:
            print("Invalid arguments")

    def do_movemonsters(self, arg):
        """Enable/disable wandering monsters. Usage: movemonsters on|off."""
        if arg not in ('on', 'off'):
            print("Invalid arguments. Usage: movemonsters on|off.")
            return
        self.send_command(f"movemonsters {arg}")

    def complete_movemonsters(self, text, line, begidx, endidx):
        """Complete on/off for movemonsters command."""
        return [opt for opt in ['on', 'off'] if opt.startswith(text)]

    def receive_messages(self):
        """Background thread reading server messages and displaying them."""
        while self.running:
            try:
                data = self.sock.recv(4096).decode().strip()
                if data:
                    print(f"\n{data}")
                    print(f"{self.prompt}{readline.get_line_buffer()}", end='', flush=True)
            except socket.timeout:
                continue
            except Exception:
                break
        self.running = False

    def send_command(self, cmd):
        """Send a command string to the server."""
        try:
            self.sock.sendall((cmd + '\n').encode())
        except Exception:
            print("Connection lost.")
            self.running = False
            return

    def do_up(self, arg):
        """Move up. Usage: up."""
        self.send_command("move -1 0")

    def do_down(self, arg):
        """Move down. Usage: down."""
        self.send_command("move 1 0")

    def do_left(self, arg):
        """Move left. Usage: left."""
        self.send_command("move 0 -1")

    def do_right(self, arg):
        """Move right. Usage: right."""
        self.send_command("move 0 1")

    def do_addmon(self, arg):
        """
        Create a new monster with given parameters.

        Usage: addmon <monster_name> hello <hello_string> hp <hitpoints> coords <x> <y>
        """
        if not arg:
            print("Invalid arguments")
            return
        try:
            args = split(arg)
        except ValueError:
            print("Invalid arguments")
            return
        if len(args) != 8:
            print("Invalid arguments")
            return
        name = args[0]
        if not (name == "jgsbat" or name in list_cows()):
            print("Cannot add unknown monster")
            return

        i = 1
        hello = hp = x = y = None
        while i < len(args):
            if args[i] == 'hello':
                try:
                    hello = args[i+1]
                except Exception:
                    print("Invalid arguments")
                    return
                i += 2
            elif args[i] == 'hp':
                try:
                    hp = int(args[i+1])
                    if hp <= 0:
                        raise ValueError
                except Exception:
                    print("Invalid arguments")
                    return
                i += 2
            elif args[i] == 'coords':
                try:
                    x = int(args[i+1])
                    y = int(args[i+2])
                    if not (0 <= x < 10 and 0 <= y < 10):
                        raise ValueError
                except Exception:
                    print("Invalid arguments")
                    return
                i += 3
            else:
                print("Invalid arguments")
                return
        if None in (hello, hp, x, y):
            print("Invalid arguments")
            return

        self.send_command(f"addmon {name} {hello} {hp} {x} {y}")

    def do_attack(self, arg):
        """
        Attack monster in your position.

        Usage: attack <name_monster> [with <weapon_name>]
        """
        try:
            args = split(arg) if arg else []
        except ValueError:
            print("Invalid arguments")
            return
        if len(args) == 0:
            print("Incorrect arguments")
            return
        mon_name = args[0]

        weapons = {"sword": 10, "spear": 15, "axe": 20}
        if len(args) == 1:
            weapon = "sword"
        elif len(args) == 3 and args[1] == 'with':
            if args[2] not in weapons:
                print("Unknown weapon")
                return
            weapon = args[2]
        else:
            print("Invalid arguments")
            return
        damage = weapons[weapon]

        self.send_command(f"attack {mon_name} {damage}")

    def complete_attack(self, text, line, begidx, endidx):
        """Complete weapon names after 'with'."""
        args = line[:endidx].split()
        arg_index = len(args)

        weapons = ["sword", "spear", "axe"]

        if arg_index == 1:
            return []

        elif arg_index == 2:
            if "with".startswith(text):
                return ["with"]
            return []

        elif arg_index == 3:
            if len(args) >= 3 and args[2] == "with":
                return [w for w in weapons if w.startswith(text)]
            return []
        return []

    def complete_addmon(self, text, line, begidx, endidx):
        """Complete for command addmon."""
        args = line[:endidx].split()

        if len(args) == 1:
            cows = list_cows() + ["jgsbat"]
            return [cow for cow in cows if cow.startswith(text)]

        used_keywords = set()
        for arg in args[1:]:
            if arg in ("hello", "hp", "coords"):
                used_keywords.add(arg)
        all_keywords = ["hello", "hp", "coords"]
        available = [k for k in all_keywords if k not in used_keywords and k.startswith(text)]
        return available

    def do_locale(self, arg):
        """Set locale. Usage: locale ru_RU.UTF-8."""
        if not arg:
            print("Usage: locale <locale_name>")
            return
        self.send_command(f"locale {arg}")

    def do_exit(self, arg):
        """Exit the MUD. Usage: exit."""
        self.send_command("exit")
        self.running = False
        self.sock.close()
        self.receiver.join(timeout=2)
        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl-D."""
        return self.do_exit(arg)

    def default(self, line):
        """Handle unknown commands."""
        print("Invalid command")

    def emptyline(self):
        """Do nothing on empty line."""
        pass

    def do_documentation(self, arg):
        """Open generated HTML documentation in browser."""
        try:
            from importlib.resources import files
            doc_path = files('mood') / 'html_docs' / 'index.html'
            if doc_path.is_file():
                webbrowser.open(f'file://{doc_path}')
                return
        except (ImportError, OSError):
            pass

        local_doc = Path('docs/_build/html/index.html')
        if local_doc.exists():
            webbrowser.open(f'file://{local_doc.absolute()}')
        else:
            print("Documentation not found. Run 'doit html' to generate it.")
