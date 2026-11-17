# Coding Canvas v5 — LEGO Education-style Word Blocks

This independent classroom prototype uses Blockly to provide a visual programming palette based on screenshots of the LEGO Education Word Blocks interface. It is **not** an official LEGO Education product or an exact copy of its underlying software.

## Launch
1. Enable GitHub Pages under Settings → Pages, deploy from `main` / `(root)`.
2. Open https://marklockett-hub.github.io/CodingCanvas/ or serve locally with `python -m http.server 8765 --bind 127.0.0.1`.
3. Choose **Simulator** to try supported movement blocks. Use **Save project** to download your Blockly project.

## Palette
- Single Motor: 11 blocks
- Double Motor movement: 9 blocks
- Double Motor independent motors: 11 blocks
- Motion Sensor: 5 blocks
- Colour Sensor: 6 blocks
- Controller: 4 blocks
- Events: 6 blocks
- Control: 8 blocks
- Sound: 4 blocks
- Operators: 7 blocks
- Timer: 2 blocks
- Text: 7 blocks
- Blockly Variables, Lists and My Blocks (procedures)
- AI & Simulation: 5 existing prototype blocks

## Important limitations
**Palette availability is not the same as runtime support.** The newly added blocks have editable fields and a Python preview, but most are placeholders until their behaviour is implemented and tested. Some generated Python is intentionally illustrative, not runnable. The simulator currently runs the earlier `drive`, `turn`, basic repeat/if and sensor/controller conditions. It does not yet execute all v5 LEGO-style blocks. The existing local `bridge.py` remains unchanged and supports only bounded drive/turn actions on the Double Motor; physical Single Motor, Colour Sensor, Controller, Motion Sensor, sounds and events are not implemented. The STOP button is not a guaranteed emergency stop.

The editor depends on the Blockly CDN and requires internet connectivity for the initial load. Camera classification uses separate third-party CDNs and is experimental.

## Testing
The repository upload was verified through GitHub. Full browser behaviour, individual Blockly blocks and physical LEGO hardware have **not** been end-to-end tested.

## Next engineering tasks
1. Browser smoke-test block creation, serialization and Python preview.
2. Add a safe block interpreter for each category with simulated hardware state.
3. Verify official LEGO Education Python APIs before adding hardware mappings.
4. Add unit tests and explicit unsupported-block warnings before physical runs.
