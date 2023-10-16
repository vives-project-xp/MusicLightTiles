#ifndef Tile_h
#define Tile_h

// Include necessary libraries
#include <Arduino.h>
#include <ArduinoJson.h>

class Tile {
  public:
    Tile();
    void DeserializeInput(char* payload, unsigned int length);
    String SerializeOutput();
    void UpdateState();
    void UpdateUptime();
  private:
    bool reboot;
    String firmware;
    String hardware;
    String mode;
    unsigned long uptime;
    unsigned long lastUptime;
    String* sounds;
};

#endif