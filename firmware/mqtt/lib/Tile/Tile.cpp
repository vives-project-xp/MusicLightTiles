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

void Tile::DeserializeInput(char* payload, unsigned int length) {
  Serial.println("Deserializing input");
  // TODO: Implement deserialization
  this->UpdateState();
}

String Tile::SerializeOutput() {
  Serial.println("Serializing output");
  // TODO: Implement serialization
  return "{\"hello\":\"world\"}";
}

void Tile::UpdateState() {
  Serial.println("Updating state");
  // TODO: Implement state update
}

void Tile::UpdateUptime() {
  Serial.println("Updating uptime");

  // Get current time
  unsigned long currentUptime = millis();

  // Check if 1 second has passed
  if (currentUptime - this->lastUptime >= 1000) {
    // Update uptime
    this->uptime += 1;
    this->lastUptime = currentUptime;
  }
}