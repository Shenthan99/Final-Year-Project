# import os
# import time
# from mininet.net import Mininet
# from mininet.node import OVSKernelSwitch, Controller
# from mininet.cli import CLI
# from mininet.log import setLogLevel, info
# from mininet.link import TCLink
# from mininet.clean import cleanup

# from qos_monitoring.qos_monitor import QoSMonitor
# from routing_algorithms.dijkstra import DijkstraRouting

# def create_topology():
#     net = Mininet(switch=OVSKernelSwitch, link=TCLink, controller=Controller)

#     info("*** Adding controller\n")
#     net.addController('c0')

#     info("*** Adding switches\n")
#     s1 = net.addSwitch('s1')
#     s2 = net.addSwitch('s2')
#     s3 = net.addSwitch('s3')

#     info("*** Adding hosts\n")
#     h1 = net.addHost('h1')
#     h2 = net.addHost('h2')
#     h3 = net.addHost('h3')

#     info("*** Adding links\n")
#     net.addLink(s1, s2, bw=10, delay='5ms')
#     net.addLink(s2, s3, bw=15, delay='10ms')
#     net.addLink(s1, s3, bw=5, delay='15ms')
#     net.addLink(h1, s1)
#     net.addLink(h2, s2)
#     net.addLink(h3, s3)

#     return net

# def run_simulation():
#     info("*** Cleaning up mininet\n")
#     cleanup()

#     info("*** Creating network\n")
#     try:
#         net = create_topology()
#         net.start()
#         info("*** Network started successfully\n")

#         info("*** Waiting for network convergence (5 seconds)\n")
#         time.sleep(5)

#         info("*** Applying Dijkstra routing\n")
#         router = DijkstraRouting(net)
#         router.apply_routing()
#         info("*** Dijkstra routing applied\n")

#         info("*** Initializing QoS monitor\n")
#         qos_monitor = QoSMonitor(net)

#         info("*** Measuring QoS metrics between h1 and h3\n")
#         try:
#             metrics = qos_monitor.measure_all_metrics('h1', 'h3')
#             info(f"Bandwidth: {metrics['bandwidth']:.2f} Mbits/sec\n")
#             info(f"Latency: {metrics['latency']:.2f} ms\n")
#             info(f"Jitter: {metrics['jitter']:.2f} ms\n")
#         except Exception as e:
#             info(f"*** Error measuring QoS metrics: {e}\n")

#         info("*** Running CLI\n")
#         CLI(net)

#     except Exception as e:
#         info(f"*** Error during simulation: {e}\n")
    
#     finally:
#         info("*** Stopping network\n")
#         if 'net' in locals():
#             net.stop()
#         cleanup()

# if __name__ == '__main__':
#     setLogLevel('info')
#     run_simulation()

import os
import time
import random
import csv
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.clean import cleanup

from qos_monitoring.qos_monitor import QoSMonitor
from routing_algorithms.dijkstra import DijkstraRouting
from routing_algorithms.ospf import OSPFRouting
from routing_algorithms.bgp import BGPRouting

def create_dynamic_topology(num_switches, num_hosts):
    net = Mininet(switch=OVSKernelSwitch, link=TCLink, controller=RemoteController)

    info("*** Adding Ryu controller\n")
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    info("*** Adding switches\n")
    switches = [net.addSwitch(f's{i+1}') for i in range(num_switches)]

    info("*** Adding hosts\n")
    hosts = [net.addHost(f'h{i+1}') for i in range(num_hosts)]

    info("*** Adding links\n")
    # Connect all switches in a mesh topology
    for i in range(num_switches):
        for j in range(i + 1, num_switches):
            bw = random.randint(10, 100)
            delay = f'{random.randint(1, 10)}ms'
            net.addLink(switches[i], switches[j], bw=bw, delay=delay)

    # Connect hosts to random switches
    for host in hosts:
        switch = random.choice(switches)
        net.addLink(host, switch)

    return net

def run_simulation():
    info("*** Cleaning up mininet\n")
    cleanup()

    info("*** Creating dynamic network\n")
    try:
        num_switches = 5  # Reduced from random(5, 10)
        num_hosts = 8  # Reduced from random(5, 15)
        net = create_dynamic_topology(num_switches, num_hosts)
        net.start()
        info(f"*** Network started successfully with {num_switches} switches and {num_hosts} hosts\n")

        info("*** Waiting for network convergence (10 seconds)\n")
        time.sleep(10)

        routing_algorithms = [
            ("Dijkstra", DijkstraRouting(net)),
            ("OSPF", OSPFRouting(net)),
            ("BGP", BGPRouting(net))
        ]

        qos_monitor = QoSMonitor(net)

        results = []

        for algo_name, router in routing_algorithms:
            info(f"*** Applying {algo_name} routing\n")
            router.apply_routing()
            info(f"*** {algo_name} routing applied\n")

            info(f"*** Measuring QoS metrics for {algo_name}\n")
            for i in range(3):  # Measure 3 random host pairs
                src, dst = random.sample(net.hosts, 2)
                try:
                    metrics = qos_monitor.measure_all_metrics(src.name, dst.name)
                    info(f"QoS metrics from {src.name} to {dst.name}:\n")
                    info(f"  Bandwidth: {metrics['bandwidth'] if metrics['bandwidth'] is not None else 'N/A'} Mbits/sec\n")
                    info(f"  Latency: {metrics['latency'] if metrics['latency'] is not None else 'N/A'} ms\n")
                    info(f"  Jitter: {metrics['jitter'] if metrics['jitter'] is not None else 'N/A'} ms\n")
                    
                    results.append({
                        "algorithm": algo_name,
                        "src": src.name,
                        "dst": dst.name,
                        "bandwidth": metrics['bandwidth'],
                        "latency": metrics['latency'],
                        "jitter": metrics['jitter']
                    })
                except Exception as e:
                    info(f"*** Error measuring QoS metrics: {e}\n")

            info("*** Waiting for 30 seconds before applying the next routing algorithm\n")
            time.sleep(30)

        # Save results to CSV
        with open('qos_results.csv', 'w', newline='') as csvfile:
            fieldnames = ['algorithm', 'src', 'dst', 'bandwidth', 'latency', 'jitter']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

        info("*** QoS measurement results saved to qos_results.csv\n")

        info("*** Running CLI\n")
        CLI(net)

    except Exception as e:
        info(f"*** Error during simulation: {e}\n")
    
    finally:
        info("*** Stopping network\n")
        if 'net' in locals():
            net.stop()
        cleanup()

if __name__ == '__main__':
    setLogLevel('info')
    run_simulation()