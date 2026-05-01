# UNICARD - 4-in-1 RFID Vehicle Document System

> Consolidating RC, DL, Insurance and PUC into a single RFID card

## Problem Statement
Vehicle owners carry multiple documents (RC, Driving License, Insurance, PUC). UNICARD stores all four on one RFID card - reducing paperwork and enabling instant digital verification.

## Hardware Required
| Component | Quantity |
|-----------|----------|
| Arduino Uno | 1 |
| MFRC522 RFID Module | 1 |
| RFID Card/Tag (1KB) | 1 |
| I2C LCD 16x2 | 1 |
| Jumper Wires | - |

## Wiring
| MFRC522 Pin | Arduino Pin |
|-------------|-------------|
| SDA | 10 |
| SCK | 13 |
| MOSI | 11 |
| MISO | 12 |
| RST | 9 |
| 3.3V | 3.3V |
| GND | GND |

## Libraries Required
- MFRC522 by GithubCommunity
- LiquidCrystal_I2C by Frank de Brabander

Install via Arduino IDE > Tools > Manage Libraries

## How It Works
1. Scan RFID card > system reads 4 data blocks
2. Each block stores one document key info (number + expiry)
3. Data displayed on LCD + Serial Monitor
4. Traffic police can verify all docs with one scan

## Block Memory Map
| Block | Document | Data Stored |
|-------|----------|-------------|
| 4 | RC | Vehicle Reg Number + Valid Till |
| 8 | DL | License Number + Valid Till |
| 12 | Insurance | Policy Number + Expiry |
| 16 | PUC | Certificate No + Expiry |

## Author
**Mothi Charan Naik Desavath** - Embedded Systems Engineer