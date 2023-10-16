#ifndef Light_h
#define Light_h
// code goes here

// Import required libraries
#include <Arduino.h>
#include <arduinoJson.h>

// Define constants
#define MAX_SECTIONS 10

struct Section {
  int red;
  int green;
  int blue;
  int white;
};

class Light {
  public:
    // Methods
    Light();
  
  private:
    // Atributes
    int brightness;
    Section sections[MAX_SECTIONS];
};
#endif