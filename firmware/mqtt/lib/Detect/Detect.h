#ifndef Detect_h
#define Detect_h

// Import required libraries
#include <Arduino.h>
#include <arduinoJson.h>

class Detect {
  public:
    Detect();
    String SerializeOutput();
    void UpdateState();
  private:
    bool detected;
};
#endif