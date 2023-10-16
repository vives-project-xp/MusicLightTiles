#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Tile.h>
#include "secret.h"

const char* rootTopic = "music-light-tiles";
const char* stateTopic = "state";
const char* commandTopic = "command";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Define global constants
#define FW_VERSION "1.0.0"
#define HW_VERSION "1.0.0"

// Declare global variables
char* device_name;

// Create objects of tile class
Tile tile;

// Forward declaration of callback function
void callback(char* topic, byte* payload, unsigned int length);

// Setup function
void setup() {
  // Set device name
  device_name = "Tile-1"; // TODO: implement random number generator and check if name is already in use

  // Set serial monitor baud rate for debugging purposes
  Serial.begin(9600);

  // Set device name as hostname
  WiFi.setHostname(device_name);

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
      client.subscribe((String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic)).c_str());
    } else {
      Serial.print("Failed to connect to MQTT broker, retrying in 5 seconds...");
      delay(5000);
    }
  }

  // Construct new tile object
  tile = Tile();
}

// Loop function
void loop() {
  // Keep the MQTT connection alive and process incoming messages
  client.loop();

  // Update tile state
  tile.updateState();

  // Publish tile state to MQTT broker if state has changed
  if (tile.stateChanged()) {
   client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic)).c_str(), tile.serializeOutput().c_str());
  }
}

// Callback function
void callback(char* topic, byte* payload, unsigned int length) {
  // Print the topic and payload for debugging purposes
  Serial.println("Message arrived in topic: " + String(topic));
  Serial.println("Message: " + String((char*)payload));

  // TODO: Validate payload
  
  // Pass the message to the tile object
  tile.deserializeInput(topic, payload, length);
}
