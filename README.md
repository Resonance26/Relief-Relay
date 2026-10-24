# Relief-Relay
# 🌍 RELIEF-RELAY
### *When Networks Fail, Relief Shouldn't.*

**Team Resonance | HACK4SDG 2026**

## 🚨 The Problem

During natural disasters, communication networks often fail, leaving affected families unable to request essential supplies.

Relief organisations also struggle to identify household-specific requirements, manage limited resources, and coordinate timely distribution.

## 💡 Our Solution

**Relief-Relay** is an offline-first disaster-relief communication and resource-management system that connects affected families with relief centres using **Bluetooth, LoRa, and intelligent resource allocation**.

Our objective is to ensure that essential needs can be communicated and coordinated even when conventional networks are unavailable.

## ✨ Key Features

- **Offline Emergency Requests:** Families can register their needs without internet connectivity.
- **Multilingual Accessibility:** English and Hindi as core languages, with Kannada currently supported and provision for additional Indian regional languages.
- **Bluetooth & LoRa Communication:** Enables short-range and longer-distance transmission through compatible devices and gateways.
- **Personalised Relief Kits:** Supplies allocated based on household size, infants, senior citizens and disaster-specific requirements.
- **Medical Assistance Requests:** Identifies medicine and healthcare requirements for human review.
- **Warehouse Management:** Tracks incoming requests, available inventory and relief-kit allocation.
- **Smart Weight Verification:** Uses an ESP32, HX711 and load cell to support package verification alongside manual item checks.

## ⚙️ System Architecture

```text
Disaster-Affected Family
          ↓
Relief-Relay Android App
          ↓
Bluetooth Communication
          ↓
ESP32 + LoRa Transmitter
          ↓
ESP32 + LoRa Receiver
          ↓
Warehouse Dashboard
          ↓
Need-Based Resource Allocation
          ↓
Smart Packing Verification
          ↓
Relief Distribution
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Mobile application | MIT App Inventor, Android |
| Offline storage | TinyDB |
| Short-range communication | Bluetooth |
| Long-range communication | LoRa + ESP32 |
| Warehouse software | Python, HTML, CSS, SQLite |
| Weight verification | ESP32, HX711, Load Cell |
| Collaboration | GitHub |

## 🧪 Prototype Status

**Developed and tested:**
- Offline Android request creation and storage
- English, Hindi and Kannada interfaces
- Senior-citizen and medicine requirement fields
- Warehouse request processing and inventory allocation
- Simulated package-weight verification

**Under development:**
- End-to-end Bluetooth–LoRa hardware integration
- Physical load-cell verification
- Automated phone-to-phone relaying

The driver interface is a prototype demonstration, not a verified delivery-tracking service.

## 🌱 Sustainable Development Goals

**Primary: SDG 11 — Sustainable Cities and Communities**

Relief-Relay supports disaster resilience by improving communication and relief coordination, especially for vulnerable households.

**Supporting SDGs:**
- SDG 3 — Good Health and Well-Being
- SDG 9 — Industry, Innovation and Infrastructure
- SDG 2 — Zero Hunger

## 💰 Sustainability

Relief-Relay is designed to be **free for disaster-affected families**.

Potential deployment partners include NGOs, government disaster-management agencies and CSR-funded organisations.

## 🔮 Future Scope

- Automatic Bluetooth mesh-style relaying
- Expanded Indian regional-language support
- Secure request transmission and acknowledgements
- Improved emergency prioritisation and stock management
- Driver coordination and delivery confirmation
- Larger-scale deployment through community LoRa gateways

## 👥 About Us

**Team Resonance** is developing Relief-Relay for **HACK4SDG 2026**, combining electronics, communication technology and software to address real-world humanitarian challenges.

*Relief-Relay is an experimental student prototype. It is not a certified emergency service, and medical requests require qualified human review.*

---

### ❤️ When Networks Fail, Relief Shouldn't.
**Built by Team Resonance.**

