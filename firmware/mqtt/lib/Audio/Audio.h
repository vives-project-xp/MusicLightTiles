#ifndef Audio_h
#define Audio_h

// Import required libraries
#include <Arduino.h>
#include <arduinoJson.h>

class Audio {
  public:
    Audio();
    void DeserializeInput(char* payload, unsigned int length);
    String SerializeOutput();
    void UpdateState();
  private:
    bool playing;
    String sound;
    int volume;
};
#endif