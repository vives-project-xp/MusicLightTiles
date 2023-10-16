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
}

void Tile::deserializeInput(byte* payload, unsigned int length) {
  Serial.println("Deserializing input");
  // TODO: Implement deserialization
  this->updateState();
}

String Tile::serializeOutput() {
  Serial.println("Serializing output");
  // TODO: Implement serialization
  return "{\"hello\":\"world\"}";
}

void Tile::updateState() {
  Serial.println("Updating state");
  // TODO: Implement state update
}

bool Tile::stateChanged() {
  Serial.println("Checking if state changed");
  // TODO: Implement state change check
  return false;
}