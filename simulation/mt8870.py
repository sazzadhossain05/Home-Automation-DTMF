"""
mt8870.py
---------
Software model of the MT8870 DTMF Decoder IC.

The MT8870 detects Dual Tone Multi-Frequency (DTMF) signals and decodes
them into a 4-bit binary output on pins Q1, Q2, Q3, Q4.

DTMF Tone Frequencies
----------------------
Each phone key generates two simultaneous tones: one from the row group
and one from the column group.

         1209 Hz  1336 Hz  1477 Hz  1633 Hz
 697 Hz |   1   |   2   |   3   |   A   |
 770 Hz |   4   |   5   |   6   |   B   |
 852 Hz |   7   |   8   |   9   |   C   |
 941 Hz |   *   |   0   |   #   |   D   |

4-Bit Output Truth Table (Q1 Q2 Q3 Q4)
---------------------------------------
Key  | Q4  Q3  Q2  Q1
-----|----------------
  1  |  0   0   0   1
  2  |  0   0   1   0
  3  |  0   0   1   1
  4  |  0   1   0   0
  5  |  0   1   0   1
  6  |  0   1   1   0
  7  |  0   1   1   1
  8  |  1   0   0   0
  9  |  1   0   0   1
  0  |  1   0   1   0
  *  |  1   0   1   1
  #  |  1   1   0   0
  A  |  1   1   0   1
  B  |  1   1   1   0
  C  |  1   1   1   1
  D  |  0   0   0   0

Source: MT8870 Datasheet, Zarlink Semiconductor.

Note: In this circuit only Q2, Q3, Q4 are used (connected to ULN2003
input pins 5, 6, 7). Q1 is not connected to any relay.
"""

# DTMF row and column frequencies (Hz)
ROW_FREQUENCIES = [697, 770, 852, 941]
COL_FREQUENCIES = [1209, 1336, 1477, 1633]

# MT8870 4-bit output truth table
# Key -> (Q1, Q2, Q3, Q4)
TRUTH_TABLE = {
    '1': (1, 0, 0, 0),
    '2': (0, 1, 0, 0),
    '3': (1, 1, 0, 0),
    '4': (0, 0, 1, 0),
    '5': (1, 0, 1, 0),
    '6': (0, 1, 1, 0),
    '7': (1, 1, 1, 0),
    '8': (0, 0, 0, 1),
    '9': (1, 0, 0, 1),
    '0': (0, 1, 0, 1),
    '*': (1, 1, 0, 1),
    '#': (0, 0, 1, 1),
    'A': (1, 0, 1, 1),
    'B': (0, 1, 1, 1),
    'C': (1, 1, 1, 1),
    'D': (0, 0, 0, 0),
}

# DTMF tone frequency pairs for each key
# Key -> (row_freq_hz, col_freq_hz)
TONE_FREQUENCIES = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633),
}

VALID_KEYS = set(TRUTH_TABLE.keys())


class MT8870:
    """
    Software model of the MT8870 DTMF Decoder IC.

    In hardware this IC:
      - Receives DTMF audio on IN+ and IN- pins via AUX wire
      - Uses a 3.57 MHz crystal oscillator for internal timing
      - Outputs decoded 4-bit binary on Q1, Q2, Q3, Q4 pins
      - Raises StD (Delayed Steering) pin HIGH when a valid tone is detected

    This class models the decoding behaviour only.
    """

    def __init__(self):
        self.q1 = 0
        self.q2 = 0
        self.q3 = 0
        self.q4 = 0
        self.std = 0   # Delayed Steering output: 1 when valid tone detected
        self.last_key = None

    def receive_tone(self, key: str) -> bool:
        """
        Simulates receiving a DTMF tone for the given key character.
        Updates Q1-Q4 outputs and StD pin.

        Parameters
        ----------
        key : str
            A single character representing the DTMF key pressed.
            Valid values: '0'-'9', '*', '#', 'A', 'B', 'C', 'D'

        Returns
        -------
        bool
            True if the key was valid and decoded successfully.
            False if the key is not a valid DTMF character.
        """
        key = key.upper()

        if key not in VALID_KEYS:
            self.std = 0
            return False

        self.q1, self.q2, self.q3, self.q4 = TRUTH_TABLE[key]
        self.std = 1
        self.last_key = key
        return True

    def get_outputs(self) -> dict:
        """Returns the current state of all output pins."""
        return {
            'Q1': self.q1,
            'Q2': self.q2,
            'Q3': self.q3,
            'Q4': self.q4,
            'StD': self.std,
        }

    def get_tone_frequencies(self, key: str) -> tuple:
        """
        Returns the two DTMF frequencies (row, col) in Hz for a given key.
        Returns None if the key is not valid.
        """
        return TONE_FREQUENCIES.get(key.upper(), None)

    def reset(self):
        """Resets all output pins to 0."""
        self.q1 = self.q2 = self.q3 = self.q4 = self.std = 0
        self.last_key = None

    def print_truth_table(self):
        """Prints the full MT8870 4-bit output truth table."""
        print("MT8870 DTMF Decoder Truth Table")
        print("-" * 40)
        print(f"{'Key':<6} {'Q1':<5} {'Q2':<5} {'Q3':<5} {'Q4':<5}")
        print("-" * 40)
        for key, (q1, q2, q3, q4) in TRUTH_TABLE.items():
            print(f"  {key:<4} {q1:<5} {q2:<5} {q3:<5} {q4:<5}")
        print("-" * 40)
