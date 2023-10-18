// Import necessary libraries
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "secret.h" // TODO: implement better way of storing and accessing secrets

// Define pin constants
const int modeSwitchPin = 4;  // pin for mode switch

// Define MQTT constants
const char* rootTopic = "music-light-tiles";
const char* stateTopic = "state";
const char* commandTopic = "command";

const int uptimeInterval = 1000; // interval in milliseconds to update uptime

// Define device specific constants
const int amount_of_sections = 16;
const int amount_of_sounds = 3;
const char* firmware_version = "0.0.3";
const char* hardware_version = "0.0.1";

// Define mode enum (mode switch)
enum Mode {
  DEMO,
  MQTT
};

// Define section struct (led section)
struct Section {
  int red;
  int green;
  int blue;
  int white;
};

// Define global objects
Mode mode = DEMO; // default mode to demo mode
WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Define global variables
String device_name = "tile";

bool reboot = false;
unsigned long uptime = 0;
unsigned long lastUptime = 0;
String sounds[amount_of_sounds] = {String("")};

bool presence = false;
bool previous_presence = false;

bool play = false;
bool previous_play = false;
String sound = "";
String previous_sound = "";
int volume = 0;
int previous_volume = 0;

int brightness = 0;
int previous_brightness = 0;
Section sections[amount_of_sections] = {Section{0, 0, 0, 0}};
Section previous_sections[amount_of_sections] = {Section{0, 0, 0, 0}};

// Function prototypes
void demo_loop();
void mqtt_setup();
void mqtt_loop();
void callback(char* topic, byte* payload, unsigned int length);
void updateState();
bool updateUptime();
bool updatePresence();
bool updateAudio();
bool updateLights();
String serializeState();

// Setup function
void setup() {
  // Wait for serial monitor to connect
  delay(1000); // TODO: remove this later

  // Set serial monitor baud rate for debugging purposes
  Serial.begin(9600);

  // Initialize the pushbutton pin as an input
  pinMode(modeSwitchPin, INPUT);

  // Set mode from button state
  if (digitalRead(modeSwitchPin) == HIGH) { // TODO: no contact defaults to mqtt, but should be demo (but mqtt can't get past connecting to wifi for some reason if demo is default)
    mode = DEMO;
  } else {
    mode = MQTT;
  }

  // General setup
  Serial.println("Running general setup...");

  // TODO: Implement general setup

  // Initialise program depending on mode
  if (mode == DEMO) {
    // Demo mode doesn't need setup, so do nothing
    Serial.println("Running demo setup...");
  } else if (mode == MQTT) {
    // Run mqtt setup
    mqtt_setup();
  } else {
    // Something went wrong, print error and do nothing
    Serial.println("Unknown mode, doing nothing...");
  }
}

// Loop function
void loop() {
  // Run loop depending on mode
  if (mode == DEMO) {
    // Run demo loop
    demo_loop();
  } else if (mode == MQTT) {
    // Run mqtt loop
    mqtt_loop();
  } else {
    // Something went wrong, print error and do nothing
    Serial.println("Unknown mode, doing nothing...");
  }
}

// Demo loop function (loop for demo mode)
void demo_loop() {
  // Update presence
  bool presenceChanged = updatePresence();

  // If presence has changed
  if (presenceChanged) {
    // If presence is true
    if (presence) {
      // Fill sections with the color green
      for (int i = 0; i < amount_of_sections; i++) {
        sections[i].red = 0;
        sections[i].green = 255;
        sections[i].blue = 0;
        sections[i].white = 0;
      }

      // Update lights
      updateLights();

      // Set audio
      updateAudio();

    } else {
      // Fill sections with the color red
      for (int i = 0; i < amount_of_sections; i++) {
        sections[i].red = 255;
        sections[i].green = 0;
        sections[i].blue = 0;
        sections[i].white = 0;
      }

      // Update lights
      updateLights();

      // Set audio
      updateAudio();
    }
  }

  // Wait a little bit (just for testing purposes, remove this later)
  delay(1000);
}

// MQTT setup function (setup for MQTT mode)
void mqtt_setup() {
  // Run MQTT setup
  Serial.println("Running MQTT setup...");

  // Set device name to mac address of ESP32
  String mac = WiFi.macAddress();
  mac.replace(":", "");
  device_name = mac;

  // Connect to Wi-Fi as default device name
  WiFi.setHostname(device_name.c_str());

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi as " + device_name + "...");
  }
  Serial.println("Connected to WiFi as " + device_name);

  // Update MQTT settings
  client.setBufferSize(1024); // Set MQTT packet buffer size
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Connect to MQTT broker
  while (!client.connected()) {
    if (client.connect(device_name.c_str(), mqtt_user, mqtt_password, (String(rootTopic) + "/" + String(device_name)).c_str(), 1, true, String("OFFLINE").c_str())) {
      Serial.println("Connected to MQTT broker as " + String(device_name));
      client.publish((String(rootTopic) + "/" + String(device_name)).c_str(), String("ONLINE").c_str());
      client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic)).c_str(), serializeState().c_str());
      client.subscribe((String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic)).c_str());
      Serial.println("Connected to MQTT broker as " + String(device_name));
    } else {
      Serial.println("Failed to connect to MQTT broker, retrying in 5 seconds...");
      delay(5000);
    }
  }
}

