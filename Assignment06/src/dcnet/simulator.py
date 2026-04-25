from __future__ import annotations

from dataclasses import dataclass, field

from .config import SimConfig
from .metrics import SimulationReport, build_report
from .model import Flow, Packet
from .routing import RoutePlanner
from .topology import Topology


@dataclass(slots=True)
class Simulator:
    topology: Topology
    cfg: SimConfig
    flows: list[Flow]
    route_planner: RoutePlanner = field(init=False)
    current_tick: int = 0
    next_packet_id: int = 0
    total_packets_created: int = 0

    def __post_init__(self) -> None:
        self.route_planner = RoutePlanner(self.topology)

    def run(self) -> SimulationReport:
        for tick in range(self.cfg.ticks):
            self.current_tick = tick
            self._record_queue_samples()
            self._inject_new_packets()
            self._service_links()
            self._update_completed_flows()
        return build_report(self.flows, list(self.topology.links.values()), self.total_packets_created, self.cfg.ticks)

    def _record_queue_samples(self) -> None:
        for link in self.topology.links.values():
            link.record_queue_sample()

    def _inject_new_packets(self) -> None:
        for flow in self.flows:
            if flow.start_tick > self.current_tick:
                continue
            if flow.packets_created >= flow.size_packets:
                continue

            packet = Packet(
                packet_id=self.next_packet_id,
                flow_id=flow.flow_id,
                src=flow.src,
                dst=flow.dst,
                created_tick=self.current_tick,
                current_node=flow.src,
            )
            self.next_packet_id += 1
            self.total_packets_created += 1
            flow.packets_created += 1

            next_hop = self.route_planner.next_hop(packet.current_node, packet.src, packet.dst, packet.flow_id)
            if next_hop is None:
                continue

            link = self.topology.links[(packet.current_node, next_hop)]
            enqueued = link.enqueue(packet)
            if not enqueued:
                self.flows[packet.flow_id].packets_dropped += 1

    def _service_links(self) -> None:
        arrivals: list[tuple[Packet, str]] = []

        for link in self.topology.links.values():
            packets_to_send = min(link.capacity_packets_per_tick, len(link.queue))
            for _ in range(packets_to_send):
                packet = link.queue.popleft()
                link.transmitted_packets += 1
                arrivals.append((packet, link.dst))

        for packet, node_id in arrivals:
            packet.current_node = node_id
            if node_id == packet.dst:
                packet.delivered_tick = self.current_tick
                flow = self.flows[packet.flow_id]
                flow.packets_delivered += 1
                continue

            next_hop = self.route_planner.next_hop(node_id, packet.src, packet.dst, packet.flow_id)
            if next_hop is None:
                continue

            next_link = self.topology.links[(node_id, next_hop)]
            enqueued = next_link.enqueue(packet)
            if not enqueued:
                self.flows[packet.flow_id].packets_dropped += 1

    def _update_completed_flows(self) -> None:
        for flow in self.flows:
            if flow.completion_tick is None and flow.is_complete:
                flow.completion_tick = self.current_tick
