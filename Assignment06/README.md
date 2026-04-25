# Data Center Networking Simulator

This project simulates congestion, incast, ECMP imbalance, and queueing behavior in a simplified leaf-spine data center network.

## Features

- Leaf-spine topology with configurable:
  - number of leaf switches
  - servers per leaf
  - number of spine switches
  - link bandwidth
  - queue capacity
- Three workload generators:
  - uniform random traffic
  - incast traffic
  - hotspot traffic
- Stable ECMP-style path selection for inter-rack flows
- Per-link finite output queues
- Packet drops on buffer overflow
- Discrete-time simulation
- Metrics for:
  - total packets sent, delivered, and dropped
  - average and maximum flow completion time
  - average and maximum queue length
  - per-link utilization

## Project structure

```text
src/
  dcnet/
    cli.py
    config.py
    metrics.py
    model.py
    routing.py
    simulator.py
    topology.py
    workloads.py
tests/
  test_topology.py
  test_workloads.py
```

## How routing works

- If source and destination are in the same rack, traffic stays within one leaf switch.
- If source and destination are in different racks, traffic goes:
  - source server -> source leaf -> chosen spine -> destination leaf -> destination server
- ECMP is modeled by hashing `(src, dst, flow_id)` to one spine switch and keeping that path fixed for the life of the flow.

## How the queue model works

- Each directed link has a finite-capacity output queue.
- Each tick, a link transmits up to its configured bandwidth in packets.
- Packets move one hop per tick.
- If a packet arrives at a full queue, it is dropped.

## Running the simulator

From the project root:

```bash
python -m src.dcnet.cli --workload uniform --ticks 100
python -m src.dcnet.cli --workload incast --ticks 100
python -m src.dcnet.cli --workload hotspot --ticks 100
```

Optional parameters:

```bash
python -m src.dcnet.cli --workload incast --ticks 150 --leafs 8 --servers-per-leaf 8 --spines 4 --bandwidth 4 --queue-capacity 32
```

## Running tests

```bash
pytest -q
```

## Suggested report experiments

1. Increase the number of simultaneous senders in an incast workload and compare flow completion time and drops.
2. Use uniform traffic and inspect the per-link utilization values to evaluate ECMP balance.
3. Show that some equal-cost paths still become overloaded under hashing.
4. Increase queue capacity and compare drops versus delay.
5. Increase hotspot concentration and compare throughput, queue growth, and loss.

## Sample interpretation

- Incast increases contention at the destination leaf and server-facing links.
- ECMP helps distribute inter-rack traffic, but hash-based assignment is not perfectly even.
- Larger queues can reduce packet loss, but often increase queueing delay and tail completion time.
- More concentrated hotspot traffic pushes a few destination-facing links into sustained overload.

## Notes

This model intentionally stays simple enough to connect directly to the assignment concepts. It does not implement full TCP congestion control, retransmissions, or variable packet sizes.
