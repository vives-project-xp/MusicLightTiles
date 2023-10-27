// Import necessary libraries
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <DFRobotDFPlayerMini.h>

#include "secret.h" // TODO: implement better way of storing and accessing secrets

// Define mode enum (mode switch)
enum Mode {
  DEMO,
  MQTT
};

// Define audio action enum (audio_state + audio_mode)
enum AudioAction {
  IDLE_PLAY = 1,
  IDLE_PAUSE = 2,
  IDLE_RESUME = 3,
  IDLE_STOP = 4,
  PLAY_PLAY = 11,
  PLAY_PAUSE = 12,
  PLAY_RESUME = 13,
  PLAY_STOP = 14,
  PAUSE_PLAY = 21,
  PAUSE_PAUSE = 22,
  PAUSE_RESUME = 23,
  PAUSE_STOP = 24
};

// Define sound struct (sound file)
struct Sound {
  int id;
  String name;
};

// Define pixel struct (led strip pixel)
struct Pixel {
  int red;
  int green;
  int blue;
  int white;
};

// Define pin constants
#define MODE_SWITCH_PIN 4  // pin for mode switch
#define PRESENCE_PIN 5     // pin for presence detection
#define LEDSTRIP_PIN 25    // pin for led strip
#define RX_PIN 16          // pin rx, should be connected to tx of dfplayer
#define TX_PIN 17          // pin tx, should be connected to rx of dfplayer

// Define MQTT constants
const char* rootTopic = "music-light-tiles";
const char* stateTopic = "state";
const char* commandTopic = "command";

const int uptimeInterval = 1000; // interval in milliseconds to update uptime

// Define device specific constants
const int amount_of_pixels = 16; // amount of pixels in the led strip
const char* firmware_version = "0.0.4";
const char* hardware_version = "0.0.1";
const Sound sounds[] = {
  Sound{1, "Sound-1"}, 
  Sound{2, "Sound-2"}, 
  Sound{3, "Sound-3"},
  Sound{4, "Sound-4"},
  Sound{5, "Sound-5"},
  Sound{6, "Sound-6"},
  Sound{7, "Sound-7"}
}; // All sounds that can be played (available on the sd card of the dfplayer)
const int amount_of_sounds = sizeof(sounds) / sizeof(sounds[0]);

// Define global objects
Mode mode = DEMO; // default to demo mode
WiFiClient wifiClient;
PubSubClient client(wifiClient);
Adafruit_NeoPixel ledstrip = Adafruit_NeoPixel(amount_of_pixels, LEDSTRIP_PIN, NEO_WRGB + NEO_KHZ800);
HardwareSerial hs(1);
DFRobotDFPlayerMini dfplayer;

// Define global variables
String device_name = "tile";

bool reboot = false;
bool ping = true; // TODO: should be false by default, but true for debugging purposes
unsigned long uptime = 0;
unsigned long lastUptime = 0;

bool presence = false;
bool previous_presence = false;

int audio_mode = 4; // 1 = play, 2 = pause, 3 = resume, 4 = stop
int previous_audio_mode = 4;
int audio_state = 0; // 0 = idle, 1 = playing, 2 = paused
bool audio_loop = false;
bool previous_audio_loop = false;
String sound = sounds[0].name; // Take first sound in sounds array as default
String previous_sound = sound;
int volume = 0; // 0-30
int previous_volume = 0;

int brightness = 1; // 0-255 (0 = off, 255 = full brightness)
int previous_brightness = 1;
Pixel pixels[amount_of_pixels] = {Pixel{0, 0, 0, 0}};
Pixel previous_pixels[amount_of_pixels] = {Pixel{0, 0, 0, 0}};

// Function prototypes
void demo_setup();
void demo_loop();
void mqtt_setup();
void mqtt_loop();
void callback(char* topic, byte* payload, unsigned int length);
void updateState();
bool updateUptime();
bool updatePresence();
bool updateAudio();
bool audioPlayerStateChanged();
bool updateLights();
String serializeState();

