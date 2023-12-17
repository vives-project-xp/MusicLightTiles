# MusicLightTiles

![360° view](./img/360.mp4)

## About

Welcome to the MusicLightTiles project!  
This project was created as part of the Project Experience course at [VIVES University of Applied Sciences](https://www.vives.be/en).  
The goal of this project was to create a Proof of Concept interactive floor tile that can play music and light up when someone stands on it.  
The tile should also be able to work with [Project Master](https://github.com/vives-project-xp/ProjectMaster).  

## The team

- [Rob Cocquyt](https://github.com/Robbedoes24)
- [Ruben Belligh](https://github.com/RubenBelligh)
- [Luca De Clerck](https://github.com/LucaClrk)
- [Alberiek Depreytere](https://github.com/AlberiekDepreytere)

## Features

- Small form factor
- Can work standalone or as a set
- Hardcoded and wireless modes
- Add your own music
- Individualy addressable RGB leds
- Tested for 85kg of weight
- Can detect people starting from 5kg
- Works with [Project Master](https://github.com/vives-project-xp/ProjectMaster)

## How it works

Each tile has an ESP32 microcontroller that controls the lights and music and detects when someone stands on the tile.  
The tile reacts differently depending on the mode it is in, more info about this in the [Modes](#modes) section.  

### Person detection

To detect when someone stands on the tile, the ESP32 uses a simple circuit with 2 conductive strips.  
When someone stands on the tile, the conductive strips touch each other and close the circuit.  
To make sure the circuit is normally open, the tile uses seal strip to keep the plate (where people stand on) and the base (where the circuit is) separated.  
This way, the circuit is only closed when someone stands on the tile, because the seal strip is compressed.  
When the person later leaves the tile, the seal strip will decompress and push the plate back up, opening the circuit again.  

![Section View](./img/sectionview.png)

### Audio

For the audio, we use a DFPlayer Mini.
This is a small mp3 player that can be controlled with a serial connection.  
The ESP32 sends commands to the DFPlayer Mini to play, pause, stop, change volume, etc.  
The player has a micro SD card slot where you can put your own music.  
This player also has a built-in amplifier, so you can connect a speaker directly to it (3W speaker recommended).  

### Lights

For the lights, we use a WS2814 LED strip.  
This is a 24v LED strip with individually addressable RGB led sections.  
Each section has 6 leds and is about 10cm long.  

## Modes

The tiles can work in 2 modes:

- Hardcoded mode (Demo mode)
- Wireless mode (MQTT mode)

### Demo mode

In this mode, every tile will work on its own.  
When someone stands on a tile, the lights will turn on and music will start playing.  
When the person leaves the tile, the lights will turn red  and music will stop.  

### MQTT mode

In this mode, the tiles basically function as a sensor and actuator.  
When the state of a tile changes (like when someone stands on it), it will send a message to the MQTT broker.  
When a tile receives a command from the MQTT broker, it will execute the command and change its state accordingly.  

With the help of the server, you can control multiple tiles with the same command.  
This makes it possible to create a set of tiles that work together and can be controlled from a single point.  

## Project state

This project is currently in a working state.  
The tiles can be used in both modes and can be controlled with the [Project Master](https://github.com/vives-project-xp/ProjectMaster).  
There is an api available to control the tiles with websocket messages.
We started on a web interface to control the tiles, but this is not finished yet.

## Documentation

If you want to build your own tile(s) or build further on this project, you can find all aditional information in the [Wiki](https://github.com/vives-project-xp/MusicLightTiles/wiki).    

## Future improvements

- Finish the web interface.
- Replace the led strip with a 5v one, so the leds can be controlled individually.
- Replace the DFPlayer Mini with custom circuitry, so there won't be any delay when playing music.
- Add effects to the control server.
- Make the tiles cheaper to produce (so they can be used in schools, etc.).
