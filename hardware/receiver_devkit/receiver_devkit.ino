/* RELIEF-RELAY: original ESP32 DevKit + SX1276 868 MHz SPI LoRa module.
   Radio VCC->3.3V only, GND->GND, SCK->18, MISO->19, MOSI->23,
   NSS/CS->5, RESET->14, DIO0->26. Attach correct antenna first.
   Library: LoRa by Sandeep Mistry. Match the gateway frequency/settings.
*/
#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
const long RF_HZ=866000000L;
void setup(){
  Serial.begin(115200);delay(600);SPI.begin(18,19,23,5);LoRa.setPins(5,14,26);
  if(!LoRa.begin(RF_HZ)){Serial.println("ERROR|LoRa startup failed: check 3.3V and wiring");while(1)delay(1000);}
  LoRa.setSyncWord(0x12);Serial.println("READY|Receiver listening");
}
void loop(){
  int n=LoRa.parsePacket();if(!n)return;
  String msg="";
  while(LoRa.available() && msg.length()<120)msg+=(char)LoRa.read();
  if(msg.startsWith("RR1|"))Serial.println(msg);
  else Serial.println("IGNORED|Unexpected packet");
}