// MQTT loop function (loop for MQTT mode)
void mqtt_loop() {
  // Keep the MQTT connection alive look for incoming messages
  client.loop();

  // If reboot is true, reboot
  if (reboot) {
    ESP.restart();
  }

  // Update uptime
  bool uptimeChanged = updateUptime();

  // Update audio
  bool audioChanged = updateAudio();

  // Update lights
  bool lightsChanged = updateLights();

  // Update presence
  bool presenceChanged = updatePresence();

  // If state has changed, publish new state
  if (uptimeChanged  || audioChanged || lightsChanged || presenceChanged) {
    client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic)).c_str(), serializeState().c_str());
  }

  // Wait a little bit (just for testing purposes, remove this later)
  delay(10);
}

// MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  // Print the topic and payload for debugging purposes
  Serial.println("Message arrived in topic: " + String(topic));
  Serial.println("Message: " + String((char*)payload));

  // Validate topic
  if (String(topic) != String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic)) {
    Serial.println("Invalid topic, ignoring message...");
    return;
  }

  // Deserialize JSON
  StaticJsonDocument<1536> doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  reboot = doc["system"]["reboot"];

  JsonObject audio = doc["audio"];
  play = audio["play"];
  sound = (const char*)audio["sound"];
  volume = audio["volume"];

  brightness = doc["light"]["brightness"];

  JsonArray light_sections = doc["light"]["sections"];
  for (int i = 0; i < amount_of_sections; i++) {
    JsonObject section = light_sections[i];
    sections[i].red = section["r"];
    sections[i].green = section["g"];
    sections[i].blue = section["b"];
    sections[i].white = section["w"];
  }
}

// Update uptime function
bool updateUptime() {
  // Get current millis
  unsigned long currentMillis = millis();
  // If current millis - last uptime is greater than uptime interval
  if (currentMillis - lastUptime >= uptimeInterval) {
    // Update uptime
    uptime++;
    // Update last uptime
    lastUptime = currentMillis;
    // State has changed, return true
    return true;
  } else {
    // State hasn't changed, return false
    return false;
  }
}

// Update presence function
bool updatePresence() {
  // Update presence
  presence = false; // TODO: implement presence detection
  // If presence has changed
  if (presence != previous_presence) {
    // Update previous presence
    previous_presence = presence;
    // State has changed, return true
    return true;
  } else {
    // State hasn't changed, return false
    return false;
  }
}

// Update audio function
bool updateAudio() {
  if (play != previous_play || sound != previous_sound || volume != previous_volume) {

    // Set audio to new values
    Serial.println("Updating audio...");

    // Update previous values
    previous_play = play;
    previous_sound = sound;
    previous_volume = volume;
    // State has changed, return true
    return true;
  } else {
    // Nothing has changed, return false
    return false;
  }
}

// Update lights function
bool updateLights() {
  // If brightness has changed or sections have changed (value in sections is different from previous value in sections)
  if (brightness != previous_brightness || memcmp(sections, previous_sections, sizeof(sections)) != 0) {

    // Set lights to new values
    Serial.println("Updating lights...");

    // Update previous values
    previous_brightness = brightness;
    memcpy(previous_sections, sections, sizeof(sections));
    // State has changed, return true
    return true;
  } else {
    // Nothing has changed, return false
    return false;
  }
}

// Serialize state function (serializes current state to JSON)
String serializeState() {
  StaticJsonDocument<2048> doc;

  JsonObject system = doc.createNestedObject("system");
  system["firmware"] = firmware_version;
  system["hardware"] = hardware_version;
  system["uptime"] = uptime;

  JsonArray system_sounds = system.createNestedArray("sounds");
  for (int i = 0; i < amount_of_sounds; i++) {
    system_sounds.add(sounds[i]);
  }

  JsonObject audio = doc.createNestedObject("audio");
  audio["playing"] = play;
  audio["sound"] = sound;
  audio["volume"] = volume;

  JsonObject light = doc.createNestedObject("light");
  light["brightness"] = brightness;

  JsonArray light_sections = light.createNestedArray("sections");
  for (int i = 0; i < amount_of_sections; i++) {
    JsonObject section = light_sections.createNestedObject();
    section["r"] = sections[i].red;
    section["g"] = sections[i].green;
    section["b"] = sections[i].blue;
    section["w"] = sections[i].white;
  }

  doc["detect"]["detected"] = presence;

  String output;
  serializeJson(doc, output);
  return output;
}
