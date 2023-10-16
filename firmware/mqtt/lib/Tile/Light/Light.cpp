#include "Light.h"

Light::Light() {
  // Set default values
  this->brightness = 0;
  for (int i = 0; i < MAX_SECTIONS; i++) {
    this->sections[i].red = 0;
    this->sections[i].green = 0;
    this->sections[i].blue = 0;
    this->sections[i].white = 0;
  }
}