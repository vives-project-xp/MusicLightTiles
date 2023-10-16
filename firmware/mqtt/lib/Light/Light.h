#ifndef Light_h
#define Light_h
// code goes here

// Import required libraries
#include <Arduino.h>
#include <arduinoJson.h>

// Define constants
#define MAX_SECTIONS 10

struct Section {
  int r;
  int g;
  int b;
  int w;
};

class Light {
  public:
    Light();
    void DeserializeInput(char* payload, unsigned int length);
    String SerializeOutput();
    void UpdateState();
  private:
    int brightness;
    Section sections[MAX_SECTIONS];
};
#endif