// Setup function
void setup() {
  // Set serial monitor baud rate for debugging purposes
  Serial.begin(115200);

  // Initialize the mode switch pin as an input with internal pullup resistor (pressed = LOW, not pressed = HIGH)
  pinMode(MODE_SWITCH_PIN, INPUT_PULLUP);

  // Set mode from button state
  if (digitalRead(MODE_SWITCH_PIN) == HIGH) { // TODO: no contact defaults to mqtt, but should be demo (but mqtt can't get past connecting to wifi for some reason if demo is default)
    mode = DEMO;
  } else {
    mode = MQTT;
  }

  // General setup
  Serial.println("Running general setup...");
  // Setup presence detection pin as input with internal pulldown resistor (pressed = HIGH, not pressed = LOW)
  pinMode(PRESENCE_PIN, INPUT_PULLDOWN);
  // Setup led strip (set leds to off)
  ledstrip.begin();
  ledstrip.setBrightness(1);
  ledstrip.show();
  // Setup audio
  hs.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  dfplayer.begin(hs); // Use hardware serial to communicate with DFPlayer Mini
  dfplayer.setTimeOut(500); // Set serial communication time out 500ms
  dfplayer.volume(volume); // Set volume off
  dfplayer.EQ(DFPLAYER_EQ_NORMAL);  // Set EQ to normal

  // Initialise program depending on mode
  if (mode == DEMO) {
    // Run demo setup
    demo_setup();
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
    delay(1000); // Wait some time to prevent spamming the serial monitor
  }
}

void demo_setup() {
  // Run demo setup
  Serial.println("Running demo setup...");

  // Audio seettings for demo mode (these don't change while running demo mode)
  // Set sound
  sound = "Sound-1";
  // Set volume
  volume = 15; // 15 = 50% volume
  // Set audio loop
  audio_loop = true;
}

