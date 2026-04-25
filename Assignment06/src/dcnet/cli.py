from __future__ import annotations

import argparse

from .config import SimConfig
from .simulator import Simulator
from .topology import build_leaf_spine_topology
from .workloads import workload_by_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Leaf-spine data center simulator")
    parser.add_argument("--workload", choices=["uniform", "incast", "hotspot"], default="uniform")
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--leafs", type=int, default=8)
    parser.add_argument("--servers-per-leaf", type=int, default=8)
    parser.add_argument("--spines", type=int, default=4)
    parser.add_argument("--bandwidth", type=int, default=4)
    parser.add_argument("--queue-capacity", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = SimConfig(
        num_leaf_switches=args.leafs,
        servers_per_leaf=args.servers_per_leaf,
        num_spine_switches=args.spines,
        link_bandwidth_packets_per_tick=args.bandwidth,
        queue_capacity_packets=args.queue_capacity,
        ticks=args.ticks,
    )

    topology = build_leaf_spine_topology(cfg)
    flows = workload_by_name(args.workload, topology, cfg)
    simulator = Simulator(topology=topology, cfg=cfg, flows=flows)
    report = simulator.run()

    print("=== Simulation Report ===")
    print(f"workload: {args.workload}")
    print(f"packets created:        {report.total_packets_created}")
    print(f"packets delivered:      {report.total_packets_delivered}")
    print(f"packets dropped:        {report.total_packets_dropped}")
    print(f"completed flows:        {report.completed_flows}/{len(flows)}")
    print(f"avg flow c.t.:          {report.average_flow_completion_time:.2f}")
    print(f"max flow c.t.:          {report.max_flow_completion_time}")
    print(f"avg queue length:       {report.average_queue_length:.2f}")
    print(f"max queue length:       {report.maximum_queue_length}")
    print("top 10 utilized links:")
    for item in report.per_link_utilization[:10]:
        print(
            f"  {item.src:>10} -> {item.dst:<10} util={item.utilization:.3f} "
            f"tx={item.transmitted_packets} avg_q={item.average_queue_length:.2f} "
            f"max_q={item.maximum_queue_length} drops={item.dropped_packets}"
        )


if __name__ == "__main__":
    main()
