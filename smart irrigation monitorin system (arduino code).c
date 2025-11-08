// Include necessary libraries
#include <HTTPClient.h>               // For making HTTP requests
#include <SPI.h>                      // For SPI communication (not directly used here)
#include <WiFi.h>                     // For Wi-Fi connection
#include <OneWire.h>                  // For 1-Wire communication (used by temp sensor)
#include <DallasTemperature.h>        // For DS18B20 temperature sensor

// Wi-Fi credentials
char ssid[] = "isreal A12";           // Wi-Fi SSID
char pass[] = "2@@623ko";             // Wi-Fi password

// PIR motion sensor
String pir = " ";                     // String to hold motion status
int pirPin = 12;                      // PIR sensor pin
int pirValue = 0;                     // Variable to store PIR sensor reading

// Soil moisture sensor
int SoilMoisturePin = 35;             // Analog pin for soil moisture sensor
int SoilMoisture = 0;                 // Raw moisture value
int SoilMoisturePercent = 0;          // Moisture level in percentage

// LDR 1 (Light sensor 1)
int ldr1_pin = 36;                    // Analog pin for LDR 1
int ldr1_value = 0;                   // Raw LDR 1 value
int ldr1Percent = 0;                  // Light intensity in percentage

// LDR 2 (Light sensor 2)
int ldr2_pin = 34;                    // Analog pin for LDR 2
int ldr2_value = 0;                   // Raw LDR 2 value
int ldr2Percent = 0;                  // Light intensity in percentage

// Temperature sensor
int tempPin = 25;                     // Pin connected to the DS18B20 sensor
int tempValue = 0;                    // Variable to store temperature reading
OneWire OneWirePin(tempPin);         // Set up one-wire instance on the tempPin
DallasTemperature sensor(&OneWirePin); // Pass oneWire reference to Dallas Temperature

void setup() {
  Serial.begin(115200);              // Start the Serial Monitor
  sensor.begin();                    // Initialize temperature sensor
  pinMode(pirPin, INPUT);            // Set PIR pin as input
  pinMode(ldr1_pin, INPUT);          // Set LDR1 pin as input
  pinMode(ldr2_pin, INPUT);          // Set LDR2 pin as input

  // Attempt to connect to Wi-Fi
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    WiFi.begin(ssid, pass);          // Start Wi-Fi connection
    delay(10000);                    // Wait 10 seconds before retry
  }
}

void loop() {
  // Visual separator for readings in Serial Monitor
  Serial.println("......................................................");
  Serial.println(" ");

  // --- Motion Sensor Section ---
  pirValue = digitalRead(pirPin);    // Read PIR sensor
  if (pirValue == HIGH) {
    Serial.println("Motion Detected!");
    pir = "Motion Detected!";
  } else {
    Serial.println("No Motion Detected!");
    pir = "No Motion Detected!";
  }

  // --- Soil Moisture Sensor Section ---
  SoilMoisture = analogRead(SoilMoisturePin);  // Read soil moisture sensor
  SoilMoisturePercent = map(SoilMoisture, 0, 4096, 100, 0); // Convert to %
  Serial.print("Soil Moisture Level IS: ");
  Serial.print(SoilMoisturePercent);
  Serial.println("%");

  // --- LDR 1 Section ---
  ldr1_value = analogRead(ldr1_pin);          // Read LDR 1
  ldr1Percent = map(ldr1_value, 0, 4096, 0, 100); // Convert to %
  Serial.println("light intensity (LDR1): " + String(ldr1Percent) + "%");

  // --- LDR 2 Section ---
  ldr2_value = analogRead(ldr2_pin);          // Read LDR 2
  ldr2Percent = map(ldr2_value, 0, 4096, 0, 100); // Convert to %
  Serial.println("light intensity (LDR2): " + String(ldr2Percent) + "%");

  // --- Temperature Sensor Section ---
  Serial.println("Requesting temperature...");
  sensor.requestTemperatures();              // Request temperature from sensor
  tempValue = sensor.getTempCByIndex(0);     // Read temperature in Celsius
  Serial.print("Temperature is: ");
  Serial.print(tempValue);
  Serial.println("*C");

  // --- Sending Data to Server ---
  if (WiFi.status() == WL_CONNECTED) {       // Check Wi-Fi connection
    Serial.println("Connected to Wi-Fi");
    delay(2000);                             // Delay before HTTP request
    Serial.println(WiFi.localIP());          // Print device IP address

    HTTPClient http;                         // Create HTTP client object
    http.begin("http://192.168.194.140:5000"); // Server URL
    http.addHeader("Content-Type", "text/plain"); // Set header for plain text

    // Prepare sensor data to send via POST request
    int temp = tempValue;
    int ldr1 = ldr1Percent;
    int ldr2 = ldr2Percent;
    int moisture = SoilMoisturePercent;

    // Construct POST body with sensor values
    int httpCode = http.POST("temperature=" + String(temp) +
                             "&ldr1=" + String(ldr1) +
                             "&ldr2=" + String(ldr2) +
                             "&pir=" + String(pir) +
                             "&moisture=" + String(moisture));

    // Handle server response
    if (httpCode > 0) {
      String response = http.getString();    // Get response from server
      Serial.println(response);              // Print server response
    } else {
      Serial.println("Error on HTTP request"); // Print error message
    }
    http.end(); // Close connection
  } else {
    Serial.println("Not connected to Wi-Fi"); // Wi-Fi not connected
  }

  delay(10000); // Wait 10 seconds before the next loop
  Serial.println(" ");
  Serial.println("......................................................");
}
