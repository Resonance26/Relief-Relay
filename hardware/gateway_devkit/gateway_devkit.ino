/* RELIEF-RELAY: regular ORIGINAL ESP32-WROOM-32 DevKit + SX1276 868 MHz SPI LoRa module.
   Arduino IDE libraries: LoRa by Sandeep Mistry; BluetoothSerial included in ESP32 core.
   Pin connections (3.3V LOGIC ONLY):
   Radio VCC  -> ESP32 3V3 (adequately regulated 3.3V power; verify module current)
   Radio GND  -> ESP32 GND
   Radio SCK  -> GPIO18
   Radio MISO -> GPIO19
   Radio MOSI -> GPIO23
   Radio NSS/CS -> GPIO5
   Radio RESET -> GPIO14
   Radio DIO0 -> GPIO26
   The module must be SX1276-family 868 MHz SPI type, not 433MHz SX1278, SX1262, or UART E32.
   Connect compatible antenna before transmitting. Follow local radio regulatory requirements.
*/
#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <BluetoothSerial.h>
#if !defined(CONFIG_IDF_TARGET_ESP32)
#error "Bluetooth Classic requires ORIGINAL ESP32; not ESP32-S3/C3!"
#endif
BluetoothSerial bt;
const long RF_HZ = 866000000L;
const int PIN_CS=5,PIN_RESET=14,PIN_DIO0=26;
String fromBt="", fromUsb="";

bool valid(String s) {
  s.trim();
  if (!s.startsWith("RR1|") || s.length()>120) return false;
  int bars=0;
  for (unsigned int i=0;i<s.length();i++) {
    if (s[i]=='|') bars++;
    if (s[i]<32 || s[i]>126) return false;
  }
  return bars==5 || bars==8;  // old packet: 6 fields; V4: 9 fields
}
void transmit(String msg) {
  msg.trim();
  if (!valid(msg)) { Serial.println("ERROR|Invalid request");bt.println("ERROR|Invalid request");return; }
  if (!LoRa.beginPacket()) { Serial.println("ERROR|Radio busy");bt.println("ERROR|Radio busy");return; }
  LoRa.print(msg);
  bool sent=(LoRa.endPacket()==1);
  Serial.println(String(sent?"TX|":"FAILED|")+msg);
  bt.println(sent?"RADIO_SENT|Warehouse receipt NOT confirmed":"ERROR|LoRa TX failed");
}
void feed(Stream &src, String &acc) {
  while (src.available()) {
    char c=(char)src.read();
    if(c=='\n') { if(acc.length())transmit(acc);acc=""; }
    else if(c!='\r') { if(acc.length()<125)acc+=c;else acc=""; }
  }
}
void setup(){
  Serial.begin(115200);delay(600);
  SPI.begin(18,19,23,5);
  LoRa.setPins(PIN_CS,PIN_RESET,PIN_DIO0);
  if(!LoRa.begin(RF_HZ)){Serial.println("ERROR|LoRa startup. Check SX1276 SPI wiring and 3.3V supply.");while(1)delay(1000);}
  LoRa.setSyncWord(0x12);LoRa.setTxPower(10);
  if(!bt.begin("ReliefRelay-Gateway")){Serial.println("ERROR|Bluetooth Serial failed");while(1)delay(1000);}
  Serial.println("READY|Bluetooth = ReliefRelay-Gateway; send RR1|... then newline");
}
void loop(){feed(bt,fromBt);feed(Serial,fromUsb);delay(5);}
