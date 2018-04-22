"""
dtmf_relay_simulator.py
------------------------
Software simulation of the DTMF-based Home Automation System.

Hardware this code models:
  - MT8870 DTMF Decoder IC  (see simulation/mt8870.py)
  - ULN2003 Darlington Transistor Array
  - Three 5V relay switches
  - Three loads: Light, Fan, TV

Signal path in hardware:
  Mobile phone (AUX) -> MT8870 -> ULN2003 -> Relays -> Loads

Key-to-load mapping (based on MT8870 truth table and Q2/Q3/Q4 wiring):
  Key '2' -> Q2=1 -> Relay 1 -> Light
  Key '4' -> Q3=1 -> Relay 2 -> Fan
  Key '8' -> Q4=1 -> Relay 3 -> TV

NOTE: This is a software model of a hardware circuit. The actual
project has no microcontroller and no firmware. This simulation is
provided for documentation and educational purposes.

Course: CSE231 Digital Logic Design
Institution: North South University, Bangladesh (2018)

Usage:
  python dtmf_relay_simulator.py              # run demo
  python dtmf_relay_simulator.py --interactive # interactive mode
"""

import sys
import os

# Allow running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from mt8870 import MT8870


# ULN2003 output pins used in this circuit
# Maps MT8870 output pin name to ULN2003 input pin number
ULN2003_WIRING = {
    'Q2': 5,
    'Q3': 6,
    'Q4': 7,
}

# Relay to load mapping
# Each relay is driven by one ULN2003 channel
RELAY_LOADS = {
    1: 'Light',
    2: 'Fan',
    3: 'TV',
}

# Which MT8870 output controls which relay
PIN_TO_RELAY = {
    'Q2': 1,
    'Q3': 2,
    'Q4': 3,
}


class ULN2003:
    """
    Software model of the ULN2003 Darlington Transistor Array.

    In hardware the ULN2003:
      - Has 7 NPN Darlington transistor channels
      - Each channel handles up to 500 mA at 50V
      - Input HIGH drives output LOW (open collector, active low)
      - Includes internal flyback diodes for inductive load protection

    This circuit uses channels 5, 6, 7 (inputs from Q2, Q3, Q4 of MT8870).
    When an input goes HIGH, the corresponding output activates the relay coil.
    """

    def __init__(self):
        # Channel states: True = input HIGH (relay coil energised)
        self.channels = {5: False, 6: False, 7: False}

    def set_input(self, pin: int, signal: int):
        """
        Set the logic level on a ULN2003 input pin.
        Signal 1 (HIGH) energises the relay connected to this channel.
        """
        if pin in self.channels:
            self.channels[pin] = bool(signal)

    def get_output_active(self, pin: int) -> bool:
        """Returns True if the channel output is active (relay coil energised)."""
        return self.channels.get(pin, False)


class RelayController:
    """
    Models three 5V relay switches connected to ULN2003 outputs.
    Each relay controls one household load.
    Relay state is toggled each time the coil is energised.
    """

    def __init__(self):
        # Relay states: False = OFF (contact open), True = ON (contact closed)
        self.states = {1: False, 2: False, 3: False}

    def toggle(self, relay_number: int):
        """Toggle the state of a relay."""
        if relay_number in self.states:
            self.states[relay_number] = not self.states[relay_number]

    def get_state(self, relay_number: int) -> bool:
        """Returns True if the relay contact is closed (load ON)."""
        return self.states.get(relay_number, False)


