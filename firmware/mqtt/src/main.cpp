#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Audio.h>
#include <Detect.h>
#include <Light.h>
#include <System.h>
#include "secret.h"

const char* device_name = "tile-1";
const char* rootTopic = "music-light-tiles";
const char* stateTopic = "state";
const char* commandTopic = "command";

unsigned long lastMillis = 0;
unsigned long timeAlive = 0;
const unsigned long interval = 1000; // Uptime interval in milliseconds

void callback(char* topic, byte* payload, unsigned int length) {
  // Print the topic and payload for debugging purposes
  Serial.println("Message arrived in topic: " + String(topic));
  Serial.println("Message: " + String((char*)payload));
  
  // Direct message to correct handler
  if (String(topic) == (String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/system")) {
    // TODO: implement system control
    Serial.println("System control command received");
  } else if (String(topic) == (String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/audio")) {
    // TODO: implement audio control
    Serial.println("Audio control command received");
  } else if (String(topic) == (String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/light")) {
    // TODO: implement light control
    Serial.println("light control command received");
  } else {
    // Skip commands in unknown topics
    Serial.println("Command received in unknown topic, skipping...");
  }
}

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup() {
  // Set serial monitor baud rate
  Serial.begin(9600);

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
    if (client.connect(device_name)) { // TODO: implement user/pass and last will (https://pubsubclient.knolleary.net/api#connect) 
      Serial.println("Connected to MQTT broker as " + String(device_name));
      // TODO: publish online state (revive last will)
      client.subscribe((String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/#").c_str());
    } else {
      Serial.print("Failed to connect to MQTT broker, retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void loop() {
  // Keep the MQTT connection alive and process incoming messages
  client.loop();

  // Create state topic
  String outTopic = String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic);

  // Get the current time
  unsigned long currentMillis = millis();
  
  // Check if it's time to send new uptime message
  if (currentMillis - lastMillis >= interval) {
    // Save the current time
    lastMillis = currentMillis;

    // Increment the alive counter
    timeAlive++;

    // Publish the "outMessage"
    if (client.publish((outTopic + "/" + String("uptime")).c_str(), String(timeAlive).c_str())) {
      Serial.println("Uptime message sent, with value: " + String(timeAlive));
    } else {
      Serial.println("Failed to send uptime message");
    }
  }

  // wait for 10ms (to prevent flooding the broker)
  delay(10);
}