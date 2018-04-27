"""
test_simulator.py
-----------------
Unit tests for the DTMF Home Automation System simulation.

Run with:
  python -m pytest tests/
  or
  python tests/test_simulator.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'simulation'))

from mt8870 import MT8870, TRUTH_TABLE, VALID_KEYS
from dtmf_relay_simulator import HomeAutomationSystem, RelayController, ULN2003


class TestMT8870Decoder(unittest.TestCase):
    """Tests for the MT8870 DTMF decoder model."""

    def setUp(self):
        self.decoder = MT8870()

    def test_valid_key_2_outputs_q2_only(self):
        """Key '2' should set Q2=1 and Q1=Q3=Q4=0."""
        self.decoder.receive_tone('2')
        out = self.decoder.get_outputs()
        self.assertEqual(out['Q1'], 0)
        self.assertEqual(out['Q2'], 1)
        self.assertEqual(out['Q3'], 0)
        self.assertEqual(out['Q4'], 0)

    def test_valid_key_4_outputs_q3_only(self):
        """Key '4' should set Q3=1 and Q1=Q2=Q4=0."""
        self.decoder.receive_tone('4')
        out = self.decoder.get_outputs()
        self.assertEqual(out['Q1'], 0)
        self.assertEqual(out['Q2'], 0)
        self.assertEqual(out['Q3'], 1)
        self.assertEqual(out['Q4'], 0)

    def test_valid_key_8_outputs_q4_only(self):
        """Key '8' should set Q4=1 and Q1=Q2=Q3=0."""
        self.decoder.receive_tone('8')
        out = self.decoder.get_outputs()
        self.assertEqual(out['Q1'], 0)
        self.assertEqual(out['Q2'], 0)
        self.assertEqual(out['Q3'], 0)
        self.assertEqual(out['Q4'], 1)

    def test_valid_key_1_outputs_q1_only(self):
        """Key '1' should set Q1=1 and Q2=Q3=Q4=0 (no relay activated)."""
        self.decoder.receive_tone('1')
        out = self.decoder.get_outputs()
        self.assertEqual(out['Q1'], 1)
        self.assertEqual(out['Q2'], 0)
        self.assertEqual(out['Q3'], 0)
        self.assertEqual(out['Q4'], 0)

    def test_invalid_key_returns_false(self):
        """An invalid key should return False and not set StD."""
        result = self.decoder.receive_tone('Z')
        self.assertFalse(result)
        self.assertEqual(self.decoder.std, 0)

    def test_std_high_on_valid_tone(self):
        """StD pin should be HIGH after a valid DTMF tone is received."""
        self.decoder.receive_tone('5')
        self.assertEqual(self.decoder.std, 1)

    def test_reset_clears_all_outputs(self):
        """Reset should clear all output pins to 0."""
        self.decoder.receive_tone('8')
        self.decoder.reset()
        out = self.decoder.get_outputs()
        self.assertEqual(out['Q1'], 0)
        self.assertEqual(out['Q2'], 0)
        self.assertEqual(out['Q3'], 0)
        self.assertEqual(out['Q4'], 0)
        self.assertEqual(out['StD'], 0)

    def test_all_valid_keys_in_truth_table(self):
        """All keys in TRUTH_TABLE should be decoded without error."""
        for key in TRUTH_TABLE:
            result = self.decoder.receive_tone(key)
            self.assertTrue(result, f"Key '{key}' should be valid.")

    def test_tone_frequencies_key_2(self):
        """Key '2' should have row=697 Hz and col=1336 Hz."""
        freqs = self.decoder.get_tone_frequencies('2')
        self.assertEqual(freqs, (697, 1336))

    def test_tone_frequencies_key_8(self):
        """Key '8' should have row=852 Hz and col=1336 Hz."""
        freqs = self.decoder.get_tone_frequencies('8')
        self.assertEqual(freqs, (852, 1336))


class TestRelayController(unittest.TestCase):
    """Tests for the relay controller model."""

    def setUp(self):
        self.relays = RelayController()

    def test_all_relays_off_initially(self):
        """All relays should be OFF at startup."""
        for i in [1, 2, 3]:
            self.assertFalse(self.relays.get_state(i))

    def test_toggle_turns_relay_on(self):
        """First toggle should turn relay ON."""
        self.relays.toggle(1)
        self.assertTrue(self.relays.get_state(1))

    def test_double_toggle_returns_relay_off(self):
        """Second toggle should turn relay back OFF."""
        self.relays.toggle(2)
        self.relays.toggle(2)
        self.assertFalse(self.relays.get_state(2))

    def test_relays_are_independent(self):
        """Toggling one relay should not affect others."""
        self.relays.toggle(1)
        self.assertTrue(self.relays.get_state(1))
        self.assertFalse(self.relays.get_state(2))
        self.assertFalse(self.relays.get_state(3))


class TestHomeAutomationSystem(unittest.TestCase):
    """Integration tests for the full system simulation."""

    def setUp(self):
        self.system = HomeAutomationSystem()

    def test_initial_all_loads_off(self):
        """All loads should be OFF when the system starts."""
        status = self.system.get_status()
        for load, state in status.items():
            self.assertEqual(state, 'OFF', f"{load} should be OFF initially.")

    def test_key_2_turns_light_on(self):
        """Pressing key '2' should turn the Light ON."""
        self.system.press_key('2')
        self.assertEqual(self.system.get_status()['Light'], 'ON')

    def test_key_4_turns_fan_on(self):
        """Pressing key '4' should turn the Fan ON."""
        self.system.press_key('4')
        self.assertEqual(self.system.get_status()['Fan'], 'ON')

    def test_key_8_turns_tv_on(self):
        """Pressing key '8' should turn the TV ON."""
        self.system.press_key('8')
        self.assertEqual(self.system.get_status()['TV'], 'ON')

    def test_key_2_toggles_light_off(self):
        """Pressing key '2' twice should return the Light to OFF."""
        self.system.press_key('2')
        self.system.press_key('2')
        self.assertEqual(self.system.get_status()['Light'], 'OFF')

    def test_key_1_activates_no_relay(self):
        """Key '1' activates only Q1, which is not wired to any relay."""
        result = self.system.press_key('1')
        self.assertEqual(result['activated_relays'], [])
        status = self.system.get_status()
        for state in status.values():
            self.assertEqual(state, 'OFF')

    def test_invalid_key_changes_nothing(self):
        """An invalid key should leave all loads unchanged."""
        result = self.system.press_key('X')
        self.assertFalse(result['valid'])
        status = self.system.get_status()
        for state in status.values():
            self.assertEqual(state, 'OFF')

    def test_all_loads_on_then_reset(self):
        """All three loads can be turned ON and reset clears all."""
        self.system.press_key('2')
        self.system.press_key('4')
        self.system.press_key('8')
        self.system.reset()
        status = self.system.get_status()
        for load, state in status.items():
            self.assertEqual(state, 'OFF', f"{load} should be OFF after reset.")

    def test_loads_are_independent(self):
        """Turning one load ON should not affect the other two."""
        self.system.press_key('4')
        status = self.system.get_status()
        self.assertEqual(status['Light'], 'OFF')
        self.assertEqual(status['Fan'],   'ON')
        self.assertEqual(status['TV'],    'OFF')

    def test_event_log_records_key_presses(self):
        """Event log should record each valid key press."""
        self.system.press_key('2')
        self.system.press_key('4')
        self.assertEqual(len(self.system.event_log), 2)

    def test_result_contains_load_states(self):
        """Press result should include the state of all three loads."""
        result = self.system.press_key('8')
        self.assertIn('Light', result['load_states'])
        self.assertIn('Fan',   result['load_states'])
        self.assertIn('TV',    result['load_states'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
