import socket
import sys
import time

import nmap
from ovos_PHAL_plugin_commonIOT.opm.base import Sensor, IOTScannerPlugin


# Get your local network IP address. e.g. 192.168.178.X
def get_lan_ip():
    try:
        return ([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
    except socket.error as e:
        sys.stderr.write(str(e) + "\n")  # probably offline / no internet connection
        sys.exit(e.errno)


class LanDevice(Sensor):
    def __init__(self, device_id, host, name="generic lan device", raw_data=None):
        device_id = device_id or f"lan:{host}"
        raw_data = raw_data or {"name": name, "description": "local network device"}
        super().__init__(device_id, host, name, raw_data)
        self.ttl = self.raw_data.get("keeptime", 30)

    @property
    def is_on(self):
        # if seen in last 30 seconds, report online
        if time.time() - self.raw_data.get("last_seen", 0) > self.ttl:
            return False
        return True


class LanPlugin(IOTScannerPlugin):
    def scan(self):
        hosts = str(".".join(get_lan_ip().split(".")[:-1])) + ".0/24"
        scanner = nmap.PortScanner()
        scanner.scan(hosts=hosts, arguments="-sn")

        for ip in scanner.all_hosts():
            name = self.aliases.get(ip) or scanner[ip].hostname() or "unknown"
            device_id = f"{ip}:{name}"
            yield LanDevice(device_id, ip, name,
                            raw_data=scanner[ip])

    def get_device(self, ip):
        for device in self.scan():
            if device.host == ip:
                return device
        return None
