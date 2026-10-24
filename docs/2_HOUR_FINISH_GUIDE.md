# RELIEF-RELAY — TWO-HOUR SOFTWARE FINISH

Team Resonance · HACK4SDG · 24 October 2026

## The only acceptable finished scope

- One Android APK used on two teammates' phones. Each phone can create a compact request, persist it in TinyDB, copy/share and manually import a message. Language selector: English / Kannada / Hindi.
- Windows warehouse dashboard at http://127.0.0.1:5000, with packet intake, deduplication, supply allocation, physical-checklist prompt, scale input, dispatch and delivery tracking.
- One actual tested path to get a RR1 packet into the warehouse, ideally Bluetooth -> LoRa -> USB receiver. If radio is not ready, the USB-connected ESP32 Bluetooth bridge is an explicitly labeled HARDWARE FALLBACK. Simulate if neither path works.
- GitHub repository with source and instructions; one laptop backup of an exported .aia and built .apk.

## Immediate actions: two parallel teammates

**Teammate A — Mobile app (first 30 minutes):**
1. Visit https://ai2.appinventor.mit.edu/ using the venue laptop.
2. Import `android/ReliefRelay_Team_Resonance_v3_Languages.aia` from Projects → Import project (.aia).
3. Open **Blocks**: if any red blocks-loading warning appears, STOP and use the original V1, or last known-buildable APK. Do not pretend an uncompiled file is working.
4. Connect → AI Companion, check `SpinnerLanguage` can select English, Kannada and Hindi. Save a sample `YEL03 / 4 people / 1 infant / FLOOD` request and confirm `RR1|...` appears.
5. Test Copy and Share. Share is a **manual** Android share sheet; do not promise autonomous phone mesh.
6. Build → Android App (.apk). Install the APK on Phone 1. Close and reopen with mobile data off to verify TinyDB persisted.
7. Send APK as a document or via Quick Share to Phone 2. Install and test import with the identical request ID.

**Teammate B — Warehouse (first 20 minutes):**
1. Open `warehouse/START_WINDOWS.bat` and keep the black terminal window open.
2. Open `http://127.0.0.1:5000` in Chrome.
3. Use a **new** ID, e.g. `RR1|RHACK2401|YEL03|4|1|FLOOD`. Click `SIMULATE incoming message`. Duplicate ID must not add another request.
4. Click `Assign & reserve kit`. Confirm inventory decreases and expected package weight appears.
5. Enter the expected grams under SIMULATE weight. Immediately click `Verify checklist + measured weight`. For software-only testing, don't claim the physical checklist was completed. If physical demo props were checked, confirm; otherwise demonstrate the rejection by canceling.
6. Continue dispatch/delivery only if verified. If no physical test is available, narrate statuses without falsely claiming real delivery.

**Teammate C — Hardware bridge (next 45–60 minutes):**
1. Install Arduino IDE and `ESP32 by Espressif Systems` board package.
2. Original ESP32-WROOM-32 DevKit: choose ESP32 Dev Module, USB COM port and 115200 baud. Upload `hardware/gateway_devkit/gateway_direct_usb_no_lora.ino`.
3. Pair an Android phone with `ReliefRelay-Gateway` in Android Bluetooth Settings. On the app choose Connect Bluetooth Gateway and Send Saved Request. The incoming code must start `RR1|` and end with newline.
4. The USB-connected ESP32 should print that line in Serial Monitor. **Close Serial Monitor** (only one app may own the USB COM port).
5. In the warehouse folder run `python -m pip install pyserial` once, then run `python server.py --radio COMx` using your *actual* COM port. Keep the server window open.
6. Create a *new* family request ID and send from Android. Warehouse should show it with no use of `SIMULATE incoming message`.
7. Clearly label this demo `PHONE → BLUETOOTH → ESP32 → LAPTOP USB`, **NOT** LoRa or phone mesh. To implement actual LoRa, use paired SX1276 radios and the regular `gateway_devkit.ino` / `receiver_devkit.ino` files after verifying parts and wiring.

## Safe failure options

If `v3` red-errors or cannot build, keep the original V1 APK (already tested to save offline) and demo request handling using a copied RR1 message. Don't waste the full two-hour sprint troubleshooting a non-essential multilingual upgrade.

If Bluetooth fails, the warehouse **SIMULATE incoming message** button still demonstrates the allocation pipeline. Call it a software simulation, not actual received radio traffic.

If ESP32 direct USB passes but LoRa fails, present the direct USB link as genuine Bluetooth/serial hardware proof and LoRa as an unfinished planned module.

If load-cell readings aren't calibrated, `SIMULATE weight` is only for software verification; avoid claims of real weight detection.

## Message protocol (unchanged by language)

`RR1|requestID|zoneCode|peopleCount|infantCount|disaster`

Example: `RR1|RHACK2401|YEL03|4|1|FLOOD`

Valid disaster codes: `FLOOD`, `QUAKE`, `CYCLONE`. New requests need unique IDs; a relayed duplicate must retain its ID. No real medical or identifying information on the unencrypted radio demo.

## GitHub upload guidance

- On laptop, repository: https://github.com/Resonance26/Relief-Relay
- Upload **source**: Android `.aia`, `warehouse/server.py`, the two HTML templates, `.ino` sketches, `tests`, and this guide.
- Do **not** upload the Python database `relief_relay.sqlite3`, `-wal`, `-shm`, `__pycache__`, private names/phone numbers, login tokens, or any unlicensed third-party binary.
- `README.md` in the repository must distinguish `COMPLETE & TESTED`, `READY BUT NOT TESTED ON HARDWARE`, `SIMULATED`, `FUTURE`.

## Priority demo route (three minutes)

1. Family Phone A: choose Kannada or Hindi, save offline; show `RR1` code.
2. Phone B: manual share/import without internet; show unchanged request ID.
3. If working: Phone B Bluetooth sends to ESP32, then LoRa or USB bridge to laptop. Otherwise use a clearly labeled simulation on warehouse.
4. Warehouse: incoming family request → proposed kit → inventory decrement → physical checklist and measured weight (actual or explicitly simulated) → dispatched/delivered (demo statuses only).
5. Explain limitations: automatic phone relay, radio coverage, end-to-end acknowledgments, privacy/encryption and operational deployment are future work.
