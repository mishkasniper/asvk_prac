"""
Серверный модуль MOOD MUD.

Реализует многопользовательский сервер для игры MUD (Multi-User Dungeon)
с поддержкой бродячих монстров, перемещающихся каждые 30 секунд.

Обрабатывает подключения клиентов, управляет состоянием игры (позиции игроков,
монстры), обеспечивает широковещательные сообщения о событиях (добавление
монстра, атака, перемещение монстра) и индивидуальные уведомления (встреча
с монстром).

Классы:
    GameServer: основной класс сервера, управляющий сокетами, потоками и логикой.
"""

import socket
import threading
import queue
import time
import random
from cowsay import cowsay

from ..common.position import Position
from ..common.monster import Monster
from ..common.cowsay_utils import jgsbat






class GameServer:
    """
    Сервер MUD, обрабатывающий подключения и игровую логику.

    Атрибуты:
        host (str): Адрес для прослушивания (по умолчанию 'localhost').
        port (int): Порт для прослушивания (по умолчанию 1337).
        lock (threading.Lock): Блокировка для синхронизации доступа к общим данным.
        clients (dict): Словарь {имя_пользователя: сокет}.
        positions (dict): Словарь {имя_пользователя: Position} текущих позиций игроков.
        monsters (list): Список объектов Monster, присутствующих в мире.
        cmd_queue (queue.Queue): Очередь команд от клиентов (username, команда).
        running (bool): Флаг работы сервера.
    """
    def __init__(self, host='localhost', port=1337):
        """
        Инициализирует сервер.

        Args:
            host (str): Адрес для прослушивания.
            port (int): Порт для прослушивания.
        """
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.clients = {}
        self.positions = {}
        self.monsters = []
        self.cmd_queue = queue.Queue()
        self.running = True

    def broadcast(self, message, exclude=None):
        """
        Отправляет сообщение всем подключённым клиентам.

        Args:
            message (str): Текст сообщения.
            exclude (str, optional): Имя пользователя, которому сообщение не отправляется.
        """
        for name, sock in self.clients.items():
            if name != exclude:
                try:
                    sock.sendall((message + '\n').encode())
                except:
                    pass

    def send_private(self, name, message):
        """
        Отправляет личное сообщение конкретному пользователю.

        Args:
            name (str): Имя получателя.
            message (str): Текст сообщения.
        """
        sock = self.clients.get(name)
        if sock:
            try:
                sock.sendall((message + '\n').encode())
            except:
                pass
    
    def _send_encounter(self, monster, player_name):
        """
        Отправляет игроку приветствие монстра (cowsay) при встрече.

        Args:
            monster (Monster): Объект монстра.
            player_name (str): Имя игрока.
        """
        if monster.name == 'jgsbat':
            greeting = cowsay(monster.phrase, cowfile=jgsbat)
        else:
            greeting = cowsay(monster.phrase, cow=monster.name)
        self.send_private(player_name, greeting)

    def _move_random_monster(self):
        """
        Перемещает случайного монстра на одну клетку в случайном направлении.

        Избегает столкновения с другими монстрами (повторяет выбор до успеха,
        максимум 20 попыток). При успешном перемещении рассылает уведомление всем
        игрокам. Если монстр попадает на клетку с игроком, инициирует встречу.
        """
        with self.lock:
            if not self.monsters:
                return
            for _ in range(20):
                monster = random.choice(self.monsters)
                directions = [(-1, 0, 'up'), (1, 0, 'down'), (0, -1, 'left'), (0, 1, 'right')]
                dx, dy, dir_name = random.choice(directions)
                new_x = (monster.pos.x + dx) % 10
                new_y = (monster.pos.y + dy) % 10
                occupied = any(m.pos.x == new_x and m.pos.y == new_y for m in self.monsters)
                if not occupied:
                    monster.pos.x = new_x
                    monster.pos.y = new_y
                    self.broadcast(f"{monster.name} moved one cell {dir_name}")
                    players_here = [name for name, pos in self.positions.items() if pos.x == new_x and pos.y == new_y]
                    for player in players_here:
                        self._send_encounter(monster, player)
                    return

    def handle_command(self, username, cmd_line):
        """
        Обрабатывает команду, полученную от клиента.

        Поддерживаемые команды:
            move dx dy           - перемещение игрока
            addmon name hello hp x y - добавление монстра
            attack name damage   - атака монстра
            sayall message       - широковещательное сообщение
            movemonsters on/off  - включение/выключение бродячих монстров

        Args:
            username (str): Имя пользователя.
            cmd_line (str): Строка команды.
        """
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
                        self._send_encounter(m, username)
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
        """
        Поток-обработчик очереди команд.

        Извлекает команды из очереди и передаёт их в handle_command.
        Работает в бесконечном цикле до остановки сервера.
        """
        while self.running:
            try:
                username, cmd = self.cmd_queue.get(timeout=1)
            except queue.Empty:
                continue
            self.handle_command(username, cmd)

    def client_handler(self, sock, addr):
        """
        Обработчик подключения одного клиента (выполняется в отдельном потоке).

        Выполняет аутентификацию (логин), затем принимает команды и помещает их
        в очередь. При разрыве соединения удаляет пользователя и оповещает всех.

        Args:
            sock (socket.socket): Сокет клиента.
            addr (tuple): Адрес клиента.
        """
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
        """
        Запускает основной цикл сервера.

        Создаёт сокет, принимает подключения, запускает поток обработки очереди
        и поток перемещения монстров. Останавливается при установке self.running = False.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        processor = threading.Thread(target=self.process_queue)
        processor.start()

        def wander_loop():
            while self.running:
                time.sleep(30)
                self._move_random_monster()
        
        wander_thread = threading.Thread(target=wander_loop)
        wander_thread.start()

        while self.running:
            try:
                sock, addr = server.accept()
                t = threading.Thread(target=self.client_handler, args=(sock, addr))
                t.start()
            except:
                break

        self.running = False
        server.close()
        wander_thread.join()
        processor.join()

