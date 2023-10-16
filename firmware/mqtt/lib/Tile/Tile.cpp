#include "Tile.h"

Tile::Tile() {
  // set default values
  this->reboot = false;
  this->firmware = "1.0.0";
  this->hardware = "1.0.0";
  this->mode = "demo";
  this->uptime = 0;
  this->lastUptime = 0;
  this->sounds = new String[3] {""};
}

void Tile::deserializeInput(char* topic, byte* payload, unsigned int length) {
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