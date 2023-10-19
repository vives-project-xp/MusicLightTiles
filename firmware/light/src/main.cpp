#include <Arduino.h>

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#define PIN        25
#define NUMPIXELS 16

const int arrayPixel[16][4] = {{0,255,255,0},{0,255,0,255},{255,255,255,0},{0,255,255,255},{255,255,255,0},{255,255,0,255},{255,255,255,0},{255,255,255,255},
{0,255,255,0},{0,255,255,0},{0,255,0,255},{255,255,255,0},{255,255,255,255},{255,255,255,0},{0,255,255,0},{255,255,0,255}};

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRBW + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.show();
}

void loop() {
 for (int i = 0; i < NUMPIXELS; i++) {
    uint8_t red = arrayPixel[i][0];
    uint8_t white = arrayPixel[i][1];
    uint8_t green = arrayPixel[i][2];
    uint8_t blue = arrayPixel[i][3];
    pixels.setPixelColor(i, pixels.Color(red, white,green, blue));
    pixels.setBrightness(50);
  }

  pixels.show(); // Show the updated colors on the NeoPixels


}