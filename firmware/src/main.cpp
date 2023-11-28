// Import necessary libraries
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <DFRobotDFPlayerMini.h>

// Import secret.h (contains ssid, password, mqtt server, mqtt port, mqtt user and mqtt password)
#include "secret.h"

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

// Define pixel struct (led strip pixel)
struct Pixel {
  int red;
  int green;
  int blue;
  int white;
};

// Define pin constants
#define MODE_SWITCH_PIN 10 // pin for mode switch
#define PRESENCE_PIN 19    // pin for presence detection
#define LEDSTRIP_PIN 18    // pin for led strip
#define RX_PIN 1           // pin rx, should be connected to tx of dfplayer
#define TX_PIN 0           // pin tx, should be connected to rx of dfplayer

// Define MQTT constants
const char* rootTopic = "PM/MLT";

const int uptimeInterval = 1000; // interval in milliseconds to update uptime

// Define device specific constants
const int amount_of_pixels = 12; // amount of pixels in the led strip
const char* firmware_version = "0.0.7";
const char* hardware_version = "0.0.2";
const String sounds[] = {
  "A cat meowing",
  "A dog barking",
  "A duck quacking",
  "A frog croaking",
  "A horse neighing",
  "A pig grunt",
  "A rooster crowing",
  "A chicken clucking",
  "A sheep baaing",
  "A wolf howling",
  "Minecraft villager",
  "Minecraft creeper hissing",
  "Minecraft explosion",
  "Mario jump",
  "Mario coin",
  "Mario death",
  "Among Us role reveal",
  "Fortnite death",
  "Roblox oof",
  "CS:GO bomb planted",
  "CS:GO bomb defused",
  "GTA San Andreas - Here we go again",
  "GTA V wasted",
  "GTA V phone ring",
  "Bruh sound effect",
  "Emotional damage",
  "Sad violin",
  "Windows XP error",
  "Windows XP shutdown",
  "Windows XP startup",
  "Piano C note",
  "Piano C# note",
  "Piano D note",
  "Piano D# note",
  "Piano E note",
  "Piano F note",
  "Piano F# note",
  "Piano G note",
  "Piano G# note",
  "Piano A note",
  "Piano A# note",
  "Piano B note",
  "Applause",
  "Kids cheering",
  "Crickets",
  "Wheel spin",
  "Wrong answer",
  "Right answer",
  "Intermission",
  "The Office - That's what she said",
  "The Office - No, God! No, God, please no! No! No! Nooooooo!",
  "Obi-Wan Kenobi - Hello there"
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
String stateTopic = "state";
String commandTopic = "command";

int cycle = 0;

bool reboot = false;
bool ping = true;
bool previous_ping = ping;
unsigned long uptime = 0;
unsigned long lastUptime = 0;

bool presence = false;
bool previous_presence = false;

int audio_mode = 4; // 1 = play, 2 = pause, 3 = resume, 4 = stop
int previous_audio_mode = 4;
int audio_state = 0; // 0 = idle, 1 = playing, 2 = paused
bool audio_loop = false;
bool previous_audio_loop = false;
String sound = sounds[0]; // Take first sound in sounds array as default
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
void connectToWifi();
void disconnectFromWifi();
void connectToMqtt();
void disconnectFromMqtt();
bool updateSystem();
bool updateUptime();
String getSystemState();
bool updateAudio();
bool audioPlayerStateChanged();
String getAudioState();
bool updateLights();
String getLightState();
bool updatePresence();
String getPresenceState();

// Setup function
void setup() {
  // Set serial monitor baud rate for debugging purposes
  Serial.begin(115200);

  // Initialize the mode switch pin as an input with internal pullup resistor (pressed = LOW, not pressed = HIGH)
  pinMode(MODE_SWITCH_PIN, INPUT_PULLUP);

  // Set mode from button state
  if (digitalRead(MODE_SWITCH_PIN) == HIGH) {
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
    delay(1000); // Wait some time to prevent spamming the serial monitor with errors
  }
  // Update cycle counter
  cycle++;
}

// Demo setup function (setup for demo mode)
void demo_setup() {
  // Run demo setup
  Serial.println("Running demo setup...");
  // Audio seettings for demo mode (these don't change while running demo mode)
  // Set sound
  sound = "Mario jump";
  // Set volume
  volume = 25; // 15 = 50% volume
  // Set audio loop
  audio_loop = false;
  // Set brightness to 100
  brightness = 100;
}

// Demo loop function (loop for demo mode)
void demo_loop() {
  // If presence has changed
  if (updatePresence()) {
    // If presence is detected
    if (presence) {
      // Fill all pixels with the color green
      for (int i = 0; i < amount_of_pixels; i++) {
        pixels[i].red = 0;
        pixels[i].green = 255;
        pixels[i].blue = 0;
        pixels[i].white = 0;
      }
      // Set audio to play
      audio_mode = 1;
    } else {
      // Fill all pixels with the color green
      for (int i = 0; i < amount_of_pixels; i++) {
        pixels[i].red = 255;
        pixels[i].green = 0;
        pixels[i].blue = 0;
        pixels[i].white = 0;
      }
      // Set audio to stop
      audio_mode = 4;
    }
    // Update lights
    updateLights();
    // Update audio
    updateAudio();
  }
}

// MQTT setup function (setup for MQTT mode)
void mqtt_setup() {
  // Run MQTT setup
  Serial.println("Running MQTT setup...");

  // Set device name to mac address of ESP32
  String mac = WiFi.macAddress();
  mac.replace(":", "");
  device_name = mac;

  // Set state and command topics
  stateTopic = String(rootTopic) + "/" + String(device_name) + "/self/state";
  commandTopic = String(rootTopic) + "/" + String(device_name) + "/self/command";

  // Set wifi hostname to device name
  WiFi.setHostname(device_name.c_str());

  // Connect to Wi-Fi
  connectToWifi();

  // Update MQTT settings
  client.setBufferSize(2048); // Set MQTT packet buffer size
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Connect to MQTT broker
  connectToMqtt();
}

// MQTT loop function (loop for MQTT mode)
void mqtt_loop() {
  // If not connected to MQTT broker, try to connect
  if (!client.connected()) {
    // Disconnect from MQTT broker
    disconnectFromMqtt();
    // Connect to MQTT broker
    connectToMqtt();
  }

  // If not connected to Wi-Fi, try to connect
  if (WiFi.status() != WL_CONNECTED) {
    // Disconnect from Wi-Fi
    disconnectFromWifi();
    // Connect to Wi-Fi
    connectToWifi();
  }

  // Keep the MQTT connection alive look for incoming messages
  client.loop();

  // If reboot is true, reboot
  if (reboot) {
    Serial.println("Rebooting...");
    // Disconnect from MQTT broker
    disconnectFromMqtt();
    // Disconnect from Wi-Fi
    disconnectFromWifi();
    // Reboot
    ESP.restart();
  }

  // Update system
  if (updateSystem()) {
    client.publish((stateTopic + "/system").c_str(), getSystemState().c_str());
  }

  // Update audio
  if (updateAudio() || audioPlayerStateChanged()) {
    client.publish((stateTopic + "/audio").c_str(), getAudioState().c_str());
  }

  // Update lights
  if (updateLights()) {
    client.publish((stateTopic + "/light").c_str(), getLightState().c_str());
  }

  // Update presence
  if (updatePresence()) {
    client.publish((stateTopic + "/presence").c_str(), getPresenceState().c_str());
  }
}

// MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  // Print the topic and payload for debugging purposes
  Serial.println("Message arrived in topic: " + String(topic));
  //Serial.println("Message: " + String((char*)payload));

  // Parse commands from payload for each subtopic
  if (String(topic) == commandTopic + "/system") 
  {
    StaticJsonDocument<32> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    reboot = doc["reboot"];
    ping = doc["ping"];
  } 
  else if (String(topic) == commandTopic + "/audio") 
  {
    StaticJsonDocument<64> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    audio_mode = doc["mode"];
    audio_loop = doc["loop"];
    sound = (const char*)doc["sound"];
    volume = ((int)doc["volume"] / 100.0) * 30;  // Convert volume from 0-100 to 0-30
  } 
  else if (String(topic) == commandTopic + "/light") 
  {
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    brightness = doc["brightness"];

    JsonArray light_pixels = doc["pixels"];
    for (int i = 0; i < amount_of_pixels; i++) {
      JsonObject pixel = light_pixels[i];
      pixels[i].red = pixel["r"];
      pixels[i].green = pixel["g"];
      pixels[i].blue = pixel["b"];
      pixels[i].white = pixel["w"];
    }
  }
  else {
    Serial.println("Unknown topic, doing nothing...");
    Serial.println("commandTopic: " + String(commandTopic));
  }
}

