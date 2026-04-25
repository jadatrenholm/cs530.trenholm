from __future__ import annotations

import hashlib

from .topology import Topology


class RoutePlanner:
    """Computes stable next hops for packets in a leaf-spine topology."""

    def __init__(self, topology: Topology) -> None:
        self.topology = topology
        self.flow_to_spine: dict[int, str] = {}

    def _stable_hash(self, value: str) -> int:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return int(digest[:16], 16)

    def _choose_spine_for_flow(self, flow_id: int, src: str, dst: str) -> str:
        if flow_id not in self.flow_to_spine:
            spine_list = self.topology.spine_switches
            key = f"{src}|{dst}|{flow_id}"
            idx = self._stable_hash(key) % len(spine_list)
            self.flow_to_spine[flow_id] = spine_list[idx]
        return self.flow_to_spine[flow_id]

    def next_hop(self, current_node: str, src: str, dst: str, flow_id: int) -> str | None:
        src_leaf = self.topology.server_to_leaf[src]
        dst_leaf = self.topology.server_to_leaf[dst]

        if current_node == src:
            return src_leaf

        if current_node == src_leaf:
            if src_leaf == dst_leaf:
                return dst
            return self._choose_spine_for_flow(flow_id, src, dst)

        if current_node in self.topology.spine_switches:
            return dst_leaf

        if current_node == dst_leaf:
            return dst

        if current_node == dst:
            return None

        raise ValueError(f"No routing rule for packet at node {current_node!r}")
