/*
 Relief-Relay DEMO FALLBACK — PHONE -> ESP32 BLUETOOTH CLASSIC -> LAPTOP USB.
 This sketch is only for an original ESP32-WROOM-32/ESP32 DevKit with Bluetooth Classic.
 It DOES NOT use LoRa and is not a claim of long-distance or multi-hop operation.
 It gives the team a real, independently testable hardware/software link
 when LoRa modules, radio wiring, or antennas are not ready.

 USB: plug ESP32 directly into warehouse laptop.
 App: pair to Bluetooth name ReliefRelay-Gateway, then send an RR1|... request.
 Laptop: run `python server.py --radio COMx` after installing pyserial.
 Serial baud 115200. All incoming complete requests are printed as a single line.
*/
#include <Arduino.h>
#include <BluetoothSerial.h>
#if !defined(CONFIG_IDF_TARGET_ESP32)
#error "Requires original ESP32 supporting Bluetooth Classic SPP"
#endif

BluetoothSerial bt;
String incoming;

bool looksLikePacket(const String& str) {
  if (!str.startsWith("RR1|") || str.length() > 120) return false;
  int bars = 0;
  for (size_t i = 0; i < str.length(); i++) {
    char c = str[i];
    if (c == '|') bars++;
    if (c < 32 || c > 126) return false;
  }
  return bars == 5;
}

void setup() {
  Serial.begin(115200);
  delay(300);
  if (!bt.begin("ReliefRelay-Gateway")) {
    Serial.println("ERROR|Bluetooth start failed");
    while (true) delay(1000);
  }
  Serial.println("READY|ESP32 Bluetooth-to-USB bridge (NO LORA)");
}

void loop() {
  while (bt.available()) {
    char c = (char)bt.read();
    if (c == '\r') continue;
    if (c == '\n') {
      incoming.trim();
      if (looksLikePacket(incoming)) {
        Serial.println(incoming);            // warehouse ingest reads lines starting RR1|
        bt.println("USB_FORWARDED|Warehouse receipt unconfirmed");
      } else if (incoming.length()) {
        bt.println("ERROR|Invalid RR1 packet");
      }
      incoming = "";
    } else if (incoming.length() < 125) {
      incoming += c;
    } else {
      incoming = "";
      bt.println("ERROR|Message too long");
    }
  }
  delay(5);
}