// Connect to wifi function
void connectToWifi() {
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi as " + device_name + "...");
  }
  Serial.println("Connected to WiFi as " + device_name);
}

// Disconnect from wifi function
void disconnectFromWifi() {
  // Disconnect from Wi-Fi
  WiFi.disconnect();
  while (WiFi.status() == WL_CONNECTED) {
    delay(1000);
    Serial.println("Disconnecting from WiFi as " + device_name + "...");
  }
  Serial.println("Disconnected from WiFi as " + device_name);
}

// Connect to MQTT broker function
void connectToMqtt() {
  // Replace mqtt user with device name if mqtt user is NULL
  if (mqtt_user == NULL) {
    mqtt_user = device_name.c_str();
  }
  // Connect to MQTT broker
  while (!client.connected()) {
    if (client.connect(device_name.c_str(), mqtt_user, mqtt_password, (String(rootTopic) + "/" + String(device_name) + "/self").c_str(), 1, true, String("OFFLINE").c_str())) {
      Serial.println("Connected to MQTT broker as " + String(device_name));
      // Publish online message
      client.publish((String(rootTopic) + "/" + String(device_name) + "/self").c_str(), String("ONLINE").c_str(), true);
      // Publish initial state
      client.publish((stateTopic + "/system").c_str(), getSystemState().c_str());
      client.publish((stateTopic + "/audio").c_str(), getAudioState().c_str());
      client.publish((stateTopic + "/light").c_str(), getLightState().c_str());
      client.publish((stateTopic + "/presence").c_str(), getPresenceState().c_str());
      // Subscribe to command subtopic
      client.subscribe((commandTopic + "/#").c_str());
      Serial.println("Connected to MQTT broker as " + String(device_name));
    } else {
      Serial.println("Failed to connect to MQTT broker, retrying in 5 seconds...");
      delay(5000);
    }
  }
}

