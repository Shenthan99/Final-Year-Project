import time
import subprocess
from mininet.log import info

class QoSMonitor:
    def __init__(self, net):
        self.net = net

    def _run_command(self, host, cmd, timeout=30):
        try:
            return host.cmd(cmd, timeout=timeout)
        except subprocess.TimeoutExpired:
            info(f"Command timed out: {cmd}\n")
            return None

    def measure_bandwidth(self, src, dst, duration=5):
        src_host = self.net.get(src)
        dst_host = self.net.get(dst)

        server = dst_host.popen(f"iperf -s -p 5001")
        time.sleep(1)  # Give the server time to start

        output = self._run_command(src_host, f"iperf -c {dst_host.IP()} -p 5001 -t {duration}")
        server.terminate()

        if output is None:
            return None

        try:
            bandwidth = float(output.split("Mbits/sec")[0].split()[-1])
            return bandwidth
        except (IndexError, ValueError):
            info(f"Error parsing bandwidth output: {output}\n")
            return None

    def measure_latency(self, src, dst, count=5):
        src_host = self.net.get(src)
        dst_host = self.net.get(dst)

        output = self._run_command(src_host, f"ping -c {count} {dst_host.IP()}")

        if output is None:
            return None

        try:
            latency = float(output.split("/")[-3])
            return latency
        except (IndexError, ValueError):
            info(f"Error parsing latency output: {output}\n")
            return None

    def measure_jitter(self, src, dst, duration=5):
        src_host = self.net.get(src)
        dst_host = self.net.get(dst)

        server = dst_host.popen(f"iperf -s -u -p 5001")
        time.sleep(1)  # Give the server time to start

        output = self._run_command(src_host, f"iperf -c {dst_host.IP()} -u -p 5001 -t {duration}")
        server.terminate()

        if output is None:
            return None

        try:
            jitter = float(output.split("ms")[0].split()[-1])
            return jitter
        except (IndexError, ValueError):
            info(f"Error parsing jitter output: {output}\n")
            return None

    def measure_all_metrics(self, src, dst):
        bandwidth = self.measure_bandwidth(src, dst)
        latency = self.measure_latency(src, dst)
        jitter = self.measure_jitter(src, dst)

        return {
            "bandwidth": bandwidth,
            "latency": latency,
            "jitter": jitter
        }