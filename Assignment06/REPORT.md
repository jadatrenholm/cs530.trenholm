# Simulating Incast, ECMP Imbalance, and Queueing in a Leaf-Spine Data Center

## Student Report

## 1. Overview

This project models a simplified leaf-spine data center using discrete time simulation. The simulator includes servers, leaf switches, spine switches, fixed-bandwidth links, finite output queues, and stable ECMP-style routing for inter-rack traffic. The goal is to observe how different application traffic patterns affect congestion, queue growth, packet loss, throughput, and flow completion time.

The simulator supports three workloads:

- Uniform random traffic: each flow chooses a random destination.
- Incast traffic: many senders transmit simultaneously to one receiver.
- Hotspot traffic: a large fraction of flows target a small set of receivers.

## 2. Topology and Simulation Model

Default configuration used for the main experiments:

- 8 leaf switches
- 8 servers per leaf
- 4 spine switches
- Link bandwidth: 4 packets per tick
- Queue capacity: 32 packets per output port
- Default flow size: 20 packets

Routing rules:

- Same-rack traffic stays within the source leaf.
- Cross-rack traffic follows: source server -> source leaf -> spine -> destination leaf -> destination server.
- ECMP is approximated by hashing (src, dst, flow_id) to one spine and keeping that path fixed for the life of the flow.

Queueing rules:

- Every directed link has its own finite output queue.
- Each tick, a link can transmit up to its service rate.
- Packets move one hop per tick.
- Packets are dropped if the next output queue is already full.

## 3. Metrics Collected

The simulator reports:

- Total packets created
- Total packets delivered
- Total packets dropped
- Average flow completion time
- Maximum flow completion time
- Average queue length
- Maximum queue length
- Per-link utilization

## 4. Experiment Results

### 4.1 Incast sender sweep

This experiment increases the number of simultaneous senders targeting one receiver.

| Senders | Avg flow completion time | Max flow completion time | Packets dropped | Avg queue length | Max queue length |
|---|---:|---:|---:|---:|---:|
| 2 | 23.0 | 23 | 0 | 0.00 | 2 |
| 4 | 23.0 | 23 | 0 | 0.01 | 4 |
| 8 | 30.0 | 30 | 52 | 0.04 | 32 |
| 12 | 29.0 | 30 | 108 | 0.06 | 32 |
| 16 | 29.0 | 30 | 180 | 0.07 | 32 |
| 24 | 28.0 | 28 | 338 | 0.10 | 32 |
| 32 | 28.0 | 28 | 496 | 0.14 | 32 |

Observation: once the number of senders exceeds the service capacity of the destination-side path, the queue fills rapidly and packet loss rises sharply. At 8 senders and above, the queue repeatedly reaches the 32-packet limit. Flow completion time also increases because packets spend more time waiting in queues before delivery.

### 4.2 ECMP balance under uniform traffic

Uniform traffic improves overall distribution, but the load is still not perfectly balanced.

Uniform workload summary (64 flows):

- Average leaf-to-spine utilization: 0.077
- Maximum leaf-to-spine utilization: 0.244
- Minimum leaf-to-spine utilization: 0.000
- Total drops: 23
- Average queue length: 0.179
- Maximum queue length: 32

Top utilized leaf-to-spine links:

| Link | Utilization | Packets transmitted |
|---|---:|---:|
| leaf1 -> spine1 | 0.244 | 117 |
| leaf0 -> spine2 | 0.167 | 80 |
| leaf3 -> spine0 | 0.167 | 80 |
| leaf2 -> spine0 | 0.125 | 60 |
| leaf4 -> spine2 | 0.125 | 60 |
| leaf6 -> spine2 | 0.125 | 60 |
| leaf7 -> spine3 | 0.125 | 60 |
| leaf0 -> spine0 | 0.083 | 40 |

Observation: ECMP spreads flows across spines, but some links still carry substantially more traffic than others. Hash-based path selection operates at the flow level, not the packet level, so it can easily map several large flows onto the same path while other equal-cost paths remain lightly used.

