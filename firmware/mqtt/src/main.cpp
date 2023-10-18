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
const char* device_name = "tile-1"; // TODO: implement random number generator and check if name is already in use
const int amount_of_sections = 16;
const int amount_of_sounds = 3;
const char* firmware_version = "0.0.2";
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
bool reboot = false;
unsigned long uptime = 0;
unsigned long lastUptime = 0;
String state = "";
String previousState = "";
String sounds[amount_of_sounds] = {String("")};

bool presence = false;

bool play = false;
String sound = "";
int volume = 0;

int brightness = 0;
Section sections[amount_of_sections] = {Section{0, 0, 0, 0}};

// Function prototypes
void demo_loop();
void mqtt_setup();
void mqtt_loop();
void callback(char* topic, byte* payload, unsigned int length);
void updateState();
void updateUptime();
void setLights();
void setAudio();
bool getPresence();
bool stateChanged();
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
  // If presence is detected
  if (getPresence()) {
    // Fill sections with the color red
    for (int i = 0; i < amount_of_sections; i++) {
      sections[i].red = 255;
      sections[i].green = 0;
      sections[i].blue = 0;
      sections[i].white = 0;
    }

    // Set lights
    setLights();

    // Set audio
    setAudio();
  } else {
    // Fill sections with the color black
    for (int i = 0; i < amount_of_sections; i++) {
      sections[i].red = 0;
      sections[i].green = 0;
      sections[i].blue = 0;
      sections[i].white = 0;
    }

    // Set lights
    setLights();

    // Set audio
    setAudio();
  }

  // Wait a little bit (just for testing purposes, remove this later)
  delay(1000);
}

// MQTT setup function (setup for MQTT mode)
void mqtt_setup() {
  // Run MQTT setup
  Serial.println("Running MQTT setup...");

  // Set initial state and previous state
  state = serializeState();
  previousState = state;

  // Set device name as hostname
  WiFi.setHostname(device_name);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Update MQTT settings
  client.setBufferSize(1024); // Set MQTT packet buffer size
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Connect to MQTT broker
  while (!client.connected()) {
    if (client.connect(device_name)) { // TODO: implement user/pass and last will (https://pubsubclient.knolleary.net/api#connect)
      Serial.println("Connected to MQTT broker as " + String(device_name));
      client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic)).c_str(), state.c_str());
      client.subscribe((String(rootTopic) + "/" + String(device_name) + "/" + String(commandTopic)).c_str());
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

  // Update uptime
  updateUptime();

  // If state has changed, publish new state
  if (stateChanged()) {
    client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic)).c_str(), state.c_str());
    previousState = state;
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

  updateState();
}

// Update state function (sets lights and audio to current state and calls serializeState function)
void updateState() {
  // Update state
  Serial.println("Updating state...");

  // Reboot if needed
  if (reboot) {
    ESP.restart();
  }

  // Set lights
  setLights();

  // Set audio
  setAudio();

  // Update current state
  state = serializeState();
}

// Update uptime function (updates uptime and calls serializeState function)
void updateUptime() {
  // Update uptime (add 1 for every interval)
  unsigned long currentMillis = millis();
  if (currentMillis - lastUptime >= uptimeInterval) {
    uptime++;
    lastUptime = currentMillis;

    // Update current state
    state = serializeState();
  }
}

// Set lights state function
void setLights() {
  // TODO: Implement setSectionState function
  Serial.println("Setting LED Section state...");
}

// Set audio state function
void setAudio() {
  // TODO: Implement setAudio function
  Serial.println("Setting audio state...");
}

// Get detect state function (is someone standing on the tile?)
bool getPresence() {
  // TODO: Implement getDetect function
  Serial.println("Getting detect state...");
  return false;
}

// StateChanged function (checks if state has changed from last time and returns true if it has)
bool stateChanged() {
  if (state != previousState) {
    return true;
  } else {
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
