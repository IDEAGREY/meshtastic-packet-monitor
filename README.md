# Meshtastic Packet Monitor

A small terminal monitor for a Meshtastic node connected over USB serial. It displays received packet types, sender and recipient names when available, packet metadata, decoded fields, readable text messages, and payload bytes.

## What it shows

For packets the connected node receives, the monitor can display:

- **Names and IDs:** sender and recipient names from the node database, plus Meshtastic node IDs. Names appear after the node learns that node's information.
- **Messages:** decoded text when the radio has the channel key. The default LongFast channel uses the published `AQ==` PSK, so its messages are readable with matching radio settings. A custom channel requires its PSK; direct messages protected by node keys remain private.
- **Reported location:** decoded `POSITION_APP` details such as latitude, longitude, altitude, time, location source, and precision when those fields are present. These are coordinates carried in the packet by the sending node.
- **Telemetry:** fields such as battery level, voltage, uptime, channel utilization, and transmit airtime when provided.
- **Packet and radio details:** packet type and ID, channel, hop limit, RSSI, SNR, decoded routing or node information, payload size, and payload bytes in hex.

The output can contain message text and location data, so treat captured output as sensitive. The monitor shows location coordinates included in received position packets; it does not estimate location from signal strength or triangulate the radio transmitter. It also does not scan the LoRa band or bypass encryption: it formats packets delivered by the connected node on its configured frequency, modem preset, and channels.

## Requirements

- Python 3.10 or newer
- A Meshtastic radio with USB serial support
- A data-capable USB cable

## Install

### macOS or Linux

From this folder, create a virtual environment and install the dependency:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Connect one Meshtastic node over USB and run the monitor without arguments. It asks the Meshtastic Python library to detect a compatible serial device:

```sh
python packet_monitor.py
```

If multiple compatible serial devices are connected, specify the port explicitly:

```sh
python packet_monitor.py --port /dev/cu.usbserial-0001
```

On Linux, a port may look like `/dev/ttyUSB0` or `/dev/ttyACM0`. On Windows, use a COM port such as `COM5`:

```powershell
python packet_monitor.py --port COM5
```

The monitor prints one readable block per received packet. Press **Ctrl-C** to stop it. Only one program can own a serial port at a time; close the Meshtastic app or any other serial monitor before starting this script.

## Troubleshooting

- **No serial node detected:** try a data-capable USB cable, check the system's serial-device list, and pass the port with `--port`.
- **Port already in use:** stop the other monitor or app connected to the node, then run this script again.
- **No message text:** confirm the node is receiving on the intended channel and has the matching channel key. The monitor cannot decrypt channels for which the node has no key.
- **Names are missing:** the node may not have received node information for that sender yet; the packet can still appear with its node ID.

## How it works

The script uses the Meshtastic Python client API over the node's USB serial connection. It formats packets delivered by the connected node; it does not control or flash the radio.
