# Factory-I-O-Tank-Filling-and-Discharge-Control
This project uses **Python + Modbus TCP** to control a simple tank filling/discharge process in Factory I/O.

## Features

- Connects to a Modbus TCP server (PLC / Factory I/O)
- Reads discrete inputs:
  - Fill
  - Discharge
  - Factory I/O running status
- Reads coil outputs:
  - Fill Valve
  - Filling
  - Discharge Valve
  - Discharging
- Runs a state machine:
  - `IDLE`
  - `FILLING` (20s)
  - `WAIT_DISCHARGE`
  - `DISCHARGING` (20s)

## Requirements

- Python 3.9+
- `pymodbus`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Edit these constants in `modbus_monitor.py` if needed:

- `PLC_SERVER` (default: `127.0.0.1`)
- `PORT` (default: `502`)
- `SLAVE_ID` (default: `1`)

## Run

```bash
python modbus_monitor.py
```

## Notes

- `127.0.0.1` assumes Modbus server is running locally.
- Port `502` may require admin/root privileges on some systems.
- For real PLC deployments, use proper network/security controls.

## License

MIT.
