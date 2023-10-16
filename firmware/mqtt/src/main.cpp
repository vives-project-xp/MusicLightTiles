#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Audio.h>
#include <Detect.h>
#include <Light.h>
#include <Tile.h>
#include "secret.h"

const char* device_name = "tile-1";
const char* rootTopic = "music-light-tiles";
const char* stateTopic = "state";
const char* commandTopic = "command";

unsigned long lastMillis = 0;
unsigned long timeAlive = 0;
const unsigned long interval = 1000; // Uptime interval in milliseconds

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Create objects of the classes
Audio audio;
Detect detect;
Light light;
Tile tile;

// Forward declaration of callback function
void callback(char* topic, byte* payload, unsigned int length);

// Setup function
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

  // Construct the objects
  audio = Audio();
  detect = Detect();
  light = Light();
  tile = Tile();
}

// Loop function
void loop() {
  // Keep the MQTT connection alive and process incoming messages
  client.loop();

  // Update uptime
  tile.UpdateUptime();

  // Update class states
  audio.UpdateState();
  detect.UpdateState();
  light.UpdateState();
  tile.UpdateState();

  // Publish state to MQTT broker (rootTopic/device_name/state/system)
  client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic) + "/system").c_str(), tile.SerializeOutput().c_str());
  client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic) + "/audio").c_str(), audio.SerializeOutput().c_str());
  client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic) + "/light").c_str(), light.SerializeOutput().c_str());
  client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic) + "/detect").c_str(), detect.SerializeOutput().c_str());

  // wait for 10ms (to prevent flooding the broker)
  delay(10);
}

// Callback function
void callback(char* topic, byte* payload, unsigned int length) {
  // Print the topic and payload for debugging purposes
  Serial.println("Message arrived in topic: " + String(topic));
  Serial.println("Message: " + String((char*)payload));
  
  // Direct message to correct handler
  if (String(topic) == (String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/system")) {
    tile.DeserializeInput((char*)payload, length);
    Serial.println("System control command received");
  } else if (String(topic) == (String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/audio")) {
    audio.DeserializeInput((char*)payload, length);
    Serial.println("Audio control command received");
  } else if (String(topic) == (String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic) + "/light")) {
    light.DeserializeInput((char*)payload, length);
    Serial.println("light control command received");
  } else {
    // Skip commands in unknown topics
    Serial.println("Command received in unknown topic, skipping...");
  }
}
