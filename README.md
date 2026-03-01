# Assignment 04 – IPv4 vs IPv6 PCAP Analysis

## Overview
This program parses a PCAP file containing IPv4 and IPv6 traffic and generates summary statistics and decoded header logs.

The script analyzes:
- Count of IPv4 vs IPv6 packets
- TTL (IPv4) and Hop Limit (IPv6) distributions
- Protocol distribution (TCP, UDP, ICMP, ICMPv6)
- Header sizes observed
- Decoded header fields for both IPv4 and IPv6

## Requirements
- Python 3
- Scapy

Install Scapy:
pip install scapy

## Usage
# Assignment 04 – IPv4 vs IPv6 PCAP Analysis

## Overview
This program parses a PCAP file containing IPv4 and IPv6 traffic and generates summary statistics and decoded header logs.

The script analyzes:
- Count of IPv4 vs IPv6 packets
- TTL (IPv4) and Hop Limit (IPv6) distributions
- Protocol distribution (TCP, UDP, ICMP, ICMPv6)
- Header sizes observed
- Decoded header fields for both IPv4 and IPv6

## Requirements
- Python 3
- Scapy

Install Scapy:
pip install scapy

## Usage
python3 pcapdump.py <pcap_file> --max-log 40

Example:
python3 pcapdump.py test1_ping_and_curl.pcap --max-log 40

## Command Line Options
--max-log : Number of decoded packets to print (default: 50)

## Known Limitations
- IPv6 extension header size calculation is best-effort.
- Only common protocols are explicitly recognized.
