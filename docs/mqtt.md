# MQTT Communications

This document describes the way MQTT is used in this project.

> [!NOTE]  
> This document is still in development and is not finished yet.
> This file should be removed and the information should be moved to the wiki when the project is finished.

## MQTT Topics

This project uses the following base topic:

```text
PM/MLT/
```

Each device has a unique name/id. This name is used as a subtopic.  
The name of the device should be it's mac address without the colons.
For example, the device with the name `96DR72P425G4` will use the following topic:

```text
PM/MLT/96DR72P425G4/
```

Each device has multiple subtopics. These subtopics are `self` and the once required by [Project Master](#project-master).

### Self

The `self` subtopic is used to by this project to communicate with the device.
This subtopic has 2 subtopics, `state`, `command`.

Example topic:
```text
PM/MLT/96DR72P425G4/self/
```

#### Last Will and Testament

Each device has a publish a last will and testament message to the `self` subtopic.
This message is used to notify the system when a device disconnects.

#### State

The `state` subtopic is used to publish the current state of the device.
The state topic has 4 subtopics, `system`, `audio`, `light` and `presence`.

Example topic:
```text
PM/MLT/96DR72P425G4/state/
```

##### System

The `system` subtopic is used to publish the system state of the device.
This subtopic publishes its state as a JSON string and has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `firmware` | String | The firmware version of the device. |
| `hardware` | String | The hardware version of the device. |
| `ping` | Boolean | Whether the device is pinging or not. |
| `uptime` | Number | The number of seconds the device has been running. |
| `sounds` | Array | The list of possible sounds the device can play. |

Example json:
```json
{
  "firmware": "1.0.0",
  "hardware": "1.0.0",
  "ping": false,
  "uptime": 1234,
  "sounds": [
    "A cat meowing",
    "A dog barking",
    "A duck quacking",
    "A frog croaking",
    "A horse neighing",
    "A pig grunt",
    "A rooster crowing",
    "A chicken clucking",
    "A sheep baaing",
    "A wolf howling",
    "Minecraft villager",
    "Minecraft creeper hissing",
    "Minecraft explosion",
    "Mario jump",
    "Mario coin",
    "Mario death",
    "Among Us role reveal",
    "Fortnite death",
    "Roblox oof",
    "CS:GO bomb planted",
    "CS:GO bomb defused",
    "GTA San Andreas - Here we go again",
    "GTA V wasted",
    "GTA V phone ring",
    "Bruh sound effect",
    "Emotional damage",
    "Sad violin",
    "Windows XP error",
    "Windows XP shutdown",
    "Windows XP startup",
    "Piano C note",
    "Piano C# note",
    "Piano D note",
    "Piano D# note",
    "Piano E note",
    "Piano F note",
    "Piano F# note",
    "Piano G note",
    "Piano G# note",
    "Piano A note",
    "Piano A# note",
    "Piano B note",
    "Applause",
    "Kids cheering",
    "Crickets",
    "Wheel spin",
    "Wrong answer",
    "Right answer",
    "Intermission",
    "The Office - That's what she said",
    "The Office - No, God! No, God, please no! No! No! Nooooooo!",
    "Obi-Wan Kenobi - Hello there"
  ]
}
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/state/system/
```

##### Audio

The `audio` subtopic is used to publish the audio state of the device.
This subtopic publishes its state as a JSON string and has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `state` | Number | The mode the device is in. 0 = idle, 1 = playing, 2 = paused. |
| `looping` | Boolean | Whether the device is looping the audio or not. |
| `sound` | String | The sound the device is playing. |
| `volume` | Number | The volume of the device. |

Example json:
```json
{
  "state": 2,
  "looping": false,
  "sound": "Mario coin",
  "volume": 50
}
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/state/audio/
```

##### Light

The `light` subtopic is used to publish the light state of the device.
This subtopic publishes its state as a JSON string and has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness of the full ledstrip. (0-255) |
| `pixels` | Array | The list of colors of each pixel, should have a format of {r: 0, g: 0, b: 0, w:0} for each pixel. |

Example json:
```json
{
  "brightness": 50,
  "pixels": [
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
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/state/light/
```

##### Presence

The `Presence` subtopic is used to publish the detection state of the device.
This subtopic publishes its state as a JSON string and has the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `detected` | Boolean | Whether the device has detected presence or not. |

Example json:
```json
{
  "detected": true
}
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/state/presence/
```

#### Command

The `command` subtopic is used to send commands to the device.
The command topic has 3 subtopics, `system`, `audio` and `light`.

Example topic:
```text
PM/MLT/96DR72P425G4/self/command/
```

##### System

The `system` subtopic is used to send system commands to the device.
This subtopic expects a JSON string with the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `reboot` | Boolean | Whether the device should reboot or not. |
| `ping` | Boolean | Whether the device should send its uptime every change or not. |

Example json:
```json
{
  "reboot": false,
  "ping": false
}
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/command/system/
```

##### Audio

The `audio` subtopic is used to send audio commands to the device.
This subtopic expects a JSON string with the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `mode` | Number | The mode the device should set. 1 = play, 2 = pause, 3 = resume, 4 = stop. |
| `loop` | Boolean | Whether the device should loop the audio or not. |
| `sound` | String | The sound the device should play. |
| `volume` | Number | The volume the device should set. (0 - 100%) |

Example json:
```json
{
  "mode": 1,
  "loop": false,
  "sound": "Mario coin",
  "volume": 50
}
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/command/audio/
```

##### Light

The `light` subtopic is used to send light commands to the device.
This subtopic expects a JSON string with the following subproperties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness the device should set. |
| `pixels` | Array | The list of colors of each pixel, should have a format of {r: 0, g: 0, b: 0, w:0} for each pixel. |

Example json:
```json
{
  "brightness": 50,
  "pixels": [
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
```

Example topic:
```text
PM/MLT/96DR72P425G4/self/command/light/
```

#### Project Master

This project is managed by [Project Master](https://github.com/vives-project-xp/ProjectMaster)

Project Master only sends commands to the devices, it does not receive any data from the devices.

Project Master uses the following topics:

```text
PM/MLT/96DR72P425G4/command/
PM/MLT/96DR72P425G4/rgb/
PM/MLT/96DR72P425G4/effect/
```

See the [Project Master](https://github.com/vives-project-xp/ProjectMaster) documentation for more information.
