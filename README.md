# Coding Canvas v3: hardware abstraction layer

This release introduces a common **command representation** used by the browser simulator and the LEGO hardware adapter. Blockly is compiled into a bounded list of `drive` and `turn` actions. The target selector chooses the backend; the same blocks run in both.

## Start simulator (Windows, macOS, Chromebook)

Host the directory on localhost or HTTPS. For local use run `python -m http.server 8765 --bind 127.0.0.1` then open **http://localhost:8765**. Blockly and the optional AI model require an internet connection. Camera needs localhost or HTTPS.

## Start LEGO bridge (Windows or macOS)

Install **Python 3.14+** and run `python -m pip install legoeducation`. From this folder run `python bridge.py` in a second terminal. Open the browser app at **http://localhost:8765**, enter the connection card colour and serial, click Connect, select Real LEGO hardware and click Run program.

**Hardware bridge limitations:** The bridge is strictly bound to `127.0.0.1` and only permits browser requests originating at `http://localhost:8765`. It does not execute student-generated Python. Commands are validated and limited to 20 actions, maximum 360 motor degrees per drive, 60% drive speed and 180 degrees per turn. STOP is best-effort and may not interrupt a blocking Bluetooth call. Never treat it as a safety-rated emergency stop. Test with wheels raised and keep a way to physically remove power. Do not expose the bridge to a school network or the internet.

## How the HAL works

- **Blockly** → `allCommands()` expands basic blocks, loops and conditional blocks into a bounded command array.
- **Simulator backend** → animates the command array on the canvas.
- **LEGO backend** → sends the same array to the local Python bridge (`POST /execute`). The bridge maps commands to the documented `DoubleMotor.movement_move_for_degrees` and `movement_turn_for_degrees` API.
- **Camera** → optional MobileNet detection feeds the `snack_detected` conditional in both backends, but detection is sampled before running. This is not a continuous feedback loop.

## Mixed device deployment

Chromebooks can run the simulator and AI camera through a school-hosted HTTPS site. The official LEGO Python API cannot access BLE from Chromebook Linux containers, so hardware mode is limited to the computer running the local bridge. A school-wide hardware gateway would require a separately designed authenticated service and network safety review.

## Known issues

The simulator is approximate and does not model real physics. Python output is illustrative pseudocode, not a directly runnable LEGO program. The generic MobileNet classifier may not recognise snacks reliably. The current Blockly interpreter handles a restricted set of blocks and simple conditions. Hardware connection, BLE latency and motor direction have not been tested on actual devices.

Official API: https://github.com/LEGO/LEGOEducation