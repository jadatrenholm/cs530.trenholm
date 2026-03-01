#!/usr/bin/env python3
import argparse
import socket
import random
import time
from datetime import datetime

def log_line(path: str, line: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def send_control_message(server_host: str, server_port: int, msg: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3.0)
        s.connect((server_host, server_port))
        s.sendall(msg.encode("utf-8"))
        try:
            _ = s.recv(64)
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="Assignment03 TCP Client")
    parser.add_argument("--server-host", default="127.0.0.1", help="Server host/IP")
    parser.add_argument("--server-port", type=int, default=5000, help="Server port for register/unregister")
    parser.add_argument("--listen-host", default="127.0.0.1", help="Client bind interface (default localhost)")
    parser.add_argument("--listen-port", type=int, default=5001, help="Client listen port for timestamps")
    parser.add_argument("--id", type=int, required=True, help="Client identifier integer")
    parser.add_argument("--out", default=None, help="Client output file (default client_<id>.txt)")
    args = parser.parse_args()

    out_file = args.out or f"client_{args.id}.txt"

    send_control_message(args.server_host, args.server_port, f"R {args.id}\n")
    log_line(out_file, f"REGISTER_SENT id={args.id} to {args.server_host}:{args.server_port}")

    lifetime = random.randint(15, 90)
    end_time = time.time() + lifetime

    backoff = 0.25
    backoff_max = 4.0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_sock:
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind((args.listen_host, args.listen_port))
        listen_sock.listen()

        while time.time() < end_time:
            remaining = end_time - time.time()
            timeout = min(backoff, max(0.05, remaining))
            listen_sock.settimeout(timeout)

            try:
                conn, addr = listen_sock.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        msg = data.decode("utf-8", errors="replace").strip()
                        log_line(out_file, f"RECV from {addr[0]}:{addr[1]} -> {msg}")
                        backoff = 0.25
            except socket.timeout:
                backoff = min(backoff * 2.0, backoff_max)
            except Exception as e:
                log_line(out_file, f"ERROR listen err={e}")
                backoff = min(backoff * 2.0, backoff_max)

    send_control_message(args.server_host, args.server_port, f"U {args.id}\n")
    log_line(out_file, f"UNREGISTER_SENT id={args.id} after lifetime={lifetime}s")

if __name__ == "__main__":
    main()