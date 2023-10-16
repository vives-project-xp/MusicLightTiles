#include "Tile.h"

Tile::Tile(String firmware_version, String hardware_version) {
  // set default values
  this->_reboot = false;
  this->_firmware = firmware_version;
  this->_hardware = hardware_version;
  this->_mode = "mqtt";
  this->_uptime = 0;
  this->_lastUptime = 0;
  this->_sounds = new String[3] {""}; //TODO: get available sounds from audio class
  this->state = this->serializeOutput();
  this->_previous_state = this->state;
}

void Tile::deserializeInput(byte* payload, unsigned int length) {
  // TODO: Connect json input to attributes
  Serial.println("Deserializing input");

  StaticJsonDocument<2048> doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.c_str());
    return;
  }

  JsonObject system = doc["system"];
  _mode = (const char*)system["mode"]; // "mqtt"
  this->_reboot = system["reboot"]; // false
  
  JsonObject audio = doc["audio"];
  bool audio_play = audio["play"]; // true
  const char* audio_sound = audio["sound"]; // "sound-1"
  int audio_volume = audio["volume"]; // 50

  JsonObject light = doc["light"];
  int light_brightness = light["brightness"]; // 50

  Section* light_sections = new Section[AMOUNT_OF_SECTIONS];
  // for every section in json light.sections array assign values to light_sections array
  for (int i = 0; i < AMOUNT_OF_SECTIONS; i++) {
    JsonObject light_section = light["sections"][i];
    light_sections[i].red = light_section["r"];
    light_sections[i].green = light_section["g"];
    light_sections[i].blue = light_section["b"];
    light_sections[i].white = light_section["w"];
  }

  this->updateState();
}

String Tile::serializeOutput() {
  // TODO: Connect data from attributes to json output
  Section* light_sections = new Section[AMOUNT_OF_SECTIONS];
  for (int i = 0; i < AMOUNT_OF_SECTIONS; i++) {
    light_sections[i].red = 0;
    light_sections[i].green = 0;
    light_sections[i].blue = 0;
    light_sections[i].white = 0;
  }

  StaticJsonDocument<2048> doc;

  JsonObject system = doc.createNestedObject("system");
  system["firmware"] = _firmware;
  system["hardware"] = _hardware;
  system["mode"] = _mode;
  system["uptime"] = _uptime;

  JsonArray system_sounds = system.createNestedArray("sounds");
  for (int i = 0; i < AMOUNT_OF_SOUNDS; i++) {
    system_sounds.add(_sounds[i]);
  }

  JsonObject audio = doc.createNestedObject("audio");
  audio["playing"] = true;
  audio["sound"] = "sound-1";
  audio["volume"] = 50;

  JsonObject light = doc.createNestedObject("light");
  light["brightness"] = 50;

  JsonArray light_sections_array = light.createNestedArray("sections");
  for (int i = 0; i < AMOUNT_OF_SECTIONS; i++) {
    JsonObject light_section = light_sections_array.createNestedObject();
    light_section["r"] = light_sections[i].red;
    light_section["g"] = light_sections[i].green;
    light_section["b"] = light_sections[i].blue;
    light_section["w"] = light_sections[i].white;
  }

  doc["detect"]["detected"] = true;

  String output;
  serializeJson(doc, output);

  return output;
}

void Tile::updateState() {
  // Process reboot command
  if (this->_reboot) {
    Serial.println("Rebooting");
    ESP.restart();
  }
  // Update current state
  this->state = this->serializeOutput();
}

void Tile::updateUptime() {
  // Update uptime (add 1 for every second)
  unsigned long currentMillis = millis();
  if (currentMillis - this->_lastUptime >= UPTIME_INTERVAL) {
    this->_uptime++;
    this->_lastUptime = currentMillis;

    // Update current state
    this->state = this->serializeOutput();
  }
}

bool Tile::stateChanged() {
  // Check if state equals previous state
  if (this->state == this->_previous_state) {
    return false;
  } else {
    this->_previous_state = this->state;
    return true;
  }
}