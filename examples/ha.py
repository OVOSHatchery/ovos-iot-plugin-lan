import json
import string
from pprint import pprint

import requests
from ovos_utils import wait_for_exit_signal
from ovos_utils.messagebus import FakeBus

from ovos_iot_plugin_lan import LanPlugin

HA_URL = "http://0.0.0.0:8123"
HA_TOKEN = "xxx"

bus = FakeBus()
print("scanning....")

# user defined device_id to friendly name mappings
aliases = {
    "192.168.1.1": "Router",
    "192.168.1.19": "Mark 1"
}

icons = {

}


def get_id_name(device):
    if device.name and device.name != "unknown":
        device_id = device.name
        friendly = device.name
    else:
        device_id = device.device_id
        friendly = device.host

    if device.host in aliases:
        friendly = aliases[device.host]

    device_id = device_id.replace(":", "_").replace("-", "_").replace(".", "_").replace("(", "_").replace(")",
                                                                                                          "").strip().replace(
        " ", "_")
    friendly = friendly.replace("(", "_").replace(")", "").strip().replace(" ", "_")

    device_id = ''.join(filter(lambda x: x in string.printable, device_id))
    friendly = ''.join(filter(lambda x: x in string.printable, friendly))
    return device_id, friendly


def new_cb(device):
    pprint(device.as_dict)

    device_id, friendly = get_id_name(device)

    attrs = {"friendly_name": friendly,
             "icon": "mdi:devices",
             "state_color": True,
             "device_class": "presence"}
    if device.host in icons:
        attrs["icon"] = icons[device.host]

    response = requests.post(
        f"{HA_URL}/api/states/binary_sensor.lan_{device_id}",
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
            "content-type": "application/json",
        },
        data=json.dumps({"state": "on", "attributes": attrs}),
    )
    print(response.text)


def cb(device):
    pprint(device.as_dict)

    device_id, friendly = get_id_name(device)

    attrs = {"friendly_name": friendly,
             "icon": "mdi:devices",
             "state_color": True,
             "device_class": "presence"}
    if device.host in icons:
        attrs["icon"] = icons[device.host]

    response = requests.post(
        f"{HA_URL}/api/states/binary_sensor.lan_{device_id}",
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
            "content-type": "application/json",
        },
        data=json.dumps({"state": "off", "attributes": attrs}),
    )
    print(response.text)


scanner = LanPlugin(bus,
                    aliases=aliases,
                    new_device_callback=new_cb,
                    lost_device_callback=cb)

scanner.start()
wait_for_exit_signal()