### 4.3 Queue capacity sweep

This experiment uses a 16-sender incast while increasing queue size.

| Queue capacity | Packets delivered | Packets dropped | Avg flow completion time | Max flow completion time | Avg queue length | Max queue length |
|---|---:|---:|---:|---:|---:|---:|
| 8 | 92 | 228 | 23.0 | 24 | 0.03 | 8 |
| 16 | 108 | 212 | 25.0 | 26 | 0.04 | 16 |
| 32 | 140 | 180 | 29.0 | 30 | 0.06 | 32 |
| 64 | 184 | 136 | 37.0 | 38 | 0.11 | 64 |
| 128 | 248 | 72 | 53.0 | 54 | 0.20 | 128 |

Observation: larger queues reduce drops because they absorb more burst traffic, but delay increases significantly. This is a classic drop-versus-delay tradeoff. The 128-packet queue delivers many more packets than the 8-packet queue, but it also more than doubles the average completion time.

### 4.4 Hotspot concentration sweep

This experiment varies the fraction of flows sent to a small hot set of receivers.

| Hotspot fraction | Packets delivered | Packets dropped | Avg flow completion time | Max flow completion time | Avg queue length | Max queue length |
|---|---:|---:|---:|---:|---:|---:|
| 0.30 | 1095 | 185 | 23.75 | 30 | 0.20 | 32 |
| 0.50 | 859 | 421 | 24.76 | 30 | 0.27 | 32 |
| 0.70 | 658 | 622 | 25.62 | 30 | 0.31 | 32 |
| 0.85 | 536 | 744 | 26.00 | 30 | 0.32 | 32 |
| 0.95 | 433 | 847 | 26.20 | 30 | 0.33 | 32 |

Observation: as traffic becomes more concentrated, delivery decreases, losses rise, and queue occupancy grows. Even in a richly connected topology, traffic aimed at a small number of endpoints creates bottlenecks on the final links feeding those receivers.

## 5. Answers to Required Questions

### Why does a leaf-spine topology help with bisection bandwidth?

A leaf-spine topology gives each leaf multiple parallel paths into the fabric through the spine layer. This increases the amount of bandwidth available between one half of the data center and the other half because traffic can use many simultaneous equal-cost paths instead of depending on a small number of aggregation bottlenecks. In practice, this improves east-west traffic capacity compared with a traditional hierarchical tree.

### Why can incast still occur even in a highly connected fabric?

Incast happens when many senders target one receiver at nearly the same time. Even if the core of the network has many parallel paths, all of that traffic must eventually converge on the destination leaf and then the final server-facing link. That last part of the path is shared, so bursts from many senders can overflow queues there.

### Why does ECMP not guarantee perfect load balance?

ECMP balances at the granularity of flows, not individual packets. A hash can assign multiple high-volume flows to the same path while leaving other equal-cost paths less used. Because the mapping depends on the flow keys and not on current congestion, ECMP can create imbalance even when many equivalent routes exist.

### Why is tail latency often more important than average latency?

Applications such as search, analytics, and distributed storage often wait for the slowest response among many parallel requests. Averages can look acceptable while a small set of delayed packets or flows causes the whole application to stall. Tail latency captures these worst-case delays, which are often what users and distributed applications actually feel.

### How do application communication patterns shape network behavior?

The network does not become congested randomly; it becomes congested because applications generate specific communication patterns. Uniform traffic tends to spread load more evenly. Incast causes synchronized bursts toward one receiver. Hotspot traffic concentrates demand on a few destinations. These patterns directly determine where queues build, which links become overloaded, how often packets are dropped, and how long flows take to finish.

## 6. Conclusion

The simulation shows that a leaf-spine topology improves path diversity and aggregate bandwidth, but it does not eliminate congestion. Incast and hotspot workloads still create sharp bottlenecks at destination-side links, while ECMP can leave some equal-cost paths much busier than others. Increasing queue size can reduce loss, but it also increases delay and tail completion time. Overall, the experiments show that network performance is shaped not only by topology, but also by workload structure and transport behavior.
