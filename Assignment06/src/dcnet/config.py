from dataclasses import dataclass


@dataclass(slots=True)
class SimConfig:
    num_leaf_switches: int = 8
    servers_per_leaf: int = 8
    num_spine_switches: int = 4
    link_bandwidth_packets_per_tick: int = 4
    queue_capacity_packets: int = 32
    default_flow_size_packets: int = 20
    ticks: int = 100
    random_seed: int = 7
