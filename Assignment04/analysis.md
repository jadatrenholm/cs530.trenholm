# IPv4 vs IPv6 Packet Analysis

## 1. Why does IPv6 not include a header checksum?

IPv4 includes a header checksum that must be recalculated at each router hop. This introduces processing overhead.

IPv6 eliminates the header checksum to improve router efficiency. Error detection is handled by:
- Link-layer CRC
- Transport-layer checksums (TCP/UDP)

In the decoded logs, IPv4 packets show a checksum field, while IPv6 packets do not.

---

## 2. How does Path MTU Discovery differ? What ICMP message is used in IPv6?

In IPv4:
- Routers may fragment packets.
- Fragmentation fields include ID, DF, MF, and Fragment Offset.

In IPv6:
- Routers do NOT fragment packets.
- Fragmentation is performed only by the source host.
- IPv6 uses ICMPv6 "Packet Too Big" messages for PMTUD.

---

## 3. When will you see an IPv6 Fragment header?

An IPv6 Fragment header appears only when the source host fragments a packet due to MTU limitations.

No IPv6 fragment headers were observed in the captured traffic.

---

## 4. How do IPv6 extension headers change parsing logic?

IPv4:
- Options are embedded in the header.
- Header length is determined by the IHL field.
- Observed header sizes: 20 and 24 bytes.

IPv6:
- Base header is fixed at 40 bytes.
- Additional functionality is implemented via extension headers chained using the Next Header field.
- Observed header size: 40 bytes.

---

## Observations from Captured Data

- IPv4 TTL values commonly observed: 64 and 255
- IPv6 Hop Limit values commonly observed: 64 and 255
- Protocols captured: TCP, UDP, ICMP, ICMPv6, ARP (Non-IP)

The captures clearly demonstrate structural and operational differences between IPv4 and IPv6.
