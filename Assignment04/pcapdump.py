#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple

from scapy.all import PcapReader
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6

NH_HOP_BY_HOP = 0
NH_TCP = 6
NH_UDP = 17
NH_ROUTING = 43
NH_FRAGMENT = 44
NH_AH = 51
NH_ESP = 50
NH_ICMPV6 = 58
NH_NO_NEXT = 59
NH_DEST_OPTS = 60

EXTENSION_HEADERS = {
    NH_HOP_BY_HOP: "Hop-by-Hop Options",
    NH_ROUTING: "Routing",
    NH_FRAGMENT: "Fragment",
    NH_DEST_OPTS: "Destination Options",
    NH_AH: "AH",
    NH_ESP: "ESP",
}

UPPER_PROTOCOLS = {
    NH_TCP: "TCP",
    NH_UDP: "UDP",
    NH_ICMPV6: "ICMPv6",
    NH_NO_NEXT: "No Next Header",
}

IPV4_PROTOCOLS = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}


@dataclass
class IPv4Decoded:
    version: int
    ihl: int
    total_length: int
    identification: int
    flags_df: bool
    flags_mf: bool
    frag_offset: int
    ttl: int
    protocol_num: int
    protocol_name: str
    checksum: int
    src: str
    dst: str
    header_bytes: int


@dataclass
class IPv6Decoded:
    version: int
    traffic_class: int
    flow_label: int
    payload_length: int
    next_header: int
    hop_limit: int
    src: str
    dst: str
    extension_chain: List[Tuple[int, str]]
    upper_proto_name: str
    header_bytes_observed: int


def decode_ipv4(ip: IP) -> IPv4Decoded:
    df = bool(int(ip.flags) & 0x2)
    mf = bool(int(ip.flags) & 0x1)

    ihl = int(ip.ihl) if ip.ihl is not None else 0
    header_bytes = ihl * 4 if ihl else 0

    proto_num = int(ip.proto)
    proto_name = IPV4_PROTOCOLS.get(proto_num, f"OTHER({proto_num})")

    return IPv4Decoded(
        version=int(ip.version),
        ihl=ihl,
        total_length=int(ip.len) if ip.len is not None else -1,
        identification=int(ip.id) if ip.id is not None else -1,
        flags_df=df,
        flags_mf=mf,
        frag_offset=int(ip.frag) if ip.frag is not None else -1,
        ttl=int(ip.ttl) if ip.ttl is not None else -1,
        protocol_num=proto_num,
        protocol_name=proto_name,
        checksum=int(ip.chksum) if ip.chksum is not None else -1,
        src=str(ip.src),
        dst=str(ip.dst),
        header_bytes=header_bytes,
    )


def parse_ipv6_extension_chain(pkt) -> Tuple[List[Tuple[int, str]], str, int]:
    chain: List[Tuple[int, str]] = []
    ext_bytes = 0

    if not pkt.haslayer(IPv6):
        return chain, "UNKNOWN", 0

    ip6 = pkt.getlayer(IPv6)
    nh = int(ip6.nh)

    layer = ip6.payload
    safety = 0
    while safety < 20:
        safety += 1

        if nh in EXTENSION_HEADERS:
            chain.append((nh, EXTENSION_HEADERS[nh]))
            try:
                ext_len = len(bytes(layer))
                if 0 < ext_len < 512:
                    ext_bytes += ext_len
            except Exception:
                pass

            if hasattr(layer, "nh"):
                nh = int(layer.nh)
                layer = layer.payload
                continue
            break

        if nh in UPPER_PROTOCOLS:
            return chain, UPPER_PROTOCOLS[nh], ext_bytes

        if layer is None:
            break

        if layer.name == "TCP":
            return chain, "TCP", ext_bytes
        if layer.name == "UDP":
            return chain, "UDP", ext_bytes
        if "ICMPv6" in layer.name:
            return chain, "ICMPv6", ext_bytes

        if hasattr(layer, "nh"):
            nh = int(layer.nh)
            layer = layer.payload
        else:
            break

    return chain, f"OTHER({nh})", ext_bytes


