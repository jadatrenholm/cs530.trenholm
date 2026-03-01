#!/usr/bin/env python3
import argparse
import socket
import threading
import time
import random
from datetime import datetime

registry = {}
registry_lock = threading.Lock()

def log_line(path: str, line: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def handle_client(conn: socket.socket, addr, server_log: str):
    ip, _port = addr
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = data.decode("utf-8", errors="replace").strip()
        parts = msg.split()

        if len(parts) != 2 or parts[0] not in ("R", "U"):
            log_line(server_log, f"BAD_MSG from {ip}: {msg!r}")
            return

        op, cid_str = parts
        try:
            cid = int(cid_str)
        except ValueError:
            log_line(server_log, f"BAD_ID from {ip}: {msg!r}")
            return

        with registry_lock:
            if op == "R":
                registry[cid] = (ip, time.time())
                log_line(server_log, f"REGISTER client={cid} ip={ip}")
            else:
                existed = cid in registry
                registry.pop(cid, None)
                log_line(server_log, f"UNREGISTER client={cid} ip={ip} existed={existed}")

        conn.sendall(b"OK\n")
    except Exception as e:
        log_line(server_log, f"ERROR handle_client {ip}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def broadcast_loop(server_log: str, client_port: int):
    while True:
        delay = random.randint(5, 30)
        time.sleep(delay)

        timestamp = datetime.now().isoformat(timespec="seconds")
        message = f"TS {timestamp}\n".encode("utf-8")

        with registry_lock:
            items = list(registry.items())

        for cid, (ip, _last_seen) in items:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2.0)
                    s.connect((ip, client_port))
                    s.sendall(message)
                log_line(server_log, f"SENT to client={cid} ip={ip} msg={message.decode().strip()}")
            except Exception as e:
                log_line(server_log, f"FAIL_SEND client={cid} ip={ip} err={e}")

def main():
    parser = argparse.ArgumentParser(description="Assignment03 TCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default localhost)")
    parser.add_argument("--port", type=int, default=5000, help="Server listen port (register/unregister)")
    parser.add_argument("--client-port", type=int, default=5001, help="Port clients listen on for timestamps")
    parser.add_argument("--log", default="server.log", help="Server log file")
    args = parser.parse_args()

    t = threading.Thread(target=broadcast_loop, args=(args.log, args.client_port), daemon=True)
    t.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((args.host, args.port))
        server_sock.listen()
        log_line(args.log, f"SERVER_START host={args.host} port={args.port} client_port={args.client_port}")

        while True:
            conn, addr = server_sock.accept()
            th = threading.Thread(target=handle_client, args=(conn, addr, args.log), daemon=True)
            th.start()

if __name__ == "__main__":
    main()