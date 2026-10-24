# RELIEF-RELAY — TONIGHT'S REAL SOFTWARE CHECKLIST
**Team Resonance. Beginner-friendly build. Single APK on all three Android phones.**

## PLEASE READ FIRST
The original native Android app already works and saves one request offline. **Keep it installed as backup.**
The `android/ReliefRelay_Team_Resonance_v2.aia` is an *updated project source*, not an APK; import it into MIT App Inventor, test it and build an APK. The new project is separate from the previously imported project.

The **warehouse server has been exercised in tests**. The new v2 `.aia` has been structurally checked but **not compiled by MIT App Inventor** in this environment; test its import/build tonight. If it fails, use your original known-working APK and the warehouse software. Don't overwrite the only working app!

## THE FIRST 30 MINUTES — WAREHOUSE LAPTOP

1. On the laptop you will actually take to the hackathon, install Python 3. Check `python --version` (Windows) or `python3 --version` (Mac/Linux). Install from https://www.python.org/downloads/ if needed.
2. Unzip this package and go into `warehouse`.
3. **Windows:** double-click `START_WINDOWS.bat`. If it closes unexpectedly, open Command Prompt in that folder and run `py server.py` (or `python server.py`).
4. **Mac/Linux:** open Terminal in the warehouse folder and run `python3 server.py`.
5. In the SAME laptop's browser, open `http://127.0.0.1:5000`.
6. Type `RR1|RDEMO101|YEL03|4|1|FLOOD` and tap **SIMULATE incoming message**. It must appear below. Click **Assign & reserve kit**.
7. Read its **expected grams**. Enter exactly that number into **SIMULATE weight**, tap the button, then **Verify checklist + measured weight**; confirm the kit checklist. Click **Mark dispatched**, then **Mark delivered**.
8. Congratulations: the dashboard + allocation + verification + delivery loop works **without internet**. The fake radio and weight sources are clearly labeled *SIMULATED*.

**If you see an error on launch**: make sure Python is installed and no other app is using port 5000. Do not install Streamlit or Flask; this project uses the Python standard library only.

## THE NEXT 60–90 MINUTES — UPDATE YOUR EXISTING PHONE APP

1. Open https://ai2.appinventor.mit.edu/ on laptop.
2. From **Projects → Import project (.aia) from my computer**, select `android/ReliefRelay_Team_Resonance_v2.aia`.
3. You should see a **new separate project**, named `ReliefRelayTeam`. Do not delete your earlier known-working `ReliefRelay` project.
4. Under the existing request form, this version adds **COPY CURRENT REQUEST**, **SHARE WITH NEARBY ANDROID PHONE**, **IMPORT RELAY REQUEST AND SAVE**, and **VIEW SAVED REQUESTS**.
5. `Connect → AI Companion` and scan its QR on your Lenovo tablet. Tap **SAVE REQUEST OFFLINE** with `YEL03`, `4`, `1`, `FLOOD`, and confirm the `RR1|...` appears.
6. Tap **COPY CURRENT REQUEST**, then paste it into a text editor or notes app. It should match the RR1 string exactly.
7. Copy that text and paste it into **IMPORT RELAY REQUEST AND SAVE** and confirm the app stores it. This is the *manual phone relay import* workflow.
8. Tap **VIEW SAVED REQUESTS** to check whether the saved records are there.
9. Test **SHARE WITH NEARBY ANDROID PHONE**. The Android sharing chooser should appear. When you have a second Android phone, test **Quick Share**. Quick Share support/availability varies by device. Avoid using messaging apps that require Internet for the offline demonstration.
10. Select **Build → Android App (.apk)**, download the new APK, and install it. KEEP the older app available as backup. Run the new APK with Wi-Fi/mobile data off and verify local persistence after a restart.

**If v2 fails to compile or import:** stop troubleshooting after ~25 minutes, use the original already-built APK and focus on the warehouse. Original APK is enough for two independent family requests; manual relay can be shown by sharing/typing the RR1 text into a volunteer phone when the v2 relay interface works.

## TOMORROW — INSTALL ON THREE ANDROID PHONES

- Export the **same v2 APK** to all three phones (USB cable/Quick Share/Drive beforehand). Phones do not need the source `.aia` or MIT Companion to run the installed APK.
- **Phone A:** Family A creates request `YEL03 / 4 people / 1 infant / FLOOD`; stores offline.
- **Phone B:** Field relay. Accepts the *same* RR1 text through offline Quick Share (if supported), pastes into v2's **IMPORT RELAY REQUEST**, saves offline; later pairs with `ReliefRelay-Gateway` and sends it over Bluetooth Classic.
- **Phone C:** Family C creates independent request `YEL04 / 2 people / 0 infants / QUAKE`. Connects to the gateway *after Phone B disconnects*, and sends. If the phone is needed for a delivery demo, it can also open the local driver's browser page when connected to the laptop hotspot.
- The field ESP32 supports **one Bluetooth SPP client at a time** in this basic sketch. Send packets **one phone at a time**. Keep unchanged IDs to demonstrate duplicate rejection.

**Important:** Quick Share uses proximity protocols that can include Wi-Fi Direct. You can have **no internet**, while Bluetooth and Wi-Fi radios remain enabled. Do not claim it is a proven always-on autonomous Bluetooth mesh. Device-to-device transfer is manual and hardware/OS-dependent.

## TOMORROW — ESP32 + SX1276 CONNECTION