// Disconnect from MQTT broker function
void disconnectFromMqtt() {
  // Disconnect from MQTT broker
  if (client.connected()) {
    // Publish offline message
    client.publish((String(rootTopic) + "/" + String(device_name) + "/self").c_str(), String("OFFLINE").c_str(), true);
    // Disconnect from MQTT broker
    client.disconnect();
    while (client.connected()) {
      delay(1000);
      Serial.println("Disconnecting from MQTT broker as " + String(device_name) + "...");
    }
    Serial.println("Disconnected from MQTT broker as " + String(device_name));
  }
}

// Update system function
bool updateSystem() {
  if (ping != previous_ping) {
    // Ping has changed
    updateUptime();
    // Update previous ping
    previous_ping = ping;
    // State has changed, return true
    return true;
  } else if (ping) {
    return updateUptime();
  } else {
    updateUptime();
    // State hasn't changed, return false
    return false;
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

// Get system state function (returns system state as JSON)
String getSystemState() {
  StaticJsonDocument<2048> doc;

  doc["firmware"] = firmware_version;
  doc["hardware"] = hardware_version;
  doc["ping"] = ping;
  doc["uptime"] = uptime;

  JsonArray system_sounds = doc.createNestedArray("sounds");
  for (int i = 0; i < amount_of_sounds; i++) {
    system_sounds.add(sounds[i]);
  }

  String output;
  serializeJson(doc, output);
  return output;
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
          if (sound == sounds[i]) {
            dfplayer.play(i + 1);
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
      // Set audio mode to stop, since the player is done playing
      audio_mode = 4;
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

// Get audio state function (returns audio state as JSON)
String getAudioState() {
  StaticJsonDocument<96> doc;

  doc["state"] = audio_state;
  doc["looping"] = audio_loop;
  doc["sound"] = sound;
  doc["volume"] = (volume / 30.0) * 100;  // Convert volume from 0-30 to 0-100

  String output;
  serializeJson(doc, output);
  return output;
}

// Update lights function
bool updateLights() {
  // If brightness has changed or pixel colors have changed (value in pixels is different from previous value in pixels)
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

// Get light state function (returns light state as JSON)
String getLightState() {
  StaticJsonDocument<1024> doc;

  doc["brightness"] = brightness;

  JsonArray light_pixels = doc.createNestedArray("pixels");
  for (int i = 0; i < amount_of_pixels; i++) {
    JsonObject pixel = light_pixels.createNestedObject();
    pixel["r"] = pixels[i].red;
    pixel["g"] = pixels[i].green;
    pixel["b"] = pixels[i].blue;
    pixel["w"] = pixels[i].white;
  }

  String output;
  serializeJson(doc, output);
  return output;
}

// Update presence function
bool updatePresence() {
  // Update presence
  presence = digitalRead(PRESENCE_PIN);
  // Only check presence every 100 clock cycles (to prevent bouncing)
  if (cycle % 100 == 0) {
    // If presence has changed
    if (presence != previous_presence) {
      Serial.println("Updating presence...");
      // Update previous presence
      previous_presence = presence;
      // State has changed, return true
      return true;
    }
  } else {
    // State hasn't changed, return false
    return false;
  }
}

// Get presence state function (returns presence state as JSON)
String getPresenceState() {
  StaticJsonDocument<16> doc;

  doc["detected"] = presence;

  String output;
  serializeJson(doc, output);
  return output;
}
