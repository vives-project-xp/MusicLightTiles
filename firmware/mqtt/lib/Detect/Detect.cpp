#include "Detect.h"

Detect::Detect() {
  // Set default values
  this->detected = false;
}

String Detect::SerializeOutput() {
  Serial.println("Serializing output");
  // TODO: Implement serialization
  return "{\"hello\":\"world\"}";
}

void Detect::UpdateState() {
  Serial.println("Updating state");
  // TODO: Implement state update
}