def decode_ipv6(pkt) -> IPv6Decoded:
    ip6: IPv6 = pkt.getlayer(IPv6)
    chain, upper_name, ext_bytes = parse_ipv6_extension_chain(pkt)
    header_bytes_observed = 40 + ext_bytes

    return IPv6Decoded(
        version=int(ip6.version),
        traffic_class=int(ip6.tc),
        flow_label=int(ip6.fl),
        payload_length=int(ip6.plen),
        next_header=int(ip6.nh),
        hop_limit=int(ip6.hlim),
        src=str(ip6.src),
        dst=str(ip6.dst),
        extension_chain=chain,
        upper_proto_name=upper_name,
        header_bytes_observed=header_bytes_observed,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="pcapdump: Summarize IPv4 vs IPv6 traffic and print decoded headers.")
    parser.add_argument("pcap", help="Path to a .pcap file")
    parser.add_argument("--max-log", type=int, default=50, help="Max packets to print in decoded log (default: 50)")
    args = parser.parse_args()

    counts = Counter()
    ttl_dist = Counter()
    hlim_dist = Counter()
    proto_dist = Counter()
    header_sizes = Counter()
    decoded_logs: List[str] = []

    total_packets = 0
    with PcapReader(args.pcap) as pr:
        for pkt in pr:
            total_packets += 1

            if pkt.haslayer(IP):
                counts["IPv4"] += 1
                ip = pkt.getlayer(IP)
                d = decode_ipv4(ip)
                ttl_dist[d.ttl] += 1
                header_sizes[d.header_bytes] += 1
                proto_dist[d.protocol_name] += 1

                if len(decoded_logs) < args.max_log:
                    decoded_logs.append(
                        "IPv4 "
                        f"src={d.src} dst={d.dst} "
                        f"ver={d.version} ihl={d.ihl} hdr_bytes={d.header_bytes} "
                        f"len={d.total_length} id={d.identification} "
                        f"DF={int(d.flags_df)} MF={int(d.flags_mf)} frag_off={d.frag_offset} "
                        f"ttl={d.ttl} proto={d.protocol_name}({d.protocol_num}) chksum=0x{d.checksum:04x}"
                    )

            elif pkt.haslayer(IPv6):
                counts["IPv6"] += 1
                d6 = decode_ipv6(pkt)
                hlim_dist[d6.hop_limit] += 1
                header_sizes[d6.header_bytes_observed] += 1
                proto_dist[d6.upper_proto_name] += 1

                chain_str = " -> ".join([name for _, name in d6.extension_chain]) if d6.extension_chain else "None"
                if len(decoded_logs) < args.max_log:
                    decoded_logs.append(
                        "IPv6 "
                        f"src={d6.src} dst={d6.dst} "
                        f"ver={d6.version} tc={d6.traffic_class} fl=0x{d6.flow_label:05x} "
                        f"plen={d6.payload_length} nh={d6.next_header} hlim={d6.hop_limit} "
                        f"ext_chain={chain_str} upper={d6.upper_proto_name} "
                        f"hdr_bytes~{d6.header_bytes_observed}"
                    )
            else:
                counts["Non-IP"] += 1
                proto_dist["Non-IP"] += 1

    print("==== PCAP SUMMARY ====")
    print(f"Total packets: {total_packets}")
    print(f"IPv4 packets: {counts.get('IPv4', 0)}")
    print(f"IPv6 packets: {counts.get('IPv6', 0)}")
    if counts.get("Non-IP", 0):
        print(f"Non-IP packets: {counts.get('Non-IP', 0)}")

    print("\n==== TTL / Hop Limit distributions ====")
    if ttl_dist:
        print("IPv4 TTL:")
        for k in sorted(ttl_dist):
            print(f"  {k}: {ttl_dist[k]}")
    if hlim_dist:
        print("IPv6 Hop Limit:")
        for k in sorted(hlim_dist):
            print("  {}: {}".format(k, hlim_dist[k]))

    print("\n==== Protocol distribution ====")
    for proto, c in proto_dist.most_common():
        print(f"  {proto}: {c}")

    print("\n==== Header sizes observed (bytes) ====")
    for sz, c in sorted(header_sizes.items(), key=lambda x: x[0]):
        print(f"  {sz}: {c}")

    print("\n==== DECODED HEADER LOG (first {} packets) ====".format(min(args.max_log, len(decoded_logs))))
    for line in decoded_logs:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
