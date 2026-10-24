// Relief-Relay load-cell station (separate regular ORIGINAL ESP32 DevKit).
// Install Arduino library: HX711 by bogde.
// HX711 VCC -> ESP32 3V3 (ONLY if your HX711 breakout supports 3.3 V)
// HX711 GND -> GND, DOUT -> GPIO32, SCK -> GPIO33.
// Load cell: connect E+/E-/A+/A- according to its wire colour datasheet.
// Calibrate first: use a known weight and replace CALIBRATION_RAW_PER_GRAM.
#include <Arduino.h>
#include "HX711.h"

HX711 scale;
constexpr uint8_t DATA_PIN = 32;
constexpr uint8_t CLOCK_PIN = 33;
constexpr float CALIBRATION_RAW_PER_GRAM = 1.0f; // PLACEHOLDER: NOT calibrated!

void setup() {
  Serial.begin(115200);
  scale.begin(DATA_PIN, CLOCK_PIN);
  Serial.println("INFO|Remove all load; taring in 2 seconds");
  delay(2000);
  if (!scale.wait_ready_timeout(3000)) {
    Serial.println("ERROR|HX711 not detected");
    return;
  }
  scale.set_scale(CALIBRATION_RAW_PER_GRAM);
  scale.tare(10);
  Serial.println("INFO|Tared. Calibrate before using displayed gram weights.");
  Serial.println("INFO|Enter C in Serial Monitor to read raw calibration value.");
}

void loop() {
  if (Serial.available()) {
    char c = static_cast<char>(Serial.read());
    if (c == 't' || c == 'T') {
      scale.tare(10);
      Serial.println("INFO|Scale tared");
    }
    if (c == 'c' || c == 'C') {
      // With set_scale(1) and empty container tared, raw counts == get_value().
      Serial.print("RAW_DIFFERENCE_FOR_KNOWN_WEIGHT|");
      Serial.println(scale.get_value(10), 0);
      Serial.println("INFO|Divide the raw difference by known mass in grams; replace calibration constant and re-upload.");
    }
  }
  if (scale.wait_ready_timeout(500)) {
    // Do NOT rely on this number until calibration is finished.
    Serial.print("WEIGHT|");
    Serial.println(scale.get_units(5), 1);
  }
  delay(500);
}
