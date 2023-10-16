#ifndef Tile_h
#define Tile_h

// Include necessary libraries
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Audio/Audio.h>
#include <Detect/Detect.h>
#include <Light/Light.h>

// Define Global Constants
#define AMOUNT_OF_SECTIONS 16
#define AMOUNT_OF_SOUNDS 3
#define UPTIME_INTERVAL 1000

// Define class
class Tile {
  public:
    // Methods
    Tile(String firmware_version, String hardware_version);
    void updateState();
    void updateUptime();
    void deserializeInput(byte* payload, unsigned int length);
    String serializeOutput();
    bool stateChanged();

    // Atributes
    String state;
    
  private:
    // Atributes
    Audio _audio;
    Detect _detect;
    Light _light;

    bool _reboot;
    String _firmware;
    String _hardware;
    String _mode; // Will currently always be "mqtt", but demo mode will be implemented later.
    unsigned long _uptime;
    unsigned long _lastUptime;
    String* _sounds;

    String _previous_state;
    // Methods
};

#endif