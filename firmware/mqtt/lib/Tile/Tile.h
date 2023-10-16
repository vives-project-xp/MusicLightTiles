#ifndef Tile_h
#define Tile_h

// Include necessary libraries
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Audio/Audio.h>
#include <Detect/Detect.h>
#include <Light/Light.h>

// Define class
class Tile {
  public:
    // Methods
    Tile();
    void updateState();
    void deserializeInput(char* topic, byte* payload, unsigned int length);
    String serializeOutput();
    bool stateChanged();
    
  private:
    // Atributes
    Audio audio;
    Detect detect;
    Light light;

    bool reboot;
    String firmware;
    String hardware;
    String mode;
    unsigned long uptime;
    unsigned long lastUptime;
    String* sounds;

    // Methods
};

#endif