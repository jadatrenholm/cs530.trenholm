from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Deque, Optional


class NodeKind(Enum):
    SERVER = auto()
    LEAF = auto()
    SPINE = auto()


@dataclass(slots=True, frozen=True)
class Node:
    node_id: str
    kind: NodeKind


@dataclass(slots=True)
class Packet:
    packet_id: int
    flow_id: int
    src: str
    dst: str
    created_tick: int
    current_node: str
    delivered_tick: Optional[int] = None


@dataclass(slots=True)
class Flow:
    flow_id: int
    src: str
    dst: str
    size_packets: int
    start_tick: int
    packets_created: int = 0
    packets_delivered: int = 0
    packets_dropped: int = 0
    completion_tick: Optional[int] = None

    @property
    def is_complete(self) -> bool:
        return self.packets_delivered >= self.size_packets

    @property
    def is_finished(self) -> bool:
        return (self.packets_delivered + self.packets_dropped) >= self.size_packets


@dataclass(slots=True)
class Link:
    src: str
    dst: str
    capacity_packets_per_tick: int
    queue_capacity_packets: int
    queue: Deque[Packet] = field(default_factory=deque)
    transmitted_packets: int = 0
    dropped_packets: int = 0
    queue_length_sum: int = 0
    queue_length_samples: int = 0
    max_queue_length: int = 0

    def enqueue(self, packet: Packet) -> bool:
        if len(self.queue) >= self.queue_capacity_packets:
            self.dropped_packets += 1
            return False
        self.queue.append(packet)
        if len(self.queue) > self.max_queue_length:
            self.max_queue_length = len(self.queue)
        return True

    def record_queue_sample(self) -> None:
        qlen = len(self.queue)
        self.queue_length_sum += qlen
        self.queue_length_samples += 1
        if qlen > self.max_queue_length:
            self.max_queue_length = qlen

    @property
    def average_queue_length(self) -> float:
        if self.queue_length_samples == 0:
            return 0.0
        return self.queue_length_sum / self.queue_length_samples
