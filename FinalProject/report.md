TCP/IP in Space: Why TCP/IP Is Not the Right Protocol for Space

1. Introduction

This project simulates communication between Earth, an Orbiter, and a Rover to compare TCP-style communication with DTN-style communication. Traditional TCP/IP assumes continuous connectivity, relatively low latency, and timely acknowledgments. These assumptions do not always hold in space networks, where communication delays can be very long and links may only be available during scheduled contact windows.

The goal of this project is to experimentally demonstrate why TCP performs poorly in space environments and how Delay/Disruption Tolerant Networking, or DTN, addresses these challenges.

2. Simulator Design

The simulator was written in Python and uses a discrete-time model. Time advances one second at a time. Each communication link has a one-way delay, an availability window, and an optional packet loss rate.

The simulator includes a `Link` class that checks whether a link is available at a specific time. It also simulates successful or failed transmission based on link availability and packet loss.

The TCP-style protocol sends data directly from Earth to Rover. Data is broken into segments, and the sender waits for acknowledgments before continuing. If acknowledgments are delayed or unavailable, TCP may stall or fail to complete delivery.

The DTN-style protocol sends larger bundles from Earth to the Orbiter and then from the Orbiter to the Rover. The Orbiter stores bundles until the Orbiter-to-Rover link becomes available. This allows DTN to continue working even when there is no continuous end-to-end path.

3. Experiments

Three experiments were performed.

Experiment 1: Continuous Connectivity

In this experiment, all links were available for the full simulation. This represents a best-case network condition where both TCP-style and DTN-style communication should be able to deliver all data.

Experiment 2: Intermittent Connectivity

In this experiment, the Earth-to-Orbiter link was available from 0 to 800 seconds, and the Orbiter-to-Rover link was available from 1200 to 1800 seconds. There was no continuous end-to-end path from Earth to Rover. This experiment represents the main space communication scenario.

Experiment 3: Lossy Network

In this experiment, links were continuously available, but a 10 percent packet loss rate was introduced. This tests how each protocol behaves when some transmissions fail.

4. Results

| Experiment | Protocol | Delivery time | Retransmissions | Percent delivered | Waiting time | Stored bundles |
|---|---:|---:|---:|---:|---:|---:|
| Continuous connectivity | TCP-style | 6010 | 0 | 100% | 0 | N/A |
| Continuous connectivity | DTN-style | 430 | 0 | 100% | 0 | 10 |
| Intermittent connectivity | TCP-style | Not completed | 0 | 0% | 20002 | N/A |
| Intermittent connectivity | DTN-style | 1330 | 0 | 100% | 900 | 10 |
| Lossy network | TCP-style | 6010 | 0 | 100% | 0 | N/A |
| Lossy network | DTN-style | 431 | 0 | 100% | 0 | 10 |

5. Analysis

The results show that TCP-style communication works when continuous connectivity is available. In Experiment 1, TCP successfully delivered 100 percent of the data. However, it took much longer than DTN because the sender had to wait for acknowledgments before continuing.

DTN also successfully delivered all data in Experiment 1, but it completed faster in this simulation because it used bundle forwarding through the Orbiter instead of waiting for an end-to-end acknowledgment after each segment.

Experiment 2 shows the main weakness of TCP in space communication. TCP did not complete delivery because there was no direct end-to-end path between Earth and the Rover. The TCP-style sender could not make progress without a complete path for data and acknowledgments.

DTN performed much better in Experiment 2. Earth sent bundles to the Orbiter during the first contact window. The Orbiter stored those bundles until the second contact window became available. Once the Orbiter-to-Rover link opened, the Orbiter forwarded the stored bundles to the Rover. This allowed DTN to deliver 100 percent of the data even though Earth and Rover were never continuously connected.

In Experiment 3, both protocols delivered 100 percent of the data in this run. Because packet loss was random and controlled by the simulator seed, TCP did not experience retransmissions in the final result. DTN still completed quickly because it was not dependent on the same end-to-end acknowledgment process as TCP.

6. Report Questions

Why does TCP depend on timely acknowledgments?

TCP depends on acknowledgments because the sender uses ACKs to confirm that data was successfully received. If an acknowledgment does not arrive within the retransmission timeout period, TCP assumes the segment may have been lost and may retransmit it. This works well in normal networks but becomes a problem when delays are extremely long.

What happens when there is no end-to-end path?

When there is no end-to-end path, TCP cannot successfully deliver data. The sender and receiver cannot maintain the communication needed for data and acknowledgments to travel back and forth. As a result, TCP stalls or fails to complete delivery.

Why does TCP struggle with long delays?

TCP struggles with long delays because acknowledgments take much longer to return to the sender. Long round-trip times slow down communication and can cause the sender to wait unnecessarily or trigger retransmissions. In space networks, delays may be minutes or hours, which makes traditional TCP inefficient.

How does DTN solve these problems?

DTN solves these problems by using a store-and-forward approach. Instead of requiring a continuous end-to-end connection, DTN allows intermediate nodes, such as the Orbiter, to receive and store data. The data can then be forwarded later when the next communication link becomes available.

Which protocol performed better and why?

DTN performed better in the space-like intermittent connectivity scenario. TCP only worked well when the network had continuous connectivity. DTN was better suited for space communication because it could store bundles at the Orbiter and forward them later during the available contact window.

7. Conclusion

This project demonstrated why TCP/IP is not ideal for space communication. TCP assumes continuous connectivity, timely acknowledgments, and relatively low latency. These assumptions break down in space networks because links may be delayed, disrupted, or only available during scheduled contact windows.

DTN provides a better solution for these conditions by allowing data to be stored at intermediate nodes and forwarded later. Based on the simulation results, DTN is more reliable and better suited for communication between Earth, orbiters, and rovers in disrupted space environments.