You bought **regular ESP32 DevKit boards**, NOT integrated LILYGO LoRa boards. Use the `.ino` files inside:
- `hardware/gateway_devkit/gateway_devkit.ino` → ESP32 #1 + external SX1276 radio, Bluetooth gateway.
- `hardware/receiver_devkit/receiver_devkit.ino` → ESP32 #2 + external SX1276 radio, laptop USB receiver.
- `hardware/scale_devkit/scale_devkit.ino` → ESP32 #3 + HX711/load cell.

**The two external radio modules must be actual SX1276-family 868 MHz compatible SPI modules**. The common SX1278 RA-02 433 MHz and UART E32 modules will NOT work with the supplied frequency/driver as-is. Do not transmit on an unapproved frequency. Only 3.3V logic, correct antenna, and regulatory-compliant settings.

Both external LoRa modules wire identically:

| External SX1276 module | Original ESP32 DevKit |
|---|---|
| VCC | regulated 3.3V **not 5V** |
| GND | GND |
| SCK | GPIO 18 |
| MISO | GPIO 19 |
| MOSI | GPIO 23 |
| NSS / CS | GPIO 5 |
| RST / RESET | GPIO 14 |
| DIO0 | GPIO 26 |

**If the radio has different pin names/model, stop and check its datasheet and show a photo.** Mount an antenna before transmitting. Current drain can be too high for weak 3.3V rails; use a sufficiently rated regulated supply and a common GND. Check bare module/breakout form factors; some bare modules need soldering and are not breadboard-ready.

In Arduino IDE install **ESP32 by Espressif Systems**, **LoRa by Sandeep Mistry**, **HX711 by bogde** (scale only). Choose **ESP32 Dev Module**, correct USB port, baud **115200**.

For Bluetooth, use the **original ESP32-WROOM-32** or similar with Bluetooth Classic. **ESP32-S3/C3 do not support this BluetoothSerial/SPP workflow**.

### Hardware checkpoints in order
1. Receiver LoRa ESP32 on USB. After upload, Serial Monitor says `READY|Receiver listening`.
2. Gateway LoRa ESP32 on USB. After upload, Serial Monitor says `READY|Bluetooth = ReliefRelay-Gateway`.
3. Bluetooth pair an Android phone with `ReliefRelay-Gateway`; in the app tap **CONNECT BLUETOOTH GATEWAY**. Grant Bluetooth/Nearby devices permission.
4. Tap **SEND SAVED REQUEST**, then check receiver Serial Monitor: it should display exactly `RR1|...`.
5. CLOSE receiver Serial Monitor. In the warehouse folder: `python -m pip install pyserial` (once) then run `python server.py --radio COM5` replacing `COM5` with actual receiver USB port.
6. Open warehouse dashboard and resend a NEW request. It should appear as a real radio-received request.
7. Only then connect the calibrated HX711 station with `--scale COM6`, using a different USB port. Read `hardware/scale_devkit/scale_devkit.ino` for the calibration process.

### Driver page (OPTIONAL LOCAL NETWORK MODE)
For a mobile browser screen for a driver: connect the driver's Android phone and warehouse laptop to the SAME trusted local hotspot/Wi-Fi network (no Internet necessary). On warehouse laptop run `python server.py --lan` (or `py server.py --lan`). Find the laptop's local IPv4 address (Windows `ipconfig`; Mac `ifconfig` / Network settings). On the phone open `http://LAPTOP_IP:5000/driver`.

The Python dashboard defaults to localhost for safety. `--lan` exposes an **unauthenticated local demo**; use only a private trusted hotspot and never real personal data. Windows Firewall may ask permission. If it doesn't connect, show the delivery status on the warehouse laptop instead.

## HONEST JUDGES' DEMO (3 MINUTES)
1. Three phones and the warehouse laptop begin with mobile data turned off. Local radios as needed.
2. Family phone creates a request and saves it. Volunteer relay phone *manually* imports/shared it (experimental Quick Share).
3. Volunteer phone connects by Bluetooth Classic to field gateway and transmits.
4. LoRa receiver passes the compact request into the warehouse laptop.
5. Warehouse dashboard shows it, auto-proposes stock based on household need, assigns kit.
6. Human confirms each item, calibrated scale measures actual package mass; wrong weight is refused.
7. Mark dispatch and use optional driver browser page to confirm demonstration handover.
8. Explicitly explain remaining work: autonomous multi-hop phone mesh, guaranteed acknowledgements, encryption/privacy, regulatory approvals, field-ready power and actual disaster deployment.

### Protocol we MUST all keep unchanged
`RR1|request_id|zone|people|infants|disaster` followed by newline over Bluetooth Classic, e.g. `RR1|RDEMO101|YEL03|4|1|FLOOD`. Each request ID must remain the SAME across relays and resend attempts; a genuinely different household request needs a different ID.

### Stop conditions / fallbacks
- If app v2 import/build takes too long → **use your confirmed working v1 APK**.
- If Bluetooth app-to-ESP32 connection fails → use **Serial Bluetooth Terminal** to send `RR1|...` and show that the firmware/LoRa/warehouse works.
- If LoRa hardware fails → use dashboard **SIMULATE incoming message** but clearly identify it as simulation.
- If scale calibration fails → use **SIMULATE weight** and clearly identify it as simulation.

No real names, phone numbers, home addresses, detailed medical needs or sensitive personal data should be carried on the demo's **unencrypted** LoRa link.