// Demo loop function (loop for demo mode)
void demo_loop() {
  // Update presence
  bool presenceChanged = updatePresence();

  // If presence has changed
  if (presenceChanged) {
    // If presence is true
    if (presence) {
      // Set brightness to 50
      brightness = 50;
      // Fill sections with the color green
      for (int i = 0; i < amount_of_pixels; i++) {
        pixels[i].red = 0;
        pixels[i].green = 255;
        pixels[i].blue = 0;
        pixels[i].white = 0;
      }
      // Set audio to play
      audio_mode = 1;
    } else {
      // Set brightness to 1 (off)
      brightness = 0;
      // Fill sections with the color red
      //for (int i = 0; i < amount_of_pixels; i++) {
      //  pixels[i].red = 255;
      //  pixels[i].green = 0;
      //  pixels[i].blue = 0;
      //  pixels[i].white = 0;
      //}
      // Set audio to stop
      audio_mode = 4;
    }
    // Update lights
    updateLights();

    // Update audio
    updateAudio();
  }

  // Wait a little bit (just for testing purposes, remove this later)
  delay(10);
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
      client.publish((String(rootTopic) + "/" + String(device_name)).c_str(), String("ONLINE").c_str(), true);
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
  // If not connected to MQTT broker or Wi-Fi, reconnect
  if (!client.connected() || !WiFi.isConnected()) {
    // Try to disconnect from MQTT broker
    if (client.connected()) {
      client.publish((String(rootTopic) + "/" + String(device_name)).c_str(), String("OFFLINE").c_str());
      client.disconnect();
    }
    // Try to disconnect from Wi-Fi
    if (WiFi.isConnected()) {
      WiFi.disconnect();
    }
    // Rerun MQTT setup (reconnect to MQTT broker and Wi-Fi)
    mqtt_setup();
  }

  // Keep the MQTT connection alive look for incoming messages
  client.loop();

  // If reboot is true, reboot
  if (reboot) {
    Serial.println("Rebooting...");
    client.publish((String(rootTopic) + "/" + String(device_name)).c_str(), String("OFFLINE").c_str(), true);
    ESP.restart();
  }

  // Update uptime
  bool uptimeChanged = false;
  if (ping) {
    uptimeChanged = updateUptime();
  } else {
    updateUptime();
  }

  // Update presence
  bool presenceChanged = updatePresence();

  // Update audio
  bool audioChanged = updateAudio();

  // Read player state
  bool playerStateChanged = audioPlayerStateChanged();

  // Update lights
  bool lightsChanged = updateLights();

  // If state has changed, publish new state
  if (uptimeChanged || audioChanged || lightsChanged || presenceChanged || playerStateChanged) {
    client.publish((String(rootTopic) + "/" + String(device_name) + "/" + String(stateTopic)).c_str(), serializeState().c_str());
  }

  // Wait a little bit (just for testing purposes, remove this later)
  delay(100);
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

  // TODO: validate payload values (check if values are possible)
  // Deserialize JSON
  StaticJsonDocument<1536> doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  JsonObject system = doc["system"];
  reboot = system["reboot"];
  ping = system["ping"];

  JsonObject audio = doc["audio"];
  audio_mode = audio["mode"];
  audio_loop = audio["loop"];
  sound = (const char*)audio["sound"];
  volume = ((int)audio["volume"] / 100.0) * 30;  // Convert volume from 0-100 to 0-30

  brightness = doc["light"]["brightness"];

  JsonArray light_sections = doc["light"]["sections"];
  for (int i = 0; i < amount_of_pixels; i++) {
    JsonObject section = light_sections[i];
    pixels[i].red = section["r"];
    pixels[i].green = section["g"];
    pixels[i].blue = section["b"];
    pixels[i].white = section["w"];
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
    Serial.println("Updating uptime...");
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
  presence = digitalRead(PRESENCE_PIN);
  // If presence has changed
  if (presence != previous_presence) {
    Serial.println("Updating presence...");
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
  if (audio_mode != previous_audio_mode || sound != previous_sound || volume != previous_volume || audio_loop != previous_audio_loop) {

    Serial.println("Updating audio...");

    // Print current state for debugging purposes
    if (dfplayer.available()) {
      Serial.println("Player is available");
      Serial.println("Current state: " + String(audio_state));
    } else {
      Serial.println("Player is not available");
      Serial.println("Current state: " + String(audio_state));
    }

    // Create audio action from audio state and audio mode
    AudioAction audioAction = AudioAction((String(audio_state) + String(audio_mode)).toInt());
    Serial.println("Audio action: " + String(audioAction));

    // Check current audio state
    switch (audioAction){
      case IDLE_PLAY: case PLAY_PLAY: case PAUSE_PLAY:
        /* Play sound + Set volume + Set loop */
        Serial.println("Playing sound...");
        // Set volume
        dfplayer.volume(volume);
        // Set loop
        if (audio_loop) {
          dfplayer.enableLoop();
        } else {
          dfplayer.disableLoop();
        }
        // Play sound
        for (int i = 0; i < amount_of_sounds; i++) {
          if (sound == sounds[i].name) {
            dfplayer.play(sounds[i].id);
            break;
          }
        }
        // Set audio state to playing
        audio_state = 1;
        break;
      
      case IDLE_PAUSE: case IDLE_RESUME: case IDLE_STOP: case PAUSE_PAUSE:
        /* Set volume + Set loop */
        Serial.println("Setting volume and loop...");
        // Set volume
        dfplayer.volume(volume);
        // Set loop
        if (audio_loop) {
          dfplayer.enableLoop();
        } else {
          dfplayer.disableLoop();
        }
        break;

      case PLAY_RESUME:
        /* Pause sound + Set volume + Set loop + Resume sound */
        Serial.println("Setting volume and loop...");
        // Pause sound
        dfplayer.pause();
        // Set volume
        dfplayer.volume(volume);
        // Set loop
        if (audio_loop) {
          dfplayer.enableLoop();
        } else {
          dfplayer.disableLoop();
        }
        // Resume sound
        dfplayer.start();
        break;

      case PLAY_PAUSE:
        /* Pause sound + Set volume + Set loop */
        Serial.println("Pausing sound...");
        // Pause sound
        dfplayer.pause();
        // Set volume
        dfplayer.volume(volume);
        // Set loop
        if (audio_loop) {
          dfplayer.enableLoop();
        } else {
          dfplayer.disableLoop();
        }
        // Set audio state to paused
        audio_state = 2;
        break;

      case PLAY_STOP: case PAUSE_STOP:
        /* Stop sound + Set volume + Set loop */
        Serial.println("Stopping sound...");
        // Stop sound
        dfplayer.stop();
        // Set volume
        dfplayer.volume(volume);
        // Set loop
        if (audio_loop) {
          dfplayer.enableLoop();
        } else {
          dfplayer.disableLoop();
        }
        // Set audio state to idle
        audio_state = 0;
        break;

      case PAUSE_RESUME:
        /* Resume sound + Set volume + Set loop */
        Serial.println("Resuming sound...");
        // Set volume
        dfplayer.volume(volume);
        // Set loop
        if (audio_loop) {
          dfplayer.enableLoop();
        } else {
          dfplayer.disableLoop();
        }
        // Resume sound
        dfplayer.start();
        // Set audio state to playing
        audio_state = 1;
        break;
      
      default:
        // Unknown action, do nothing
        Serial.println("Unknown audio action, doing nothing...");
        break;
    }

    // Update previous values
    previous_audio_mode = audio_mode;
    previous_sound = sound;
    previous_volume = volume;
    previous_audio_loop = audio_loop;

    // State has changed, return true
    return true;
  } else {
    // Nothing has changed, return false
    return false;
  }
}

// Read player state function
bool audioPlayerStateChanged(){
  // Check if player is available
  if (dfplayer.available()) {
    // Check if player is done playing and audio is not looping
    if (dfplayer.readType() == DFPlayerPlayFinished && audio_loop == false) {
      Serial.println("Player is done playing");
      // Set audio state to idle
      audio_state = 0;
      // State has changed, return true
      return true;
    } else {
      // No significant change, return false
      return false;
    }
  } else {
    // No significant change, return false
    return false;
  }
}

// Update lights function
bool updateLights() {
  // If brightness has changed or sections have changed (value in sections is different from previous value in sections)
  if (brightness != previous_brightness || memcmp(pixels, previous_pixels, sizeof(pixels)) != 0) {

    Serial.println("Updating lights...");
    // Set brightness to new value
    ledstrip.setBrightness(brightness);
    // Set pixels to new values
    for (int i = 0; i < amount_of_pixels; i++) {
      ledstrip.setPixelColor(i, ledstrip.Color(pixels[i].red, pixels[i].green, pixels[i].blue, pixels[i].white));
    }
    // Show changes
    ledstrip.show();

    // Update previous values
    previous_brightness = brightness;
    memcpy(previous_pixels, pixels, sizeof(pixels));
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
  system["ping"] = ping;
  system["uptime"] = uptime;

  JsonArray system_sounds = system.createNestedArray("sounds");
  for (int i = 0; i < amount_of_sounds; i++) {
    system_sounds.add(sounds[i].name);
  }

  JsonObject audio = doc.createNestedObject("audio");
  audio["mode"] = audio_state;
  audio["looping"] = audio_loop;
  audio["sound"] = sound;
  audio["volume"] = (volume / 30.0) * 100;  // Convert volume from 0-30 to 0-100

  JsonObject light = doc.createNestedObject("light");
  light["brightness"] = brightness;

  JsonArray light_sections = light.createNestedArray("sections");
  for (int i = 0; i < amount_of_pixels; i++) {
    JsonObject section = light_sections.createNestedObject();
    section["r"] = pixels[i].red;
    section["g"] = pixels[i].green;
    section["b"] = pixels[i].blue;
    section["w"] = pixels[i].white;
  }

  doc["detect"]["detected"] = presence;

  String output;
  serializeJson(doc, output);
  return output;
}
