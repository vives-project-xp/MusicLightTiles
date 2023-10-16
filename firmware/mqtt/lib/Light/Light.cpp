#include "Light.h"

Light::Light() {
  // Set default values
  this->brightness = 0;
  for (int i = 0; i < MAX_SECTIONS; i++) {
    this->sections[i].r = 0;
    this->sections[i].g = 0;
    this->sections[i].b = 0;
    this->sections[i].w = 0;
  }
}

void Light::DeserializeInput(char* payload, unsigned int length) {
  Serial.println("Deserializing input");
  // TODO: Implement deserialization
  this->UpdateState();
}

String Light::SerializeOutput() {
  Serial.println("Serializing output");
  // TODO: Implement serialization
  return "{\"hello\":\"world\"}";
}

void Light::UpdateState() {
  Serial.println("Updating state");
  // TODO: Implement state update
}