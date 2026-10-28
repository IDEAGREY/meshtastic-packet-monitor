#!/usr/bin/env python3
"""Print received Meshtastic packets as readable, labeled blocks."""

import json
import argparse
import textwrap
import time
from datetime import datetime

from pubsub import pub
from meshtastic.serial_interface import SerialInterface


def json_safe(value):
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items() if key != "raw"}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def node_label(interface, node_num, node_id):
    if node_num in (None, 0xFFFFFFFF):
        return node_id or "broadcast"
    node = (getattr(interface, "nodesByNum", None) or {}).get(node_num, {})
    user = node.get("user", {})
    long_name = user.get("longName")
    short_name = user.get("shortName")
    label = " / ".join(name for name in (long_name, short_name) if name)
    return f"{label} ({node_id or f'!{node_num:08x}'})" if label else (node_id or f"!{node_num:08x}")


def on_receive(packet, interface):
    decoded = packet.get("decoded") or {}
    packet_type = decoded.get("portnum", "UNKNOWN")
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    payload = decoded.get("payload")

    print(f"\n{'─' * 68}\n{timestamp}  {packet_type}")
    sender = node_label(interface, packet.get("from"), packet.get("fromId"))
    recipient = node_label(interface, packet.get("to"), packet.get("toId"))
    print(f"From: {sender}\nTo:   {recipient}")

    fields = []
    for key, label in (("id", "ID"), ("channel", "Channel"), ("hopLimit", "Hops left"), ("hopStart", "Hop start"), ("rxRssi", "RSSI dBm"), ("rxSnr", "SNR dB")):
        if packet.get(key) is not None:
            fields.append(f"{label}: {packet[key]}")
    if payload is not None:
        fields.append(f"Payload: {len(payload)} bytes")
    if fields:
        print("  " + "  |  ".join(fields))

    message = decoded.get("text")
    if message:
        print(f"Message: {json.dumps(str(message), ensure_ascii=False)}")

    details = {key: value for key, value in decoded.items() if key not in {"payload", "raw", "portnum", "text"}}
    if details:
        print("Decoded:")
        rendered = json.dumps(json_safe(details), indent=2, ensure_ascii=False)
        print(textwrap.indent(rendered, "  "))

    if payload:
        print("Payload hex:")
        hex_bytes = payload.hex(" ")
        for line in textwrap.wrap(hex_bytes, width=96):
            print(f"  {line}")
    print(flush=True)


parser = argparse.ArgumentParser(description="Readable live monitor for USB-connected Meshtastic nodes")
parser.add_argument("--port", help="serial port (auto-detect when exactly one compatible port is found)")
args = parser.parse_args()

pub.subscribe(on_receive, "meshtastic.receive")
radio = SerialInterface(devPath=args.port)
print(f"Connected to {radio.devPath}. Readable packet monitor active; Ctrl-C to stop.", flush=True)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    radio.close()
