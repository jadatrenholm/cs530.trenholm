from __future__ import annotations

from dataclasses import dataclass, field

from .model import Flow, Link


@dataclass(slots=True)
class LinkUtilization:
    src: str
    dst: str
    utilization: float
    transmitted_packets: int
    average_queue_length: float
    maximum_queue_length: int
    dropped_packets: int


@dataclass(slots=True)
class SimulationReport:
    total_packets_created: int
    total_packets_delivered: int
    total_packets_dropped: int
    completed_flows: int
    average_flow_completion_time: float
    max_flow_completion_time: int
    average_queue_length: float
    maximum_queue_length: int
    per_link_utilization: list[LinkUtilization] = field(default_factory=list)


def build_report(flows: list[Flow], links: list[Link], total_packets_created: int, ticks: int) -> SimulationReport:
    total_packets_delivered = sum(flow.packets_delivered for flow in flows)
    total_packets_dropped = sum(link.dropped_packets for link in links)

    completion_times: list[int] = []
    for flow in flows:
        if flow.completion_tick is not None:
            completion_times.append(flow.completion_tick - flow.start_tick + 1)

    avg_completion = 0.0
    max_completion = 0
    if completion_times:
        avg_completion = sum(completion_times) / len(completion_times)
        max_completion = max(completion_times)

    avg_queue = 0.0
    max_queue = 0
    if links:
        avg_queue = sum(link.average_queue_length for link in links) / len(links)
        max_queue = max(link.max_queue_length for link in links)

    per_link: list[LinkUtilization] = []
    for link in links:
        denom = max(1, ticks * link.capacity_packets_per_tick)
        per_link.append(
            LinkUtilization(
                src=link.src,
                dst=link.dst,
                utilization=link.transmitted_packets / denom,
                transmitted_packets=link.transmitted_packets,
                average_queue_length=link.average_queue_length,
                maximum_queue_length=link.max_queue_length,
                dropped_packets=link.dropped_packets,
            )
        )

    per_link.sort(key=lambda x: (x.utilization, x.transmitted_packets), reverse=True)

    return SimulationReport(
        total_packets_created=total_packets_created,
        total_packets_delivered=total_packets_delivered,
        total_packets_dropped=total_packets_dropped,
        completed_flows=sum(1 for flow in flows if flow.is_complete),
        average_flow_completion_time=avg_completion,
        max_flow_completion_time=max_completion,
        average_queue_length=avg_queue,
        maximum_queue_length=max_queue,
        per_link_utilization=per_link,
    )
