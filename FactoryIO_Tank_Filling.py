from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
import time

PLC_SERVER = '127.0.0.1'
PORT = 502
SLAVE_ID = 1

def modbus_monitor():
    client = ModbusTcpClient(PLC_SERVER, port=PORT)
    print(f'Python attempting to connect to {PLC_SERVER}:{PORT}')

    if not client.connect():
        print('Failed to connect to PLC/Factory I/0')
        return
    print('Successfully connected to PLC!')

    # STATE MACHINE VARIABLES

    state = 'IDLE'
    fill_start_time = None
    discharge_start_time = None

    try:
        while True:
            print('Factory is running...')

            #READ INPUT STATE
            read_inputs = client.read_discrete_inputs(
                address=0,
                count=3,
                device_id=SLAVE_ID
            )

            if read_inputs.isError():
                print("[ERROR] Failed to read inputs")
                continue
            inputs = {
                'Fill': read_inputs.bits[0],
                'Discharge': read_inputs.bits[1],
                'FACTORY I/O(running)': read_inputs.bits[2]
            }
            factory_running = inputs['FACTORY I/O(running)']
            fill = inputs['Fill']
            discharge= inputs['Discharge']

            for name, status in inputs.items():
                print(f"{name}: {'ON' if status else 'OFF'}")

            # READ OUTPUT STATE
            read_outputs = client.read_coils(address=0, count=4)
            if read_outputs.isError():
                print("[ERROR] Failed to read inputs")
                continue
            outputs = {
                'Fill Valve': read_outputs.bits[0],
                'Filling': read_outputs.bits[1],
                'Discharge Valve': read_outputs.bits[2],
                'Discharging': read_outputs.bits[3]
            }
            fill_valve = outputs['Fill Valve']
            filling = outputs['Filling']
            discharge_valve = outputs['Discharge Valve']
            discharging = outputs['Discharging']

            #CONTROL LOGIC
            if not factory_running:
                for coil in range(4):
                    client.write_coil(coil, False)
                state = 'IDLE'
                fill_start_time = None
                print('[STATE]Factory has stopped...')


            elif state == 'IDLE':
                if fill and not discharge_valve:
                    client.write_coil(0, True)
                    client.write_coil(1, True)
                    fill_start_time = time.time()
                    state = 'FILLING'
                    print('[STATE] Filling Started')


            elif state == 'FILLING':
                pulse_time = time.time() - fill_start_time
                print(f'Fill Timer : {pulse_time:.1f}s')
                if pulse_time >= 20:
                    client.write_coil(0, False)
                    client.write_coil(1, False)
                    fill_start_time = None
                    state = 'WAIT_DISCHARGE'
                    print('[STATE] Tank has filled for 20 seconds..')


            elif state == 'WAIT_DISCHARGE':
                if not discharge and not fill_valve:
                    client.write_coil(2, True)
                    client.write_coil(3, True)
                    discharge_start_time = time.time()
                    state = 'DISCHARGING'
                    print('[STATE] Discharging Started')

            elif state == 'DISCHARGING':
                elapsed = time.time() - discharge_start_time
                print(f'Discharge Timer : {elapsed:.1f}s')
                if elapsed >= 20:
                    client.write_coil(2, False)
                    client.write_coil(3, False)
                    state = 'IDLE'
                    discharge_start_time = None
                    print('[STATE] Discharge Complete')

            time.sleep(0.5)

    except KeyboardInterrupt:
        print('\n[INFO]User has interrupted this process')

    except ConnectionException:
        print('[ERROR]PLC connection lost')

    except Exception as ex:
        print(f'[ERROR] Unexpected error: {ex}')

    finally:
        client.close()
        print('\nModbus connection closed')


if __name__ == '__main__':
    modbus_monitor()
