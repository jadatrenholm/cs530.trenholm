import random
import csv


class Link:
    """
    Represents a communication link between two nodes.
    Each link has:
    - a one-way delay
    - availability windows
    - optional packet loss
    """

    def __init__(self, name, delay, availability_windows, loss_rate=0.0):
        self.name = name
        self.delay = delay
        self.availability_windows = availability_windows
        self.loss_rate = loss_rate

    def is_available(self, time):
        for start, end in self.availability_windows:
            if start <= time <= end:
                return True
        return False

    def transmit(self, time, data):
        """
        Returns the arrival time if transmission succeeds.
        Returns None if the link is unavailable or packet is lost.
        """

        if not self.is_available(time):
            return None

        if random.random() < self.loss_rate:
            return None

        return time + self.delay


def simulate_tcp(total_segments, earth_to_rover_link, rto=700, max_time=10000):
    """
    Simulates a simplified TCP-style protocol.

    TCP requires end-to-end connectivity between Earth and Rover.
    The sender waits for ACKs and retransmits after timeout.
    """

    time = 0
    next_segment = 1
    delivered_segments = set()
    retransmissions = 0
    waiting_time = 0

    in_flight = None
    send_time = None
    ack_arrival_time = None

    while time <= max_time and len(delivered_segments) < total_segments:
        link_available = earth_to_rover_link.is_available(time)

        if not link_available:
            waiting_time += 1

        # Send a segment if nothing is in flight
        if in_flight is None and next_segment <= total_segments:
            arrival_time = earth_to_rover_link.transmit(time, next_segment)

            if arrival_time is not None:
                in_flight = next_segment
                send_time = time

                # ACK must return across the same end-to-end path
                ack_arrival_time = arrival_time + earth_to_rover_link.delay
            else:
                waiting_time += 1

        # Check if ACK arrived
        if ack_arrival_time is not None and time >= ack_arrival_time:
            delivered_segments.add(in_flight)
            next_segment += 1
            in_flight = None
            send_time = None
            ack_arrival_time = None

        # Timeout and retransmit
        if in_flight is not None and send_time is not None:
            if time - send_time >= rto:
                retransmissions += 1
                arrival_time = earth_to_rover_link.transmit(time, in_flight)
                send_time = time

                if arrival_time is not None:
                    ack_arrival_time = arrival_time + earth_to_rover_link.delay
                else:
                    ack_arrival_time = None

        time += 1

    percent_delivered = (len(delivered_segments) / total_segments) * 100

    return {
        "Protocol": "TCP-style",
        "Delivery Time": time if len(delivered_segments) == total_segments else "Not completed",
        "Retransmissions": retransmissions,
        "Percent Delivered": round(percent_delivered, 2),
        "Waiting Time": waiting_time,
        "Stored Bundles": "N/A"
    }


def simulate_dtn(total_bundles, earth_to_orbiter_link, orbiter_to_rover_link, max_time=10000):
    """
    Simulates a simplified DTN-style protocol.

    DTN does not need an end-to-end path.
    Earth sends bundles to the Orbiter.
    The Orbiter stores bundles until the Rover link becomes available.
    """

    time = 0
    earth_queue = list(range(1, total_bundles + 1))
    orbiter_storage = []
    rover_received = set()

    in_transit_to_orbiter = []
    in_transit_to_rover = []

    waiting_time = 0
    stored_bundle_count = 0

    while time <= max_time and len(rover_received) < total_bundles:

        # Earth sends bundles to Orbiter when Earth-Orbiter link is available
        if earth_queue and earth_to_orbiter_link.is_available(time):
            bundle = earth_queue.pop(0)
            arrival_time = earth_to_orbiter_link.transmit(time, bundle)

            if arrival_time is not None:
                in_transit_to_orbiter.append((arrival_time, bundle))
            else:
                earth_queue.insert(0, bundle)

        # Bundles arrive at Orbiter and are stored
        arrived_at_orbiter = [
            item for item in in_transit_to_orbiter if item[0] <= time
        ]

        for arrival_time, bundle in arrived_at_orbiter:
            orbiter_storage.append(bundle)
            stored_bundle_count += 1
            in_transit_to_orbiter.remove((arrival_time, bundle))

        # Orbiter forwards bundles to Rover when Orbiter-Rover link is available
        if orbiter_storage and orbiter_to_rover_link.is_available(time):
            bundle = orbiter_storage.pop(0)
            arrival_time = orbiter_to_rover_link.transmit(time, bundle)

            if arrival_time is not None:
                in_transit_to_rover.append((arrival_time, bundle))
            else:
                orbiter_storage.insert(0, bundle)

        # Bundles arrive at Rover
        arrived_at_rover = [
            item for item in in_transit_to_rover if item[0] <= time
        ]

        for arrival_time, bundle in arrived_at_rover:
            rover_received.add(bundle)
            in_transit_to_rover.remove((arrival_time, bundle))

        # Waiting time occurs when either link is unavailable and data is waiting
        if earth_queue and not earth_to_orbiter_link.is_available(time):
            waiting_time += 1

        if orbiter_storage and not orbiter_to_rover_link.is_available(time):
            waiting_time += 1

        time += 1

    percent_delivered = (len(rover_received) / total_bundles) * 100

    return {
        "Protocol": "DTN-style",
        "Delivery Time": time if len(rover_received) == total_bundles else "Not completed",
        "Retransmissions": 0,
        "Percent Delivered": round(percent_delivered, 2),
        "Waiting Time": waiting_time,
        "Stored Bundles": stored_bundle_count
    }


