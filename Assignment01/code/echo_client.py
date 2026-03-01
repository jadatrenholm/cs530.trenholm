# echo_client.py
import socket
from time import perf_counter_ns

HOST = '127.0.0.1'   # Change if server is on another machine
PORT = 12345
NUM_TRIALS = 20

round_trip_times_ms = []

print(f"Running {NUM_TRIALS} echo trials...\n")

for trial in range(1, NUM_TRIALS + 1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        message = f"Echo test {trial}".encode()

        start_time = perf_counter_ns()
        s.sendall(message)
        data = s.recv(1024)
        end_time = perf_counter_ns()

        rtt_ms = (end_time - start_time) / 1_000_000
        round_trip_times_ms.append(rtt_ms)

        print(f"Trial {trial:02d}: {rtt_ms:.3f} ms")

average_rtt = sum(round_trip_times_ms) / NUM_TRIALS

print("\n----------------------------------")
print(f"Average round-trip time: {average_rtt:.3f} ms")
print("----------------------------------")