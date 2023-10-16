#include "Audio.h"

Audio::Audio() {
  // Set default values
  this->playing = false;
  this->sound = "";
  this->volume = 0;
}

void Audio::DeserializeInput(char* payload, unsigned int length) {
  Serial.println("Deserializing input");
  // TODO: Implement deserialization
  this->UpdateState();
}

String Audio::SerializeOutput() {
  Serial.println("Serializing output");
  // TODO: Implement serialization
  return "{\"hello\":\"world\"}";
}

void Audio::UpdateState() {
  Serial.println("Updating state");
  // TODO: Implement state update
}
