# Relief-Relay V4 — Senior Citizens & Medicines

## Start with Android
1. Open MIT App Inventor (ai2.appinventor.mit.edu).
2. Projects > Import project (.aia) from my computer.
3. Select `android/ReliefRelay_Team_Resonance_v4_Seniors_Medicines.aia`.
4. Open **Blocks**. If you see a red error, STOP and keep your original working app.
5. Build > Android App (.apk) and install on the two Android test phones.
6. Set Language to Kannada/Hindi/English. Fill area YEL03, people 4, infants 1, seniors 2, medical support REGULAR and note INHALER, disaster FLOOD.
7. Save offline. Inspect generated message. Expected structure:
   `RR1|R<unique ID>|YEL03|4|1|FLOOD|2|REGULAR|INHALER`
8. Do not type personal names, diagnoses or separators (|) into medical notes; use up to 24 English letters/numbers/spaces.
9. On Phone 2, use the SHARE or show-text/import manual relay actions. This is not automatic Bluetooth mesh.

## Start new V4 warehouse dashboard (on Windows)
1. Stop any old warehouse server in its black Command Prompt window with Ctrl+C; V4 and previous versions use the same port 5000.
2. Double-click `warehouse/START_WINDOWS.bat` in THIS V4 folder.
3. Open `http://127.0.0.1:5000` on the laptop.
4. Click SIMULATE incoming message for the V4 sample packet (`RDEMO002`).
5. Check warehouse displays **2 seniors**, **REGULAR**, **INHALER**, flags **HUMAN REVIEW REQUIRED**, and suggests a **non-medical senior support kit**. Medical drugs are NEVER automatically allocated.
6. Assign supplies and simulate weight only as clearly labelled demo actions.

## Connecting hardware later
- Re-upload `hardware/gateway_devkit/gateway_devkit.ino` to Gateway ESP32, which now accepts both old 6-field and new 9-field packets.
- The LoRa receiver firmware forwards RR1 packets unchanged.
- To ingest real radio over USB you will need pyserial (`python -m pip install pyserial`) and `python warehouse/server.py --radio COMx` with the correct COM port.
- Don't claim radio receipt unless the receiver/laptop proves it; never claim warehouse delivery from a send-only acknowledgement.

## Safety and privacy
This is a hackathon prototype with no encrypted transport or access control. Use synthetic data only. Do not send identifying medical data over Bluetooth/LoRa during the demo. All medical needs require human assessment; quantities of essential supplies are illustrative only.
