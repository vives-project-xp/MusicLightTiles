#ifndef Audio_h
#define Audio_h

// Import required libraries
#include <Arduino.h>
#include <arduinoJson.h>

class Audio {
  public:
    // Methods
    Audio();
  
  private:
    // Atributes
    bool playing;
    String sound;
    int volume;
};
#endif