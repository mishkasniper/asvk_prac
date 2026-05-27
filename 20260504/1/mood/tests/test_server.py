import socket
import time
import subprocess
import sys
import pytest

HOST = 'localhost'
PORT = 1337


def is_port_open(host, port, timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False


@pytest.fixture(scope="module")
def server_process():
    proc = subprocess.Popen(
        [sys.executable, '-m', 'mood.server'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(10):
        if is_port_open(HOST, PORT):
            break
        time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError("Сервер не запустился")
    yield proc
    proc.terminate()
    proc.wait()


def connect_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    sock.connect((HOST, PORT))
    username = f"tester_{int(time.time())}"
    sock.sendall(f"login {username}\n".encode())
    data = b''
    while b'\n' not in data:
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    resp = data.decode().strip()
    if resp != "login_ok":
        raise Exception(f"Login failed: {resp}")
    return sock, username


def send_only(sock, cmd):
    sock.sendall((cmd + '\n').encode())


def read_responses(sock, timeout=0.3):
    sock.settimeout(timeout)
    responses = []
    while True:
        try:
            data = sock.recv(4096).decode().strip()
            if data:
                responses.append(data)
        except socket.timeout:
            break
    sock.settimeout(None)
    return responses


def test_addmon_and_move_and_attack(server_process):
    sock, username = connect_client()
    try:
        send_only(sock, "movemonsters off")
        time.sleep(0.3)
        read_responses(sock, 0.2)

        addmon_cmd = "addmon dragon I am dragon 30 3 4"
        send_only(sock, addmon_cmd)
        time.sleep(0.5)
        responses = read_responses(sock, 0.3)
        assert any("added monster dragon" in r and "30 HP" in r for r in responses), \
            f"Не найдено сообщение о добавлении монстра: {responses}"

        for _ in range(4):
            send_only(sock, "move 0 1")
            time.sleep(0.2)
        for _ in range(3):
            send_only(sock, "move 1 0")
            time.sleep(0.2)

        time.sleep(0.5)
        all_responses = read_responses(sock, 0.5)
        greeting_text = "\n".join(all_responses)
        assert "I am dragon" in greeting_text, f"Приветствие монстра не получено: {greeting_text}"

        # 3. Атака
        send_only(sock, "attack dragon 10")
        time.sleep(0.5)
        attack_resp = read_responses(sock, 0.5)
        assert any(["attacked dragon" in r and "10 damage" in r for r in attack_resp])
        assert any(["HP left: 20" in r for r in attack_resp])

        send_only(sock, "attack dragon 10")
        time.sleep(0.3)
        send_only(sock, "attack dragon 10")
        time.sleep(0.5)
        final_resp = read_responses(sock, 0.3)
        assert any(["and killed it" in r for r in final_resp]), "Монстр не умер после трёх атак"

    finally:
        sock.close()
