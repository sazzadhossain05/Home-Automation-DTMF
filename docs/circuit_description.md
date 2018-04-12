# Circuit Description

## Overview

The circuit receives a DTMF tone from a mobile phone via an AUX wire and uses the
MT8870 decoder IC to convert it into a 4-bit digital output. This output drives the
ULN2003 transistor array, which activates relay switches to control three loads.

---

## Stage 1: DTMF Input

A mobile phone is connected to the circuit input via a 3.5mm AUX wire. When the user
dials a key on the phone keypad, the phone generates a DTMF tone consisting of two
superimposed frequencies. This audio signal is fed directly into the IN+ and IN- pins
of the MT8870 DTMF decoder.

---

## Stage 2: DTMF Decoding (MT8870)

The MT8870 IC decodes the incoming DTMF tone and produces a 4-bit binary output on
its Q1, Q2, Q3, and Q4 output pins. A 3.57 MHz crystal oscillator is connected to the
OSC1 and OSC2 pins (pins 7 and 8) with 22 pF capacitors on each side to ground. This
provides the stable clock reference required for accurate tone detection.

A 100K resistor is connected to the IN- input pin, and a 0.1 uF capacitor is used for
signal conditioning at the input stage.

The DTMF output encoding for relevant keys is as follows:

| Key | Q1 | Q2 | Q3 | Q4 |
|-----|----|----|----|----|
| 1   | 1  | 0  | 0  | 0  |
| 2   | 0  | 1  | 0  | 0  |
| 4   | 0  | 0  | 1  | 0  |
| 8   | 0  | 0  | 0  | 1  |

---

## Stage 3: Relay Driver (ULN2003)

The Q2, Q3, and Q4 output pins of the MT8870 are connected to input pins 5, 6, and 7
of the ULN2003 respectively. An LED with a 1K resistor is placed on each line as a
visual indicator of the signal state.

The ULN2003 is a Darlington transistor array capable of sinking up to 500 mA per
channel. When an input pin goes HIGH, the corresponding output pin goes LOW (open
collector), which activates the relay coil connected to it.

The 7805 voltage regulator takes 9V from the battery and outputs a stable 5V supply
to both the MT8870 and the ULN2003. The COM pin of the ULN2003 is connected to the
positive supply rail for flyback diode protection across the relay coils.

---

## Stage 4: Relay Switching and Load Control

Three 5V relays are connected to the three ULN2003 output channels. Each relay
controls one load:

| ULN2003 Output | Relay | Load  |
|----------------|-------|-------|
| Pin 16 (OUT5)  | 1     | Light |
| Pin 15 (OUT6)  | 2     | Fan   |
| Pin 14 (OUT7)  | 3     | TV    |

The relay contacts are wired to terminal blocks. When a relay activates, it closes
the circuit for the connected load, switching it ON. Pressing the same key again
deactivates the relay and switches the load OFF.

---

## Connection Summary

1. MT8870 IN+ and IN- connected to AUX wire from mobile phone.
2. 100K resistor on IN- pin; 0.1 uF capacitor at input for signal conditioning.
3. OSC pins 7 and 8 of MT8870 connected to 3.57 MHz crystal; each crystal pin
   grounded through a 22 pF capacitor.
4. Q2, Q3, Q4 outputs of MT8870 connected through 1K resistors and LEDs to
   ULN2003 input pins 5, 6, 7.
5. 7805 voltage regulator input from 9V battery; 5V output to VCC of MT8870
   and COM of ULN2003; also to relay coil pin 2 on all three relays.
6. ULN2003 output pins connected to relay coil pin 1.
7. Relay switching contacts connected to terminal blocks and load appliances.