class HomeAutomationSystem:
    """
    Full software simulation of the DTMF Home Automation System.

    Connects the MT8870 decoder, ULN2003 driver, and relay controller
    into a complete signal chain, mirroring the hardware circuit.
    """

    def __init__(self):
        self.decoder = MT8870()
        self.driver = ULN2003()
        self.relays = RelayController()
        self.event_log = []

    def press_key(self, key: str) -> dict:
        """
        Simulates pressing a key on the mobile phone.

        Steps:
          1. MT8870 decodes the DTMF tone to 4-bit binary
          2. Q2, Q3, Q4 signals fed to ULN2003 inputs 5, 6, 7
          3. Active ULN2003 channels toggle their relay states
          4. Relay contacts open or close, switching the load

        Parameters
        ----------
        key : str
            The phone keypad character pressed ('0'-'9', '*', '#')

        Returns
        -------
        dict
            Result containing decoded outputs, activated relays,
            and current load states.
        """
        result = {
            'key': key,
            'valid': False,
            'mt8870_output': None,
            'activated_relays': [],
            'load_states': {},
        }

        # Step 1: MT8870 decodes the DTMF tone
        valid = self.decoder.receive_tone(key)
        result['valid'] = valid

        if not valid:
            result['message'] = f"Key '{key}' is not a valid DTMF character."
            return result

        outputs = self.decoder.get_outputs()
        result['mt8870_output'] = outputs

        # Step 2: Feed Q2, Q3, Q4 into ULN2003 inputs 5, 6, 7
        pin_map = {'Q2': 5, 'Q3': 6, 'Q4': 7}
        for q_pin, uln_pin in pin_map.items():
            self.driver.set_input(uln_pin, outputs[q_pin])

        # Step 3: Toggle relays where ULN2003 channel is active
        for q_pin, relay_num in PIN_TO_RELAY.items():
            uln_pin = ULN2003_WIRING[q_pin]
            if self.driver.get_output_active(uln_pin):
                self.relays.toggle(relay_num)
                load = RELAY_LOADS[relay_num]
                state = 'ON' if self.relays.get_state(relay_num) else 'OFF'
                result['activated_relays'].append({
                    'relay': relay_num,
                    'load': load,
                    'state': state,
                })

        # Step 4: Record current states of all loads
        for relay_num, load in RELAY_LOADS.items():
            result['load_states'][load] = (
                'ON' if self.relays.get_state(relay_num) else 'OFF'
            )

        self.event_log.append(result)
        return result

    def get_status(self) -> dict:
        """Returns the current ON/OFF state of all three loads."""
        return {
            load: ('ON' if self.relays.get_state(relay_num) else 'OFF')
            for relay_num, load in RELAY_LOADS.items()
        }

    def reset(self):
        """Resets all relays to OFF and clears the decoder."""
        self.decoder.reset()
        self.relays = RelayController()
        self.driver = ULN2003()
        self.event_log.clear()


# -----------------------------------------------------------------------
# Display helpers
# -----------------------------------------------------------------------

def print_status(status: dict):
    """Prints the current state of all three loads."""
    print("\n  Load states:")
    for load, state in status.items():
        indicator = "[ON] " if state == 'ON' else "[OFF]"
        print(f"    {indicator}  {load}")
    print()


def print_result(result: dict):
    """Prints the result of a key press event."""
    key = result['key']

    if not result['valid']:
        print(f"  Key '{key}': Not a valid DTMF character. No relay activated.")
        return

    outputs = result['mt8870_output']
    print(
        f"  Key '{key}': MT8870 -> "
        f"Q1={outputs['Q1']} Q2={outputs['Q2']} "
        f"Q3={outputs['Q3']} Q4={outputs['Q4']}"
    )

    if result['activated_relays']:
        for r in result['activated_relays']:
            print(
                f"    Relay {r['relay']} ({r['load']}) -> {r['state']}"
            )
    else:
        print("    No relay activated (Q2=Q3=Q4=0).")


# -----------------------------------------------------------------------
# Demo and interactive modes
# -----------------------------------------------------------------------

def run_demo():
    """Runs a demonstration showing a typical usage sequence."""
    print("=" * 55)
    print("  DTMF Home Automation System  |  Demo Mode")
    print("=" * 55)
    print()
    print("  Key mapping:")
    print("    '2'  ->  Light")
    print("    '4'  ->  Fan")
    print("    '8'  ->  TV")
    print()

    system = HomeAutomationSystem()

    sequence = [
        ('2', "Turn Light ON"),
        ('4', "Turn Fan ON"),
        ('8', "Turn TV ON"),
        ('2', "Turn Light OFF"),
        ('8', "Turn TV OFF"),
        ('1', "Key with no relay (Q1 only)"),
        ('4', "Turn Fan OFF"),
    ]

    for key, description in sequence:
        print(f"  Action: {description}")
        result = system.press_key(key)
        print_result(result)
        print_status(system.get_status())


def run_interactive():
    """Lets the user press keys manually to control the simulated loads."""
    print("=" * 55)
    print("  DTMF Home Automation System  |  Interactive Mode")
    print("=" * 55)
    print()
    print("  Key mapping:")
    print("    '2'  ->  Light")
    print("    '4'  ->  Fan")
    print("    '8'  ->  TV")
    print()
    print("  Commands:")
    print("    Any DTMF key (0-9, *, #)  ->  press key")
    print("    'status'                  ->  show load states")
    print("    'reset'                   ->  turn all loads OFF")
    print("    'table'                   ->  show MT8870 truth table")
    print("    'quit'                    ->  exit")
    print()

    system = HomeAutomationSystem()

    while True:
        user_input = input("  Press key: ").strip()

        if not user_input:
            continue

        command = user_input.lower()

        if command == 'quit':
            print("  Exiting simulation.")
            break

        elif command == 'status':
            print_status(system.get_status())

        elif command == 'reset':
            system.reset()
            print("  All loads reset to OFF.")
            print_status(system.get_status())

        elif command == 'table':
            print()
            system.decoder.print_truth_table()
            print()

        elif len(user_input) == 1:
            result = system.press_key(user_input)
            print_result(result)
            print_status(system.get_status())

        else:
            print("  Please enter a single DTMF key.")


# -----------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        run_interactive()
    else:
        run_demo()
