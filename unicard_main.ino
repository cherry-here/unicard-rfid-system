/*
 * UNICARD - 4-in-1 RFID Vehicle Document System
 * Author: Mothi Charan Naik Desavath
 * Description: Single RFID card storing RC, DL, Insurance, PUC data
 * Hardware: Arduino Uno + MFRC522 RFID Module + I2C LCD
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Document block addresses on RFID card
#define BLOCK_RC        4   // Registration Certificate
#define BLOCK_DL        8   // Driving License
#define BLOCK_INSURANCE 12  // Insurance
#define BLOCK_PUC       16  // Pollution Under Control

MFRC522::MIFARE_Key key;

void setup() {
    Serial.begin(9600);
    SPI.begin();
    rfid.PCD_Init();
    lcd.init();
    lcd.backlight();
    lcd.print("UNICARD System");
    lcd.setCursor(0, 1);
    lcd.print("Scan your card");
    Serial.println("UNICARD System Ready");
    for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
}

void loop() {
    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

    Serial.println("\n--- Card Detected ---");
    lcd.clear();
    lcd.print("Card Found!");

    readDocument("RC", BLOCK_RC);
    readDocument("DL", BLOCK_DL);
    readDocument("Insurance", BLOCK_INSURANCE);
    readDocument("PUC", BLOCK_PUC);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    delay(2000);
}

void readDocument(String docName, byte block) {
    byte buffer[18];
    byte size = sizeof(buffer);
    MFRC522::StatusCode status;

    status = rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(rfid.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print(docName); Serial.println(": Auth Failed");
        return;
    }

    status = rfid.MIFARE_Read(block, buffer, &size);
    if (status == MFRC522::STATUS_OK) {
        Serial.print(docName + ": ");
        for (uint8_t i = 0; i < 16; i++) Serial.print((char)buffer[i]);
        Serial.println();
    }
}