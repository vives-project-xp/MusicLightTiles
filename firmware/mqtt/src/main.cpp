#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <SRAM.h>
#include "secret.h"

SRAM sram(4, SRAM_1024);

unsigned long lastMillis = 0;
unsigned long timeAlive = 0;
unsigned long cycle = 0;
const unsigned long interval = 1000; // Send the message every 1 second

void callback(char* topic, byte* payload, unsigned int length) {
  sram.seek(1);

  // do something with the message
  for (uint8_t i = 0; i < length; i++) {
    Serial.write(sram.read());
  }
  Serial.println();

  // Reset position for the next message to be stored
  sram.seek(1);
}

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup() {
  Serial.begin(9600);
  sram.begin();
  sram.seek(1);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Set MQTT server
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Connect to MQTT broker
  while (!client.connected()) {
    if (client.connect("esp32Client")) {
      Serial.println("Connected to MQTT broker");
      client.publish(outTopic, "hello world");
      client.subscribe(inTopic);
    } else {
      Serial.print("Failed to connect to MQTT broker, retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void loop() {
  client.loop();

  unsigned long currentMillis = millis();

  // increment cycle counter
  cycle++;
  
  // Check if it's time to send the message
  if (currentMillis - lastMillis >= interval) {
    // Save the current time
    lastMillis = currentMillis;

    // Increment the alive counter
    timeAlive++;

    // Format the message (json)
    String outMessage = "{\"timeAlive\": " + String(timeAlive) + "}";
    char outMessageBuffer[50];
    outMessage.toCharArray(outMessageBuffer, 50);

    // Publish the "outMessage" 
    if (client.publish(outTopic, outMessageBuffer)) {
      Serial.println("Message sent");
    } else {
      Serial.println("Failed to send message");
    }
  }

  // publish current cycle
  client.publish("musiclighttiles/cycle", String(cycle).c_str());
}