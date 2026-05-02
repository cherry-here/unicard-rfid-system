# Unicard: All-in-One Vehicle Document Smart Card

> Independently conceived multi-stakeholder RFID smart card replacing 4 physical vehicle documents (RC, DL, Insurance, PUC) with role-based access, encrypted cloud backend scannable in under 2 seconds.

## Overview

Unicard is an independently conceived and fully implemented RFID-based smart card system that replaces four physical vehicle documents with a single scannable card. Built on a Raspberry Pi running a Python Flask web server backed by a MySQL database, the system was written end-to-end: backend logic, all HTML templates, and the RFID hardware interface.

When a user taps their NodeMCU-attached RFID card, the device calls the /nodemcu_scan endpoint. The backend verifies a Fernet-encrypted rolling token stored on the server -- preventing replay attacks. If the RFID tag is new, the user is redirected to register (name, mobile, license number, password + 4 security questions). On return visits, the user enters their password and reaches their personal dashboard showing all linked vehicles and insurance records.

Three stakeholder roles operate via a separate login portal: Manufacturers can register vehicles (VIN, model, RC number) against any RFID tag; Insurers can attach insurance policies (policy number + expiry date); Police can request an OTP sent to the vehicle owner's registered mobile, verify it within a 5-minute window, and view the owner's full profile -- name, license, all vehicles, and all insurance -- regardless of which company added each record. All stakeholder passwords are SHA-256 hashed. The system is fully functional as a prototype running on local hardware.

## Key Metrics
| Metric | Value |
|--------|-------|
| Scan Time | < 2 seconds |
| Documents Stored | 4-in-1 (RC, DL, Insurance, PUC) |
| Stakeholder Roles | 3 (Manufacturer, Insurer, Police) |
| Auth Method | Fernet Rolling Token |

## Hardware Connection Table

| Component | Connected To | Interface | Notes |
|-----------|-------------|-----------|-------|
| MFRC522 RFID Reader | NodeMCU GPIO | SPI (D2/D5/D6/D7) | 13.56 MHz, reads MIFARE cards |
| NodeMCU (ESP8266) | Raspberry Pi | WiFi HTTP GET | Calls /nodemcu_scan endpoint |
| Raspberry Pi 4 | MySQL Database | USB/Ethernet | Flask server on port 5000 |
| USB RFID Reader | Raspberry Pi | USB | Optional admin reader |

### NodeMCU -> MFRC522 Pinout
| MFRC522 Pin | NodeMCU Pin | Function |
|-------------|-------------|----------|
| SDA (SS) | D2 (GPIO4) | SPI Slave Select |
| SCK | D5 (GPIO14) | SPI Clock |
| MOSI | D7 (GPIO13) | SPI Master Out |
| MISO | D6 (GPIO12) | SPI Master In |
| RST | D1 (GPIO5) | Reset |
| 3.3V | 3.3V | Power |
| GND | GND | Ground |

## Tech Stack
- **Backend**: Python Flask + MySQL
- **Security**: Fernet encryption, SHA-256 hashing, rolling tokens
- **Hardware**: Raspberry Pi 4 + NodeMCU (ESP8266) + MFRC522
- **Protocol**: SPI (RFID), WiFi HTTP (NodeMCU->Pi)

## System Flow
1. User taps RFID card on NodeMCU reader
2. NodeMCU calls `/nodemcu_scan?uid=<UID>&token=<token>`
3. Backend verifies Fernet token (prevents replay attacks)
4. New users -> registration form; returning users -> login
5. Dashboard shows all linked vehicles and insurance records
6. Stakeholders access separate portal for their operations

## Author
**Mothi Charan Naik Desavath** -- Embedded Systems Engineer