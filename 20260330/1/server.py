import socket
import threading
import queue
from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def move(self, dx: int, dy: int) -> None:
        self.x = (self.x + dx) % 10
        self.y = (self.y + dy) % 10
    
    def copy(self):
        return Position(self.x, self.y)
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Position index out of range")
        
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value % 10
        elif index == 1:
            self.y = value % 10
        else:
            raise IndexError("Position index out of range")
    
    def __iter__(self):
        yield self.x
        yield self.y

class Monster:
    def __init__(self, pos: Position, name: str, phrase: str, hp: int):
        self.pos = pos
        self.name = name
        self.phrase = phrase
        self.hp = hp

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

class GameServer:
    def __init__(self, host='localhost', port=1337):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.clients = {}
        self.positions = {}
        self.monsters = []
        self.cmd_queue = queue.Queue()
        self.running = True

    def broadcast(self, message, exclude=None):
        for name, sock in self.clients.items():
            if name != exclude:
                try:
                    sock.sendall((message + '\n').encode())
                except:
                    pass

    def send_private(self, name, message):
        sock = self.clients.get(name)
        if sock:
            try:
                sock.sendall((message + '\n').encode())
            except:
                pass

    def handle_command(self, username, cmd_line):
        parts = cmd_line.strip().split()
        if not parts:
            return
        cmd = parts[0]

        if cmd == 'move':
            try:
                dx, dy = int(parts[1]), int(parts[2])
            except (IndexError, ValueError):
                return
            with self.lock:
                pos = self.positions.get(username)
                if not pos:
                    pos = Position(0, 0)
                pos.move(dx, dy)
                self.positions[username] = pos
                self.send_private(username, f"You moved to ({pos.x}, {pos.y})")
                for m in self.monsters:
                    if m.pos == pos:
                        if m.name == 'jgsbat':
                            greeting = cowsay(m.phrase, cowfile=jgsbat)
                        else:
                            greeting = cowsay(m.phrase, cow=m.name)
                        self.send_private(username, greeting)
                        break

        elif cmd == 'addmon':
            try:
                name = parts[1]
                hello = parts[2]
                hp = int(parts[3])
                x = int(parts[4])
                y = int(parts[5])
            except (IndexError, ValueError):
                return
            pos = Position(x, y)
            with self.lock:
                replaced = False
                for i, m in enumerate(self.monsters):
                    if m.pos == pos:
                        self.monsters[i] = Monster(pos, name, hello, hp)
                        replaced = True
                        break
                if not replaced:
                    self.monsters.append(Monster(pos, name, hello, hp))
                msg = f"{username} added monster {name} with {hp} HP"
                if replaced:
                    msg += " (replaced)"
                self.broadcast(msg)

        elif cmd == 'attack':
            try:
                mon_name = parts[1]
                damage = int(parts[2])
            except (IndexError, ValueError):
                return
            with self.lock:
                pos = self.positions.get(username)
                if not pos:
                    return
                target = None
                for m in self.monsters:
                    if m.pos == pos and m.name == mon_name:
                        target = m
                        break
                if target is None:
                    self.send_private(username, f"No {mon_name} here")
                    return
                if damage >= target.hp:
                    damage = target.hp
                    died = True
                    self.monsters.remove(target)
                else:
                    died = False
                    target.hp -= damage
                msg = f"{username} attacked {mon_name} with {damage} damage"
                if died:
                    msg += f" and killed it"
                else:
                    msg += f", HP left: {target.hp}"
                self.broadcast(msg)
            
        elif cmd == "sayall":
            if len(parts) < 2:
                return
            message = ' '.join(parts[1:])
            self.broadcast(f"{username}: {message}")


    def process_queue(self):
        while self.running:
            try:
                username, cmd = self.cmd_queue.get(timeout=1)
            except queue.Empty:
                continue
            self.handle_command(username, cmd)

    def client_handler(self, sock, addr):
        try:
            data = sock.recv(1024).decode().strip()
            if not data.startswith('login '):
                sock.sendall(b"error: need login\n")
                sock.close()
                return
            username = data.split(maxsplit=1)[1].strip()
            with self.lock:
                if username in self.clients:
                    sock.sendall(b"login_fail\n")
                    sock.close()
                    return
                self.clients[username] = sock
                self.positions[username] = Position(0, 0)
            sock.sendall(b"login_ok\n")
            self.broadcast(f"{username} joined the game")
        except:
            sock.close()
            return

        while self.running:
            try:
                data = sock.recv(1024).decode().strip()
                if not data:
                    break
                self.cmd_queue.put((username, data))
            except:
                break

        with self.lock:
            if username in self.clients:
                del self.clients[username]
                if username in self.positions:
                    del self.positions[username]
            self.broadcast(f"{username} left the game")
        sock.close()

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        processor = threading.Thread(target=self.process_queue)
        processor.start()

        while self.running:
            try:
                sock, addr = server.accept()
                t = threading.Thread(target=self.client_handler, args=(sock, addr))
                t.start()
            except:
                break

        self.running = False
        server.close()
        processor.join()

def main():
    GameServer().run()
    
if __name__ == "__main__":
    main()