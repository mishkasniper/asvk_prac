import socket
from shlex import split
from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO
import cmd
import threading
import sys
import readline

jgsbat = read_dot_cow(StringIO("""
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\\\\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\\\\\\'--'//__
         (((""`  `"")))
EOC
"""))

class MUDClient(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "(MUD) "

    def __init__(self, username, host='localhost', port=1337):
        super().__init__()
        self.username = username
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
        
    def receive_messages(self):
        while self.running:
            try:
                data = self.sock.recv(4096).decode().strip()
                if not data:
                    break
                print(f"\n{data}")
                print(f"{self.prompt}{readline.get_line_buffer()}", end='', flush=True)
            except socket.timeout:
                continue
            except:
                break
        self.running = False

    def send_command(self, cmd):
        try:
            self.sock.sendall((cmd + '\n').encode())
        except:
            print("Connection lost.")
            self.running = False
            return

    def do_up(self, arg):
        """Move up. Usage: up"""
        self.send_command(f"move -1 0")

    def do_down(self, arg):
        """Move down. Usage: down"""
        self.send_command(f"move 1 0")

    def do_left(self, arg):
        """Move left. Usage: left"""
        self.send_command(f"move 0 -1")

    def do_right(self, arg):
        """Move right. Usage: right"""
        self.send_command(f"move 0 1")

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
                except:
                    print("Invalid arguments")
                    return
                i += 2
            elif args[i] == 'hp':
                try:
                    hp = int(args[i+1])
                    if hp <= 0: raise ValueError
                except:
                    print("Invalid arguments")
                    return
                i += 2
            elif args[i] == 'coords':
                try:
                    x = int(args[i+1])
                    y = int(args[i+2])
                    if not (0 <= x < 10 and 0 <= y < 10): raise ValueError
                except:
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
        Attack monster in your position
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
        """complete for command addmon"""
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

    def do_exit(self, arg):
        """Exit the MUD. Usage: exit"""
        self.send_command("exit")
        self.running = False
        self.sock.close()
        self.receiver.join(timeout=2)
        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        return self.do_exit(arg)

    def default(self, line):
        print("Invalid command")

    def emptyline(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        sys.exit(1)
    MUDClient(sys.argv[1]).cmdloop()