def run_experiment(name, tcp_link, earth_orbiter_link, orbiter_rover_link):
    print(f"\n{name}")
    print("-" * len(name))

    tcp_result = simulate_tcp(
        total_segments=10,
        earth_to_rover_link=tcp_link
    )

    dtn_result = simulate_dtn(
        total_bundles=10,
        earth_to_orbiter_link=earth_orbiter_link,
        orbiter_to_rover_link=orbiter_rover_link
    )

    print(tcp_result)
    print(dtn_result)

    return name, tcp_result, dtn_result


def save_results_to_csv(results, filename="results.csv"):
    fieldnames = [
        "Experiment",
        "Protocol",
        "Delivery Time",
        "Retransmissions",
        "Percent Delivered",
        "Waiting Time",
        "Stored Bundles"
    ]

    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for experiment_name, tcp_result, dtn_result in results:
            tcp_result["Experiment"] = experiment_name
            dtn_result["Experiment"] = experiment_name

            writer.writerow(tcp_result)
            writer.writerow(dtn_result)


def main():
    random.seed(42)

    all_results = []

    # Experiment 1: Continuous connectivity
    tcp_link_1 = Link(
        name="Earth to Rover",
        delay=300,
        availability_windows=[(0, 10000)],
        loss_rate=0.0
    )

    earth_orbiter_1 = Link(
        name="Earth to Orbiter",
        delay=300,
        availability_windows=[(0, 10000)],
        loss_rate=0.0
    )

    orbiter_rover_1 = Link(
        name="Orbiter to Rover",
        delay=120,
        availability_windows=[(0, 10000)],
        loss_rate=0.0
    )

    all_results.append(
        run_experiment(
            "Experiment 1: Continuous Connectivity",
            tcp_link_1,
            earth_orbiter_1,
            orbiter_rover_1
        )
    )

    # Experiment 2: Intermittent connectivity
    # Earth can reach Orbiter from 0 to 800 seconds.
    # Orbiter can reach Rover from 1200 to 1800 seconds.
    # There is no continuous Earth-to-Rover path.
    tcp_link_2 = Link(
        name="Earth to Rover",
        delay=300,
        availability_windows=[],
        loss_rate=0.0
    )

    earth_orbiter_2 = Link(
        name="Earth to Orbiter",
        delay=300,
        availability_windows=[(0, 800)],
        loss_rate=0.0
    )

    orbiter_rover_2 = Link(
        name="Orbiter to Rover",
        delay=120,
        availability_windows=[(1200, 1800)],
        loss_rate=0.0
    )

    all_results.append(
        run_experiment(
            "Experiment 2: Intermittent Connectivity",
            tcp_link_2,
            earth_orbiter_2,
            orbiter_rover_2
        )
    )

    # Experiment 3: Lossy network
    tcp_link_3 = Link(
        name="Earth to Rover",
        delay=300,
        availability_windows=[(0, 10000)],
        loss_rate=0.10
    )

    earth_orbiter_3 = Link(
        name="Earth to Orbiter",
        delay=300,
        availability_windows=[(0, 10000)],
        loss_rate=0.10
    )

    orbiter_rover_3 = Link(
        name="Orbiter to Rover",
        delay=120,
        availability_windows=[(0, 10000)],
        loss_rate=0.10
    )

    all_results.append(
        run_experiment(
            "Experiment 3: Lossy Network",
            tcp_link_3,
            earth_orbiter_3,
            orbiter_rover_3
        )
    )

    save_results_to_csv(all_results)

    print("\nResults saved to results.csv")


if __name__ == "__main__":
    main()