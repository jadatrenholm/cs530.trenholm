from __future__ import annotations

import random
from typing import Iterable

from .config import SimConfig
from .model import Flow
from .topology import Topology



def all_servers(topology: Topology) -> list[str]:
    return list(topology.server_to_leaf.keys())



def make_uniform_random_workload(
    topology: Topology,
    cfg: SimConfig,
    num_flows: int = 20,
) -> list[Flow]:
    rng = random.Random(cfg.random_seed)
    servers = all_servers(topology)
    flows: list[Flow] = []

    for flow_id in range(num_flows):
        src = rng.choice(servers)
        dst = rng.choice(servers)
        while dst == src:
            dst = rng.choice(servers)
        flows.append(
            Flow(
                flow_id=flow_id,
                src=src,
                dst=dst,
                size_packets=cfg.default_flow_size_packets,
                start_tick=rng.randint(0, 5),
            )
        )
    return flows



def make_incast_workload(
    topology: Topology,
    cfg: SimConfig,
    num_senders: int = 12,
    start_tick: int = 0,
) -> list[Flow]:
    rng = random.Random(cfg.random_seed)
    servers = all_servers(topology)
    receiver = rng.choice(servers)
    senders = [server for server in servers if server != receiver]
    rng.shuffle(senders)
    senders = senders[:num_senders]

    flows: list[Flow] = []
    for flow_id, sender in enumerate(senders):
        flows.append(
            Flow(
                flow_id=flow_id,
                src=sender,
                dst=receiver,
                size_packets=cfg.default_flow_size_packets,
                start_tick=start_tick,
            )
        )
    return flows



def make_hotspot_workload(
    topology: Topology,
    cfg: SimConfig,
    num_flows: int = 24,
    hotspot_fraction: float = 0.7,
    num_hot_receivers: int = 2,
) -> list[Flow]:
    rng = random.Random(cfg.random_seed)
    servers = all_servers(topology)
    hot_receivers = rng.sample(servers, k=min(num_hot_receivers, len(servers)))

    flows: list[Flow] = []
    for flow_id in range(num_flows):
        src = rng.choice(servers)
        if rng.random() < hotspot_fraction:
            dst = rng.choice(hot_receivers)
        else:
            dst = rng.choice(servers)
        while dst == src:
            dst = rng.choice(servers)
        flows.append(
            Flow(
                flow_id=flow_id,
                src=src,
                dst=dst,
                size_packets=cfg.default_flow_size_packets,
                start_tick=rng.randint(0, 5),
            )
        )
    return flows



def workload_by_name(name: str, topology: Topology, cfg: SimConfig) -> list[Flow]:
    normalized = name.strip().lower()
    if normalized == "uniform":
        return make_uniform_random_workload(topology, cfg)
    if normalized == "incast":
        return make_incast_workload(topology, cfg)
    if normalized == "hotspot":
        return make_hotspot_workload(topology, cfg)
    raise ValueError(f"Unknown workload name: {name!r}")
