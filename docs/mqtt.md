# MQTT Communications

This document describes the way MQTT is used in this project.

> [!NOTE]  
> This document is still in development and is not finished yet.
> This file should be removed and the information should be moved to the wiki when the project is finished.

## MQTT Topics

This project uses the following base topic:

```text
music-light-tiles/
```

Each device has a unique name/id. This name is used as a subtopic.  
For example, the device with the name `tile-1` will use the following topic:

```text
music-light-tiles/tile-1/
```

Each device has 2 main subtopics, `state` and `command`. 

### State

The `state` subtopic is used to publish the current state of the device.
This state is published by the device itself as a JSON object.
The JSON object has the 4 main properties `system`, `audio`, `light` and `detect`.

#### System

The `system` property is used to publish the system state of the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `firmware` | String | The firmware version of the device. |
| `hardware` | String | The hardware version of the device. |
| `ping` | Boolean | Whether the device is pinging or not. |
| `uptime` | Number | The number of seconds the device has been running. |
| `sounds` | Array | The list od possible sounds the device can play. |

#### Audio

The `audio` property is used to publish the audio state of the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `state` | Number | The mode the device is in. 0 = idle, 1 = playing, 2 = paused. |
| `looping` | Boolean | Whether the device is looping the audio or not. |
| `sound` | String | The sound the device is playing. |
| `volume` | Number | The volume of the device. |

#### Light

The `light` property is used to publish the light state of the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness of the full ledstrip. (0-255) |
| `sections` | Array | The list of colors of each section, should have a format of {r: 0, g: 0, b: 0, w:0} for each section. |

#### Detect

The `detect` property is used to publish the detection state of the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `detected` | Boolean | Whether the device has detected presence or not. |

#### Example

Here is an example of how a full state payload should look.

```json
{
  "system": {
    "firmware": "1.0.0",
    "hardware": "1.0.0",
    "ping": false,
    "uptime": 1234,
    "sounds": ["sound-1", "sound-2", "sound-3"]
  },
  "audio": {
    "state": 2,
    "looping": false,
    "sound": "sound-1",
    "volume": 50
  },
  "light": {
    "brightness": 50,
    "sections": [
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255}
    ]
  },
  "detect": {
    "detected": true
  }
}
```	

### Command

The `command` subtopic is used to send commands to the device.
This command should be sent by the MQTT broker to the device as a JSON object.
The JSON object has the 3 main properties `system`, `audio` and `light`.

#### System

The `system` property is used to send system commands to the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `reboot` | Boolean | Whether the device should reboot or not. |
| `ping` | Boolean | Whether the device should send its uptime every change or not. |

#### Audio

The `audio` property is used to send audio commands to the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `mode` | Number | The mode the device should set. 1 = play, 2 = pause, 3 = resume, 4 = stop. |
| `loop` | Boolean | Whether the device should loop the audio or not. |
| `sound` | String | The sound the device should play. |
| `volume` | Number | The volume the device should set. (0 - 100%) |

#### Light

The `light` property is used to send light commands to the device.
This property has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness the device should set. |
| `sections` | Array | The list of colors of each section, should have a format of {r: 0, g: 0, b: 0, w:0} for each section. |

#### Example

Here is an example of how a full command payload should look.

```json
{
  "system": {
    "reboot": false,
    "ping": false
  },
  "audio": {
    "mode": 1,
    "loop": false,
    "sound": "sound-1",
    "volume": 50
  },
  "light": {
    "brightness": 50,
    "sections": [
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255}
    ]
  }
}
```
